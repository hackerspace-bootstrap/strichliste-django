import datetime
import json
import unittest

import requests

URL = ("http://", "127.0.0.1", ":", "8000", "/")

HEADERS = {'Content-Type': 'application/json'}


class U2UTransactionCreationTests(unittest.TestCase):
    def setUp(self):
        requests.get(''.join(URL + ('debug/clear/',)))
        params = {'name': 'gert', 'mail_address': 'gertMail'}
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(201, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.user_a = str(result['id'])
        params = {'name': 'bert', 'mail_address': 'bertMail'}
        r = requests.post(''.join(URL + ('user/',)), headers=HEADERS, data=json.dumps(params))
        self.assertEqual(201, r.status_code, msg=r.text)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.user_b = str(result['id'])

    def test_04_create_transaction_fail_nan(self):
        # Fail to create transaction when value is not a number
        params = {'value': 'foo', 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_b, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue('value' in result)
        self.assertTrue(['A valid integer is required.'], result['value'])

    def test_05_create_transaction_fail_zero(self):
        # Fail to create transaction when value is zero
        params = {'value': 0, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue('value must not be zero', result.get('msg'))

    def test_06_create_transaction_1(self):
        # Create transaction
        params = {'value': 1100, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        now = datetime.datetime.utcnow()
        self.assertEqual(201, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue({'id', 'user', 'create_date', 'value'}.issubset(result), msg=str(result))
        self.assertEqual(self.user_a, str(result['user']))
        self.assertEqual(1100, result['value'])
        # TODO This assumes Z timezone a.k.a. UTC. Should be handled and parsed properly
        create_date = datetime.datetime.strptime(result['create_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertGreater(20, (now - create_date).total_seconds())

        params = {'value': 120, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        now = datetime.datetime.utcnow()
        self.assertEqual(201, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        self.assertTrue({'id', 'user', 'create_date', 'value'}.issubset(result), msg=str(result))
        self.assertEqual(self.user_a, str(result['user']))
        self.assertEqual(120, result['value'])
        # TODO This assumes Z timezone a.k.a. UTC. Should be handled and parsed properly
        create_date = datetime.datetime.strptime(result['create_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertGreater(20, (now - create_date).total_seconds())
        self.assert_user(self.user_a, (1100, 120))
        self.assert_user(self.user_b, (-1100, -120))

    def test_08_create_transaction_fail_lower_account_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        params = {'value': -5000}
        for _ in range(4):
            r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                              headers=HEADERS,
                              data=json.dumps(params))
            self.assertEqual(201, r.status_code)

        params = {'value': -5000, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(403, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        expected_message = "transaction value of -5000 leads to an overall account balance " \
                           "of -25000 which goes below the lower account limit of -23000"
        self.assertEqual(expected_message, result.get('msg'))

    def test_09_create_transaction_fail_upper_account_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        params = {'value': 5000}
        for _ in range(8):
            r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                              headers=HEADERS,
                              data=json.dumps(params))
            self.assertEqual(201, r.status_code)

        params = {'value': 5000, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(403, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        expected_message = "transaction value of 5000 leads to an overall account balance of 45000 " \
                           "which goes beyond the upper account limit of 42000"
        self.assertEqual(expected_message, result.get('msg'))

    def test_10_create_transaction_fail_lower_transaction_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        params = {'value': -9999999, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(403, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        expected_message = "transaction value of -9999999 falls below the transaction minimum of -5000"
        self.assertEqual(expected_message, result.get('msg'))

    def test_11_create_transaction_fail_upper_transaction_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        params = {'value': 9999999, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(403, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        expected_message = "transaction value of 9999999 exceeds the transaction maximum of 5000"
        self.assertEqual(expected_message, result.get('msg'))

    def test_12_create_transaction_fail_lower_account_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        params = {'value': -5000}
        for _ in range(4):
            r = requests.post(''.join((URL + ('user', '/', self.user_b, '/', 'transaction', '/'))),
                              headers=HEADERS,
                              data=json.dumps(params))
            self.assertEqual(201, r.status_code)

        params = {'value': +5000, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(403, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        expected_message = "transaction value of -5000 leads to an overall account balance " \
                           "of -25000 which goes below the lower account limit of -23000"
        self.assertEqual(expected_message, result.get('msg'))

    def test_13_create_transaction_fail_upper_account_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        params = {'value': 5000}
        for _ in range(8):
            r = requests.post(''.join((URL + ('user', '/', self.user_b, '/', 'transaction', '/'))),
                              headers=HEADERS,
                              data=json.dumps(params))
            self.assertEqual(201, r.status_code)

        params = {'value': -5000, 'dst': self.user_b}
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data=json.dumps(params))
        self.assertEqual(403, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])
        result = json.loads(r.text)
        expected_message = "transaction value of 5000 leads to an overall account balance of 45000 " \
                           "which goes beyond the upper account limit of 42000"
        self.assertEqual(expected_message, result.get('msg'))

    def test_14_create_transaction_fail_lower_transaction_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        # Can't properly test this, because the limit on account a triggers first
        pass

    def test_15_create_transaction_fail_upper_transaction_boundary(self):
        # Fail to create transaction with 403 (lower account boundary)
        # Can't properly test this, because the limit on account a triggers first
        pass

    def test_16_invalid_json(self):
        # Fail to create transaction with 403 (lower account boundary)
        r = requests.post(''.join((URL + ('user', '/', self.user_a, '/', 'transaction', '/'))),
                          headers=HEADERS,
                          data='{"name":}')
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
