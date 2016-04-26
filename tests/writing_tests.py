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

