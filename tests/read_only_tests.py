import json
import requests
import unittest

URL = ("http://", "127.0.0.1", ":", "8000", "/")

HEADERS = {'Content-Type': 'application/json'}


class EmptyTests(unittest.TestCase):
    def setUp(self):
        requests.get(''.join(URL + ('debug/clear/',)))

    def test_empty_user_list(self):
        r = requests.get(''.join(URL + ('user',)))
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        users = json.loads(r.text)
        assert {'overall_count', 'limit', 'offset', 'entries'}.issubset(users)
        assert users['overall_count'] == 0
        assert users['limit'] == 100
        assert users['offset'] == 0
        assert users['entries'] == []

    def test_user_not_found(self):
        r = requests.get(''.join(URL + ('user', '/', '10')))
        self.assertEqual(404, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertEqual("user 10 not found", result.get('msg'))

    def test_user_not_found_transactions(self):
        r = requests.get(''.join(URL + ('user', '/', '10', '/', 'transaction')))
        self.assertEqual(404, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertEqual("user 10 not found", result.get('msg'))

    def test_empty_transactions(self):
        r = requests.get(''.join((URL + ('transaction',))))
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        transactions = json.loads(r.text)
        self.assertEqual(0, transactions.get('overall_count'))
        self.assertEqual(100, transactions.get('limit'))
        self.assertEqual(0, transactions.get('offset'))
        self.assertEqual([], transactions.get('entries'))

    def test_user_limits(self):
        r = requests.get(''.join(URL + ('user',)),
                         headers=HEADERS,
                         params={'offset': 1, 'limit': 1})
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        transactions = json.loads(r.text)
        self.assertEqual(0, transactions.get('overall_count'))
        self.assertEqual(1, transactions.get('limit'))
        self.assertEqual(1, transactions.get('offset'))
        self.assertEqual([], transactions.get('entries'))

    def test_user_limits_max(self):
        r = requests.get(''.join(URL + ('user',)),
                         headers=HEADERS,
                         params={'offset': 0, 'limit': 1000})
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        transactions = json.loads(r.text)
        self.assertEqual(0, transactions.get('overall_count'))
        self.assertEqual(250, transactions.get('limit'))  # 250 is the max
        self.assertEqual(0, transactions.get('offset'))
        self.assertEqual([], transactions.get('entries'))

    def test_transaction_limits(self):
        r = requests.get(''.join(URL + ('transaction',)),
                         headers=HEADERS,
                         params={'offset': 1, 'limit': 1})
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        transactions = json.loads(r.text)
        self.assertEqual(0, transactions.get('overall_count'))
        self.assertEqual(1, transactions.get('limit'))
        self.assertEqual(1, transactions.get('offset'))
        self.assertEqual([], transactions.get('entries'))

    def test_transaction_limits_max(self):
        r = requests.get(''.join(URL + ('transaction',)),
                         headers=HEADERS,
                         params={'offset': 0, 'limit': 1000})
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        transactions = json.loads(r.text)
        self.assertEqual(0, transactions.get('overall_count'))
        self.assertEqual(250, transactions.get('limit'))  # 250 is the max
        self.assertEqual(0, transactions.get('offset'))
        self.assertEqual([], transactions.get('entries'))
