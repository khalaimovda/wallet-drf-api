import random
import uuid
from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.models import Transaction
from wallets.models import Wallet

from .utils import assert_wallet_dict_and_wallet_model, assert_transaction_dict_and_transaction_model


class WalletTestCase(APITestCase):
    def setUp(self):
        self.page_size: int = settings.REST_FRAMEWORK['PAGE_SIZE']
        self.wallets: list[Wallet] = [
            Wallet.objects.create(label=f'Label {i}', balance=i) for i in range(self.page_size * 2 + 1)
        ][::-1]

        self.wallet_with_transactions, self.wallet_without_transactions = random.sample(self.wallets, 2)
        self.transactions: list[Transaction] = [
            Transaction.objects.create(wallet=self.wallet_with_transactions, amount=random.uniform(-100, 100))
            for _ in range(7)
        ][::-1]

    def test_get_wallet_list_with_pagination(self):
        """
        Test GET all wallets with pagination
        """
        base_url = reverse('wallet-list')
        # Page 1
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallets: list[dict] = response.data.get('results')
        self.assertEqual(len(wallets), self.page_size)
        for i in range(self.page_size):
            assert_wallet_dict_and_wallet_model(self, wallets[i], self.wallets[i])

        # Page 2
        query_params = {'page': 2}
        url_encoded_params = urlencode(query_params)
        url = f'{base_url}?{url_encoded_params}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallets: list[dict] = response.data.get('results')
        self.assertEqual(len(wallets), self.page_size)
        for i in range(self.page_size, 2 * self.page_size):
            assert_wallet_dict_and_wallet_model(self, wallets[i - self.page_size], self.wallets[i])

        # Page 3
        query_params = {'page': 3}
        url_encoded_params = urlencode(query_params)
        url = f'{base_url}?{url_encoded_params}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallets: list[dict] = response.data.get('results')
        self.assertEqual(len(wallets), 1)
        assert_wallet_dict_and_wallet_model(self, wallets[0], self.wallets[-1])

    def test_get_wallet_list_with_filters(self):
        """
        Test GET all wallets with filters by label
        """
        base_url = reverse('wallet-list')
        random_wallet: Wallet = random.choice(self.wallets)
        query_params = {'label': random_wallet.label}
        url_encoded_params = urlencode(query_params)
        url = f'{base_url}?{url_encoded_params}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallets: list[dict] = response.data.get('results')
        self.assertEqual(len(wallets), 1)
        assert_wallet_dict_and_wallet_model(self, wallets[0], random_wallet)

    def test_get_wallet_by_id(self):
        """
        Test GET wallet by its id
        """
        # Correct id
        random_wallet: Wallet = random.choice(self.wallets)
        url = reverse('wallet-detail', kwargs={'pk': random_wallet.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallet: dict = response.data
        assert_wallet_dict_and_wallet_model(self, wallet, random_wallet)

        # Incorrect id
        incorrect_id = uuid.uuid4()
        url = reverse('wallet-detail', kwargs={'pk': incorrect_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wallet_transactions(self):
        """
        Test GET all wallet transactions
        """
        # Wallet with transactions
        url = reverse('wallet-transactions', kwargs={'pk': self.wallet_with_transactions.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions: list[dict] = response.data.get('results')
        correct_response_length = min(len(self.transactions), self.page_size)
        self.assertEqual(len(transactions), correct_response_length)
        for i in range(correct_response_length):
            assert_transaction_dict_and_transaction_model(self, transactions[i], self.transactions[i])

        # Wallet without transaction
        url = reverse('wallet-transactions', kwargs={'pk': self.wallet_without_transactions.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions: list[dict] = response.data.get('results')
        self.assertEqual(len(transactions), 0)

        # Incorrect wallet id
        incorrect_id = uuid.uuid4()
        url = reverse('wallet-transactions', kwargs={'pk': incorrect_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wallet(self):
        """
        Test POST new wallet with empty balance
        """
        url = reverse('wallet-list')
        data = {'label': 'Test Create Label'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wallet: dict = response.data
        self.assertEqual(float(wallet['balance']), 0.0)
        database_wallet: Wallet = Wallet.objects.get(label=data['label'])
        assert_wallet_dict_and_wallet_model(self, wallet, database_wallet)
        database_wallet.delete()

    def test_update_wallet(self):
        """
        Test PUT and PATCH for update wallet label
        """
        # PUT
        wallet_for_update = Wallet.objects.create(label='Label For Update', balance=11.1)
        url = reverse('wallet-detail', kwargs={'pk': wallet_for_update.id})
        data = {'label': 'PUT Label'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallet: dict = response.data
        self.assertEqual(wallet['label'], data['label'])
        wallet_for_update.refresh_from_db()
        self.assertEqual(wallet_for_update.label, data['label'])
        assert_wallet_dict_and_wallet_model(self, wallet, wallet_for_update)

        # PATCH
        data = {'label': 'PATCH Label'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallet: dict = response.data
        self.assertEqual(wallet['label'], data['label'])
        wallet_for_update.refresh_from_db()
        self.assertEqual(wallet_for_update.label, data['label'])
        assert_wallet_dict_and_wallet_model(self, wallet, wallet_for_update)

        wallet_for_update.delete()

    def test_delete_wallet(self):
        """
        Test DELETE Wallet. All its transactions must be deleted too
        :return:
        """
        wallet_for_delete = Wallet.objects.create(label='Wallet For Delete', balance=101.0)
        transactions: list[Transaction] = [
            Transaction.objects.create(wallet=wallet_for_delete, amount=random.uniform(-100, 100))
            for _ in range(7)
        ]

        url = reverse('wallet-detail', kwargs={'pk': wallet_for_delete.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Wallet.objects.filter(pk=wallet_for_delete.id).exists())
        self.assertTrue(all(not Transaction.objects.filter(pk=t.id).exists() for t in transactions))
