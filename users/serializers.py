from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ROLES


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        # ✅ role is intentionally excluded — always defaults to viewer

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # ✅ properly hashes password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # ✅ authenticate() handles password hash comparison correctly
        user = authenticate(username=username, password=password)

        if user is None:
            # Could be wrong password OR username doesn't exist
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("Your account has been deactivated.")

        # ✅ Return the full user object, not just data dict
        return user


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # ✅ password is NEVER in this list
        fields = ['id', 'username', 'email', 'role', 'is_active', 'created_at']
        read_only_fields = fields


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ROLES, required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['role', 'is_active']

    def validate_role(self, value):
        if value not in [r[0] for r in ROLES]:
            raise serializers.ValidationError(f"Role must be one of: viewer, analyst, admin.")
        return value