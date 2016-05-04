import datetime
import json
import unittest

import requests

URL = ("http://", "127.0.0.1", ":", "8000", "/")

HEADERS = {'Content-Type': 'application/json'}


class FilledUserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        requests.get(''.join(URL + ('debug/clear/',)))
        params = {'name': 'gert', 'mailAddress': 'gertMail'}
        r = requests.post(''.join(URL + ('user', '/')), headers=HEADERS, data=json.dumps(params))
        result = r.json()
        user_1 = result['id']
        params = {'name': 'bar', 'mailAddress': 'barMail'}
        r = requests.post(''.join(URL + ('user', '/')), headers=HEADERS, data=json.dumps(params))
        result = r.json()
        user_2 = result['id']
        cls.names = ['gert', 'bar']
        cls.ids = [user_1, user_2]

    def test_list_2_users(self):
        r = requests.get(''.join(URL + ('user',)), headers=HEADERS)
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        users = json.loads(r.text)
        self.assertEqual(2, users.get('overall_count'))
        self.assertEqual(100, users.get('limit'))
        self.assertEqual(0, users.get('offset'))
        entries = users['entries']
        self.assertIsInstance(entries, list)
        self.assertEqual(2, len(entries))
        for i in range(0, 1):
            with self.subTest(i=i):
                self.assertEqual(self.names[i], entries[i].get('name'))
                self.assertEqual(self.ids[i], entries[i]['id'])
                self.assertEqual(0, entries[i].get('balance'))
                self.assertIsNone(entries[i].get('last_transaction'))

    def test_list_users_empty_offset(self):
        r = requests.get(''.join(URL + ('user',)), headers=HEADERS, params={'offset': 2, 'limit': 1})
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        users = json.loads(r.text)
        self.assertEqual(2, users.get('overall_count'))
        self.assertEqual(1, users.get('limit'))
        self.assertEqual(2, users.get('offset'))
        entries = users['entries']
        self.assertIsInstance(entries, list)
        self.assertEqual(0, len(entries))

    def test_load_user_by_id(self):
        for i, name in enumerate(self.names):
            r = requests.get(''.join(URL + ('user', '/', str(self.ids[i]))), headers=HEADERS)
            self.assertEqual(200, r.status_code)
            self.assertEqual('application/json', r.headers['Content-Type'])
            user = json.loads(r.text)
            self.assertEqual(name, user.get('name'))
            self.assertEqual(self.ids[i], user.get('id'))
            self.assertEqual(0, user.get('balance'))
            self.assertIsNone(user.get('last_transaction'))


class FilledTransactionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        requests.get(''.join(URL + ('debug/clear/',)))
        params = {'name': 'gert', 'mailAddress': 'gertMail'}
        r = requests.post(''.join(URL + ('user', '/')), headers=HEADERS, data=json.dumps(params))
        result = r.json()
        user_1 = result['id']
        params = {'name': 'bar', 'mailAddress': 'barMail'}
        r = requests.post(''.join(URL + ('user', '/')), headers=HEADERS, data=json.dumps(params))
        result = r.json()
        user_2 = result['id']
        cls.names = ['gert', 'bar']
        cls.ids = [user_1, user_2]
        cls.transactions = {user_1: [1000, -500, -150],
                            user_2: [2000, -250, -50]}
        for user_id, value_list in cls.transactions.items():
            for value in value_list:
                FilledTransactionsTests.add_transaction_to_user(user_id, value=value)

    @staticmethod
    def add_transaction_to_user(user_id, value):
        params = {'value': value}
        r = requests.post(''.join((URL + ('user', '/', str(user_id), '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        assert 201 == r.status_code

    def test_load_user_by_id(self):
        for i, name in enumerate(self.names):
            user_id = self.ids[i]
            r = requests.get(''.join(URL + ('user', '/', str(user_id))), headers=HEADERS)
            self.assertEqual(200, r.status_code)
            self.assertEqual('application/json', r.headers['Content-Type'])
            user = json.loads(r.text)
            self.assertEqual(name, user.get('name'))
            self.assertEqual(self.ids[i], user.get('id'))
            balance = sum(self.transactions.get(user_id, []))
            self.assertEqual(balance, user.get('balance'))
            self.assertIsNotNone(user.get('last_transaction'))
            now = datetime.datetime.utcnow()
            last_transaction = datetime.datetime.strptime(user['last_transaction'], '%Y-%m-%dT%H:%M:%S.%fZ')
            self.assertGreater(20, (now - last_transaction).total_seconds())

    def test_load_user_transactions(self):
        for i, name in enumerate(self.names):
            user_id = self.ids[i]
            r = requests.get(''.join(URL + ('user', '/', str(user_id), '/', 'transaction',)), headers=HEADERS)
            self.assertEqual(200, r.status_code)
            self.assertEqual('application/json', r.headers['Content-Type'])
            transactions = json.loads(r.text)
            self.assertEqual(len(self.transactions.get(user_id)), transactions.get('overall_count'))
            self.assertEqual(100, transactions.get('limit'))
            self.assertEqual(0, transactions.get('offset'))
            self.assertIsInstance(transactions['entries'], list)
            entries = transactions['entries']
            self.assertEqual(len(self.transactions.get(user_id)), len(entries))
            for j, entry in enumerate(entries):
                self.assertEqual(self.transactions.get(user_id)[j], entry['value'])
                self.assertEqual(user_id, entry['user'])

    def test_load_user_transactions_offset(self):
        for i, name in enumerate(self.names):
            user_id = self.ids[i]
            r = requests.get(''.join(URL + ('user', '/', str(user_id), '/', 'transaction',)), headers=HEADERS,
                             params={'limit': 1, 'offset': 2})
            self.assertEqual(200, r.status_code)
            self.assertEqual('application/json', r.headers['Content-Type'])
            transactions = json.loads(r.text)
            self.assertEqual(len(self.transactions.get(user_id)), transactions.get('overall_count'))
            self.assertEqual(1, transactions.get('limit'))
            self.assertEqual(2, transactions.get('offset'))
            self.assertIsInstance(transactions['entries'], list)
            entries = transactions['entries']
            self.assertEqual(1, len(entries))
            for j, entry in enumerate(entries):
                self.assertEqual(self.transactions.get(user_id)[j + 2], entry['value'])
                self.assertEqual(user_id, entry['user'])

    def test_load_user_single_transaction(self):
        for user_id in self.transactions.keys():
            r = requests.get(''.join(URL + ('user', '/', str(user_id), '/', 'transaction',)), headers=HEADERS)
            self.assertEqual(200, r.status_code)
            transactions = json.loads(r.text)
            entries = transactions['entries']
            for j, entry in enumerate(entries):
                with self.subTest(transaction_id=entry['id']):
                    self.assertEqual(self.transactions.get(user_id)[j], entry['value'])
                    self.assertEqual(user_id, entry['user'])
                    self.assert_user_transaction(entry['id'], entry['value'], user_id)

    def assert_user_transaction(self, transaction_id, value, user_id):
        r = requests.get(
            ''.join(URL + ('user', '/', str(user_id), '/', 'transaction', '/', str(transaction_id))),
            headers=HEADERS)
        self.assertEqual(200, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])
        transaction = r.json()
        self.assertEqual(transaction_id, transaction['id'])
        self.assertEqual(user_id, transaction['user'])
        self.assertEqual(value, transaction['value'])
        now = datetime.datetime.utcnow()
        last_transaction = datetime.datetime.strptime(transaction['create_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertGreater(20, (now - last_transaction).total_seconds())
