import django_filters
from .models import FinancialRecord


class FinancialRecordFilter(django_filters.FilterSet):
    # Filter by type: ?type=income or ?type=expense
    type = django_filters.ChoiceFilter(
        choices=[('income', 'Income'), ('expense', 'Expense')]
    )

    # Filter by category: ?category=groceries (case insensitive)
    category = django_filters.CharFilter(
        field_name='category',
        lookup_expr='icontains'
    )

    # Filter by date range: ?date_from=2026-01-01&date_to=2026-03-31
    date_from = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte'
    )
    date_to = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte'
    )

    # Filter by amount range: ?min_amount=1000&max_amount=50000
    min_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte'
    )
    max_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte'
    )

    class Meta:
        model = FinancialRecord
        fields = ['type', 'category', 'date_from', 'date_to', 'min_amount', 'max_amount']