import datetime
import json
import unittest

import requests

URL = ("http://", "127.0.0.1", ":", "8000", "/")

HEADERS = {'Content-Type': 'application/json'}


class UserCreationTests(unittest.TestCase):
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


class TransactionCreationTests(unittest.TestCase):
    def setUp(self):
        requests.get(''.join(URL + ('debug/clear/',)))
        params = {'name': 'gert', 'mail_address': 'gertMail'}
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(201, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.user = str(result['id'])

    def test_04_create_transaction_fail_nan(self):
        # Fail to create transaction when value is not a number
        params = {'value': 'foo'}
        r = requests.post(''.join((URL + ('user', '/', self.user, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue('value' in result)
        self.assertTrue(['A valid integer is required.'], result['value'])

    def test_05_create_transaction_fail_zero(self):
        # Fail to create transaction when value is zero
        params = {'value': 0}
        r = requests.post(''.join((URL + ('user', '/', self.user, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue('value must not be zero', result.get('msg'))

    def test_06_create_transaction_1(self):
        # Create transaction
        params = {'value': 1100}
        r = requests.post(''.join((URL + ('user', '/', self.user, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        now = datetime.datetime.utcnow()
        self.assertEqual(201, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue({'id', 'user', 'create_date', 'value'}.issubset(result), msg=str(result))
        self.assertEqual(self.user, str(result['user']))
        self.assertEqual(1100, result['value'])
        # TODO This assumes Z timezone a.k.a. UTC. Should be handled and parsed properly
        create_date = datetime.datetime.strptime(result['create_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertGreater(20, (now - create_date).total_seconds())

        params = {'value': 1201}
        r = requests.post(''.join((URL + ('user', '/', self.user, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        now = datetime.datetime.utcnow()
        self.assertEqual(201, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue({'id', 'user', 'create_date', 'value'}.issubset(result), msg=str(result))
        self.assertEqual(self.user, str(result['user']))
        self.assertEqual(1201, result['value'])
        # TODO This assumes Z timezone a.k.a. UTC. Should be handled and parsed properly
        create_date = datetime.datetime.strptime(result['create_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertGreater(20, (now - create_date).total_seconds())
        self.assert_user(self.user, (1100, 1201))

    def test_12_invalid_json(self):
        # Fail to create transaction with 403 (lower account boundary)
        r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data='{"name":}')
        print(r.text)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertIn('detail', result)
        self.assertIn("JSON parse error", result['detail'])

    def assert_user(self, user_id, transactions=tuple()):
        r = requests.get(''.join(URL + ('user', '/', user_id, '/')), headers=HEADERS)
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        user = json.loads(r.text)
        self.assertTrue({'mail_address', 'name', 'id', 'balance', 'last_transaction'}.issubset(user))
        self.assertEqual(user_id, str(user['id']))
        self.assertEqual(sum(transactions), user['balance'])
        self.assertIsNotNone(user['last_transaction'])

