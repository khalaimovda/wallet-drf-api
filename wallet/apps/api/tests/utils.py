import uuid

from rest_framework.test import APITestCase
from transactions.models import Transaction
from wallets.models import Wallet


def assert_wallet_dict_and_wallet_model(api_test_case: APITestCase, wallet_dict: dict, wallet_object: Wallet):
    api_test_case.assertEqual(uuid.UUID(wallet_dict.get('id')), wallet_object.id)
    api_test_case.assertEqual(wallet_dict.get('label'), wallet_object.label)
    api_test_case.assertEqual(round(float(wallet_dict.get('balance')), 5), round(float(wallet_object.balance), 5))


def assert_transaction_dict_and_transaction_model(api_test_case: APITestCase, transaction_dict: dict, transaction_object: Transaction):
    api_test_case.assertEqual(uuid.UUID(transaction_dict.get('id')), transaction_object.id)
    api_test_case.assertEqual(uuid.UUID(transaction_dict.get('txid')), transaction_object.txid)
    api_test_case.assertEqual(transaction_dict.get('wallet'), transaction_object.wallet.id)
    api_test_case.assertEqual(round(float(transaction_dict.get('amount')), 5), round(float(transaction_object.amount), 5))
