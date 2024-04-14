from django_filters import rest_framework as filters
from transactions.models import Transaction


class TransactionFilter(filters.FilterSet):
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['min_amount', 'max_amount']
