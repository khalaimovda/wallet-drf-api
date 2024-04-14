import random
from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.models import Transaction
from wallets.models import Wallet

from .utils import assert_transaction_dict_and_transaction_model


class TransactionTestCase(APITestCase):
    def setUp(self):
        self.page_size: int = settings.REST_FRAMEWORK['PAGE_SIZE']
        self.wallet = Wallet.objects.create(label='Main Wallet', balance=0)
        self.transactions: list[Transaction] = [
            Transaction.objects.create(wallet=self.wallet, amount=i)
            for i in range(self.page_size * 2 + 1)
        ][::-1]
        self.wallet.balance = sum(t.amount for t in self.transactions)
        self.wallet.save()

    def test_get_transactions_list_with_pagination(self):
        """
        Test GET all transactions with pagination
        """
        base_url = reverse('transaction-list')
        # Page 1
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions: list[dict] = response.data.get('results')
        self.assertEqual(len(transactions), self.page_size)
        for i in range(self.page_size):
            assert_transaction_dict_and_transaction_model(self, transactions[i], self.transactions[i])

        # Page 2
        query_params = {'page': 2}
        url_encoded_params = urlencode(query_params)
        url = f'{base_url}?{url_encoded_params}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions: list[dict] = response.data.get('results')
        self.assertEqual(len(transactions), self.page_size)
        for i in range(self.page_size, 2 * self.page_size):
            assert_transaction_dict_and_transaction_model(self, transactions[i - self.page_size], self.transactions[i])

        # Page 3
        query_params = {'page': 3}
        url_encoded_params = urlencode(query_params)
        url = f'{base_url}?{url_encoded_params}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions: list[dict] = response.data.get('results')
        self.assertEqual(len(transactions), 1)
        assert_transaction_dict_and_transaction_model(self, transactions[0], self.transactions[-1])

    def test_get_transaction_list_with_filters(self):
        """
        Test GET all wallets with filters (max_amount and min_amount)
        """
        base_url = reverse('transaction-list')
        max_amount = 2 * self.page_size - 1.5
        min_amount = self.page_size
        query_params = {'min_amount': min_amount, 'max_amount': max_amount}
        url_encoded_params = urlencode(query_params)
        url = f'{base_url}?{url_encoded_params}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions: list[dict] = response.data.get('results')
        self.assertEqual(len(transactions), self.page_size - 1)
        correct_transactions = [t for t in self.transactions if min_amount <= t.amount <= max_amount]
        for i in range(self.page_size - 1):
            assert_transaction_dict_and_transaction_model(self, transactions[i], correct_transactions[i])

    def test_get_transaction_by_txid(self):
        """
        Test GET transaction by its txid
        """
        random_transaction: Transaction = random.choice(self.transactions)
        # By txid we must see a result
        url = reverse('transaction-detail', kwargs={'pk': random_transaction.txid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction: dict = response.data
        assert_transaction_dict_and_transaction_model(self, transaction, random_transaction)

        # By id(not txid) we must not see a result
        url = reverse('transaction-detail', kwargs={'pk': random_transaction.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wallet(self):
        """
        Test POST new transaction. Check recalculation of wallet balance
        """
        wallet = Wallet.objects.create(label='One more Wallet', balance=0.0)

        url = reverse('transaction-list')

        data = {'wallet': str(wallet.id), 'amount': '13.3',}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction_positive: dict = response.data
        database_transaction_positive: Transaction = Transaction.objects.get(pk=transaction_positive['id'])
        assert_transaction_dict_and_transaction_model(self, transaction_positive, database_transaction_positive)
        wallet.refresh_from_db()
        self.assertEqual(float(wallet.balance), 13.3)

        data = {'wallet': str(wallet.id), 'amount': '-7.5'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction_negative: dict = response.data
        database_transaction_negative: Transaction = Transaction.objects.get(pk=transaction_negative['id'])
        assert_transaction_dict_and_transaction_model(self, transaction_negative, database_transaction_negative)
        wallet.refresh_from_db()
        self.assertEqual(float(wallet.balance), 5.8)

        database_transaction_negative.delete()
        database_transaction_positive.delete()
        wallet.delete()
