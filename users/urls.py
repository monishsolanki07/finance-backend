from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    MeView,
    UserListView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('me/', MeView.as_view(), name='user-me'),
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
]