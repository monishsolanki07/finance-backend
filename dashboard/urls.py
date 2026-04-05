from django.urls import path
from .views import (
    DashboardSummaryView,
    DashboardByCategoryView,
    DashboardTrendsView,
    DashboardRecentView,
)

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('by-category/', DashboardByCategoryView.as_view(), name='dashboard-by-category'),
    path('trends/', DashboardTrendsView.as_view(), name='dashboard-trends'),
    path('recent/', DashboardRecentView.as_view(), name='dashboard-recent'),
]