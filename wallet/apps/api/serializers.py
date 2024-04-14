from django.db import transaction as db_transaction
from rest_framework import serializers
from transactions.models import Transaction
from wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    label = serializers.CharField(max_length=250, required=True)
    balance = serializers.DecimalField(max_digits=30, decimal_places=18, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'label', 'balance', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    txid = serializers.UUIDField(read_only=True)
    amount = serializers.DecimalField(max_digits=30, decimal_places=18, default='0.0')
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())

    class Meta:
        model = Transaction
        fields = ['id', 'txid', 'amount', 'wallet']

    def create(self, validated_data):
        with db_transaction.atomic():
            amount = validated_data.get('amount')
            wallet = validated_data.get('wallet')
            transaction = Transaction.objects.create(wallet=wallet, amount=amount)
            wallet.balance += amount
            wallet.save(update_fields=['balance', ])
            return transaction
