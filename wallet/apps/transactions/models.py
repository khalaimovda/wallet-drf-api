import uuid
from decimal import Decimal

from django.db import models
from wallets.models import Wallet


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE, related_name='transactions')
    txid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=30, decimal_places=18, default=Decimal('0.0'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
