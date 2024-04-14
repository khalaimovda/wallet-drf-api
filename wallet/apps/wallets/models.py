import uuid
from decimal import Decimal

from django.db import models


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=250, null=False)
    balance = models.DecimalField(max_digits=30, decimal_places=18, default=Decimal('0.0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'
