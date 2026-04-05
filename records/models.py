from django.db import models
from django.conf import settings

RECORD_TYPES = [
    ('income', 'Income'),
    ('expense', 'Expense'),
]


class FinancialRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='records'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # ✅ DecimalField not FloatField
    type = models.CharField(max_length=10, choices=RECORD_TYPES)
    category = models.CharField(max_length=100)
    date = models.DateField()
    notes = models.TextField(blank=True, default='')

    # ✅ Soft delete — never permanently remove financial records
    is_deleted = models.BooleanField(default=False)

    # ✅ Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type.upper()} | {self.category} | {self.amount} | {self.date}"