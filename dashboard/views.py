from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from records.models import FinancialRecord
from records.serializers import RecordReadSerializer
from users.permissions import IsAdminOrAnalyst


def get_active_records():
    """Always excludes soft deleted records."""
    return FinancialRecord.objects.filter(is_deleted=False)


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/
    Returns total income, total expenses, net balance, and total record count.
    Access: Admin + Analyst only.
    """
    permission_classes = [IsAdminOrAnalyst]

    def get(self, request):
        queryset = get_active_records()

        totals = queryset.aggregate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expenses=Sum('amount', filter=Q(type='expense')),
        )

        total_income = totals['total_income'] or 0
        total_expenses = totals['total_expenses'] or 0
        net_balance = total_income - total_expenses
        total_records = queryset.count()

        return Response({
            "success": True,
            "data": {
                "total_income": f"{total_income:.2f}",
                "total_expenses": f"{total_expenses:.2f}",
                "net_balance": f"{net_balance:.2f}",
                "total_records": total_records,
            }
        }, status=200)


class DashboardByCategoryView(APIView):
    """
    GET /api/dashboard/by-category/
    Returns total amount and count grouped by category.
    Optional filter: ?type=income or ?type=expense
    Access: Admin + Analyst only.
    """
    permission_classes = [IsAdminOrAnalyst]

    def get(self, request):
        queryset = get_active_records()

        # ✅ Optional filter by type
        record_type = request.query_params.get('type', None)
        if record_type in ['income', 'expense']:
            queryset = queryset.filter(type=record_type)

        breakdown = (
            queryset
            .values('category', 'type')
            .annotate(
                total=Sum('amount'),
                count=Count('id')
            )
            .order_by('-total')
        )

        data = [
            {
                "category": item['category'],
                "type": item['type'],
                "total": f"{item['total']:.2f}",
                "count": item['count'],
            }
            for item in breakdown
        ]

        return Response({
            "success": True,
            "data": data
        }, status=200)


class DashboardTrendsView(APIView):
    """
    GET /api/dashboard/trends/
    Returns monthly income vs expenses for the current year.
    Access: Admin + Analyst only.
    """
    permission_classes = [IsAdminOrAnalyst]

    def get(self, request):
        current_year = timezone.now().year
        queryset = get_active_records().filter(date__year=current_year)

        # ✅ Aggregate income and expenses separately by month
        monthly_income = (
            queryset
            .filter(type='income')
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(income=Sum('amount'))
            .order_by('month')
        )

        monthly_expenses = (
            queryset
            .filter(type='expense')
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(expenses=Sum('amount'))
            .order_by('month')
        )

        # ✅ Merge both into a single dict keyed by month string
        trends = {}

        for item in monthly_income:
            key = item['month'].strftime('%Y-%m')
            trends[key] = {
                "month": key,
                "income": f"{item['income']:.2f}",
                "expenses": "0.00"
            }

        for item in monthly_expenses:
            key = item['month'].strftime('%Y-%m')
            if key in trends:
                trends[key]['expenses'] = f"{item['expenses']:.2f}"
            else:
                trends[key] = {
                    "month": key,
                    "income": "0.00",
                    "expenses": f"{item['expenses']:.2f}"
                }

        sorted_trends = sorted(trends.values(), key=lambda x: x['month'])

        return Response({
            "success": True,
            "data": sorted_trends
        }, status=200)


class DashboardRecentView(APIView):
    """
    GET /api/dashboard/recent/
    Returns the 10 most recent financial records.
    Access: Admin + Analyst only.
    """
    permission_classes = [IsAdminOrAnalyst]

    def get(self, request):
        recent = get_active_records().order_by('-date', '-created_at')[:10]

        return Response({
            "success": True,
            "data": RecordReadSerializer(recent, many=True).data
        }, status=200)