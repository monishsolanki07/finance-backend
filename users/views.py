from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .serializers import RegisterSerializer, LoginSerializer

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserReadSerializer,
    UserRoleUpdateSerializer,
)
from .permissions import IsAdmin, IsActiveUser


def get_tokens_for_user(user):
    """Generate JWT access and refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    """
    POST /api/users/register/
    Public. Registers a new user. Role defaults to viewer.
    """
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Account created successfully.",
                "data": UserReadSerializer(user).data
            }, status=201)
        return Response({
            "success": False,
            "error": serializer.errors,
            "code": 400
        }, status=400)


class LoginView(APIView):
    """
    POST /api/users/login/
    Public. Returns JWT tokens on valid credentials.
    """
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # ✅ validated_data is the full user object returned from LoginSerializer.validate()
            user = serializer.validated_data
            tokens = get_tokens_for_user(user)
            return Response({
                "success": True,
                "message": "Login successful.",
                "data": {
                    "tokens": tokens,
                    "user": UserReadSerializer(user).data
                }
            }, status=200)

        return Response({
            "success": False,
            "error": serializer.errors,
            "code": 400
        }, status=400)


class MeView(APIView):
    """
    GET /api/users/me/
    Any authenticated active user can view their own profile.
    """
    permission_classes = [IsActiveUser]

    def get(self, request):
        return Response({
            "success": True,
            "data": UserReadSerializer(request.user).data
        }, status=200)


class UserListView(APIView):
    """
    GET /api/users/
    Admin only. Lists all users in the system.
    """
    permission_classes = [IsAdmin]
    @swagger_auto_schema(request_body=UserReadSerializer)

    def get(self, request):
        users = User.objects.all().order_by('-created_at')
        return Response({
            "success": True,
            "data": UserReadSerializer(users, many=True).data
        }, status=200)


class UserDetailView(APIView):
    """
    GET /api/users/<pk>/
    Admin only. Get a single user by ID.
    """
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "User not found.",
                "code": 404
            }, status=404)

        return Response({
            "success": True,
            "data": UserReadSerializer(user).data
        }, status=200)


class UserUpdateView(APIView):
    """
    PATCH /api/users/<pk>/update/
    Admin only. Update a user's role or active status.
    """
    permission_classes = [IsAdmin]
    @swagger_auto_schema(request_body=UserRoleUpdateSerializer)
    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "User not found.",
                "code": 404
            }, status=404)

        # ✅ prevent admin from deactivating themselves
        if user == request.user and request.data.get('is_active') is False:
            return Response({
                "success": False,
                "error": "You cannot deactivate your own account.",
                "code": 400
            }, status=400)

        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "User updated successfully.",
                "data": UserReadSerializer(user).data
            }, status=200)

        return Response({
            "success": False,
            "error": serializer.errors,
            "code": 400
        }, status=400)


class UserDeleteView(APIView):
    """
    DELETE /api/users/<pk>/delete/
    Admin only. Soft deactivates a user (does not remove from DB).
    """
    permission_classes = [IsAdmin]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "User not found.",
                "code": 404
            }, status=404)

        # ✅ prevent admin from deactivating themselves
        if user == request.user:
            return Response({
                "success": False,
                "error": "You cannot deactivate your own account.",
                "code": 400
            }, status=400)

        user.is_active = False
        user.save()

        return Response({
            "success": True,
            "message": f"User '{user.username}' has been deactivated."
        }, status=200)