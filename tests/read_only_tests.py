import json

import requests

URL = ("http://", "127.0.0.1", ":", "8000", "/")

HEADERS = {'Content-Type': 'application/json'}


def test_empty_user_list():
    r = requests.get(''.join(URL + ('user',)))
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'
    users = json.loads(r.text)
    assert {'overall_count', 'limit', 'offset', 'entries'}.issubset(users)
    assert users['overall_count'] == 0
    assert users['limit'] == 100
    assert users['offset'] == 0
    assert users['entries'] == []


def test_user_not_found():
    r = requests.get(''.join(URL + ('user', '/', '10')))
    assert r.status_code == 404
    assert r.headers['Content-Type'] == 'application/json'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "user 10 not found"


def test_user_not_found_transactions():
    r = requests.get(''.join(URL + ('user', '/', '10', '/', 'transaction')))
    assert r.status_code == 404
    assert r.headers['Content-Type'] == 'application/json'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "user 10 not found"


def test_empty_transactions():
    r = requests.get(''.join((URL + ('transaction',))))
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'
    transactions = json.loads(r.text)
    assert {'overall_count', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overall_count'] == 0
    assert transactions['limit'] == 100
    assert transactions['offset'] == 0
    assert transactions['entries'] == []


def test_user_limits():
    r = requests.get(''.join(URL + ('user',)),
                     headers=HEADERS,
                     params={'offset': 1, 'limit': 1})
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'
    transactions = json.loads(r.text)
    assert {'overall_count', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overall_count'] == 0
    assert transactions['limit'] == 1
    assert transactions['offset'] == 1
    assert transactions['entries'] == []


def test_user_limits_max():
    r = requests.get(''.join(URL + ('user',)),
                     headers=HEADERS,
                     params={'offset': 0, 'limit': 1000})
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'
    transactions = json.loads(r.text)
    assert {'overall_count', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overall_count'] == 0
    assert transactions['limit'] == 250  # 250 is the max
    assert transactions['offset'] == 0
    assert transactions['entries'] == []

