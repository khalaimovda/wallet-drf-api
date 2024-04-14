import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from transactions.models import Transaction
from wallets.models import Wallet

from .filters import TransactionFilter
from .serializers import WalletSerializer, TransactionSerializer

logger = logging.getLogger('wallet')


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['label']
    ordering_fields = ['label', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Additional method of receiving all wallet transactions
        """
        wallet = self.get_object()
        transactions = wallet.transactions.all().order_by('-created_at')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(transactions, request, view=self)

        if page is None:
            logger.warning(f'Incorrect None result for transactions of wallet with id = {pk}')
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data)

        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


class TransactionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_object(self):
        """
        Retrieve Transaction by field "txid" instead of "id"
        """
        txid = self.kwargs.get('pk')
        try:
            return Transaction.objects.get(txid=txid)
        except Transaction.DoesNotExist:
            raise NotFound('A transaction with this txid does not exist')
