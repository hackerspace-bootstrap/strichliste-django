import json
import unittest

import requests

URL = ("http://", "127.0.0.1", ":", "8000", "/")

HEADERS = {'Content-Type': 'application/json'}


class WritingTests(unittest.TestCase):
    def setUp(self):
        requests.get(''.join(URL + ('debug/clear/',)))

    def test_01_create_user_1(self):
        # Create user
        params = {'name': 'gert', 'mailAddress': 'gertMail'}
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(201, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])

        result = json.loads(r.text)
        self.assertTrue({'id',
                'name',
                'mail_address',
                'balance',
                'last_transaction'}.issubset(result))
        self.assertEqual('gert', result['name'])
        self.assertEqual(int, type(result['id']))
        self.assertEqual(0, result['balance'])
        self.assertEqual(None, result['last_transaction'])

    def test_02_create_user_fail_duplicate(self):
        # Fail to create user with duplicate name
        params = {'name': 'gert', 'mail_address': 'gertMail'}
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(201, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])

        result = json.loads(r.text)
        self.assertTrue({'id',
                         'name',
                         'mail_address',
                         'balance',
                         'last_transaction'}.issubset(result))
        self.assertEqual('gert', result['name'])
        self.assertEqual(int, type(result['id']))
        self.assertEqual(0, result['balance'])
        self.assertEqual(None, result['last_transaction'])
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(409, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue('msg' in result)
        self.assertEqual("user gert already exists", result['msg'])

    def test_03_empty_user_transaction_list(self):
        # Show empty transactions list
        params = {'name': 'gert', 'mail_address': 'gertMail'}
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(201, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])

        result = json.loads(r.text)
        self.assertTrue({'id',
                         'name',
                         'mail_address',
                         'balance',
                         'last_transaction'}.issubset(result))
        self.assertEqual('gert', result['name'])
        self.assertEqual(int, type(result['id']))
        self.assertEqual(0, result['balance'])
        self.assertEqual(None, result['last_transaction'])
        r = requests.get(''.join((URL + ('user', '/', str(result['id']), '/', 'transaction',))), headers=HEADERS)
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        transactions = json.loads(r.text)
        self.assertTrue({'overall_count', 'limit', 'offset', 'entries'}.issubset(transactions))
        self.assertEqual({'overall_count': 0, 'limit': 100, 'offset': 0, 'entries': []}, transactions)

    def test_04_create_transaction_fail_nan(self):
        # Fail to create transaction when value is not a number
        params = {'name': 'gert', 'mail_address': 'gertMail'}
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(201, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])

        result = json.loads(r.text)
        self.assertTrue({'id',
                         'name',
                         'mail_address',
                         'balance',
                         'last_transaction'}.issubset(result))
        self.assertEqual('gert', result['name'])
        self.assertEqual(int, type(result['id']))
        self.assertEqual(0, result['balance'])
        self.assertEqual(None, result['last_transaction'])
        params = {'value': 'foo'}
        r = requests.post(''.join((URL + ('user', '/', str(result['id']), '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(400, r.status_code)
        assert r.headers['Content-Type'] == 'application/json'
        result = json.loads(r.text)
        assert 'value' in result
        assert result['value'] == ['A valid integer is required.']

