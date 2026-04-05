from rest_framework import serializers
from django.utils import timezone
from .models import FinancialRecord, RECORD_TYPES


class RecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = ['amount', 'type', 'category', 'date', 'notes']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive non-zero value.")
        return value

    def validate_type(self, value):
        valid_types = [t[0] for t in RECORD_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError("Type must be either 'income' or 'expense'.")
        return value

    def validate_category(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Category cannot be blank.")
        return value.strip().lower()  # normalize category to lowercase

    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value

    def create(self, validated_data):
        # ✅ user is injected from the view, not from request body
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class RecordReadSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FinancialRecord
        # ✅ is_deleted is intentionally excluded from output
        fields = [
            'id', 'user', 'amount', 'type',
            'category', 'date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class RecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = ['amount', 'type', 'category', 'date', 'notes']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive non-zero value.")
        return value

    def validate_type(self, value):
        valid_types = [t[0] for t in RECORD_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError("Type must be either 'income' or 'expense'.")
        return value

    def validate_category(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Category cannot be blank.")
        return value.strip().lower()

    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value