*****************************
The strichliste API Reference
*****************************

User Endpoint
=============
The user endpoint is located at ``/user`` and supports both `GET` and `POST`
methods.

GET
---
A `GET` request returns a list of user. The endpoint supports two parameter:

1. **limit** — optional, limits the number of returned users, default limit is 100 elements
2. **offset** — optional, offsets the list of users

These parameters allow pagination of arbitrary page sizes. The upper limit is 250 elements
The response will return the actually used limit.

The response consists of a dictionary containing the following keys:

1. **limit** — limit used in the query
2. **offset** — offset used in the query
3. **overall_count** — number of all users in the system
4. **entries** — list of user dictionaries

The user dictionaries contain the following keys:

1. **id** — user id
2. **name** — user name
3. **balance** — balance of the user
4. **last_transaction** — time of the last transaction of the user

POST
----
On this endpoint, the `POST` method is used to create a new user. The endpoint supports two parameters:

1. **name** — required, name of the user to be created
2. **email_address** — required, email address to be associated with the user

The response has the HTTP status code 201 and consists of a dictionary
containing the following keys:

1. **id** — user id
2. **name** — user name
3. **balance** — balance of the user
4. **last_transaction** — time of the last transaction of the user
5. **balance** — balance of the created user. (Should always be zero, but this is not guarantied)

Errors
^^^^^^
If either **name** or **email_address** are already in the database, a *409 Conflict* response is returned.

If either **name** or **email_address** is not provided, a *400 BadRequest* response is returned.

.. note::
    Error messages are not yet determined.



User Details Endpoint
=====================
The user details endpoint is located at ``/user/$user_id`` where ``$user_id`` is the numerical id of a user
It supports only the `GET` method.

GET
---
On this endpoint, the `GET` method is used to access details of a user.
The response consists of a dictionary containing the following keys:

1. **id** — user id
2. **name** — user name
3. **balance** — balance of the user
4. **last_transaction** — time of the last transaction of the user
5. **balance** — balance of the created user. (Should always be zero, but this is not guarantied)

Errors
^^^^^^
If the **user_id** is not an integer, a *400 BadRequest* response is returned.

If there is no user with the provided **user_id** a *404 NotFound* is returned.


User Transaction Endpoint
=========================
There are two endpoints to retrieve transactions, one global at ``/transaction`` and a user specific one
at ``/user/$user_id/transaction`` where ``$user_id`` is the numerical id of a user.

The user specific endpoint is a sub-endpoint of the user detail endpoint and has the same error
responses. It supports the `GET` and `POST` methods.

GET
---
On this endpoint, the `GET` method is used to retrieve a list of transactions of a specific user.
The response consist of a dictionary containing the following keys:

1. **limit** — limit transactions in the query
2. **offset** — offset used in the query
3. **overall_count** — number of all transactions in the system
4. **entries** — list of transaction dictionaries

POST
----
On this endpoint, the `POST` method is used to create a new transaction.
The endpoint supports one mandatory and one optional parameter:

1. **value** — value of the transaction in the smallest currency unit
2. **dst** - (optional) ID of an account to transfer funds to

If the **dst** parameter is provided any funds removed from the first account are added the destination account
and vice versa.

Errors
^^^^^^
If the **value** is not an integer or zero, a *400 BadRequest* response is returned.

The **value** is boundary checked, if those fail a *403 forbidden* response is returned.

.. note::
    Error messages are not yet determined.


Global Transaction Endpoint
===========================
There are two endpoints to retrieve transactions, one global at ``/transaction`` and a user specific one
at ``/user/$user_id/transaction`` where ``$user_id`` is the numerical id of a user.

The global endpoint supports only the `GET` method.

GET
---
On this endpoint, the `GET` method is used to retrieve a list of transactions of all users.
The response consist of a dictionary containing the following keys:

1. **limit** — limit transactions in the query
2. **offset** — offset used in the query
3. **overall_count** — number of all transactions in the system
4. **entries** — list of transaction dictionaries

The transaction dictionaries contain the following keys:

1. **id** — transaction id
2. **user_id** — user id
3. **value** — value of the transaction in the smallest currency unit
4. **create_date** — date this transaction was created



Settings Endpoint
=================
The settings endpoint is located at ``/settings``.

GET
---
This endpoint returns currently defined limits on transactions and accounts. It takes no parameters and does not
return any errors.::

    {
      boundaries: {
        transaction: {
            upper: <int>,
            lower: <int>},
        account: {
            upper: <int>,
            lower: <int>}
      }
    }

All four boundaries are defined as cent values.

Metrics Endpoint
================
The metrics endpoint is located at ``/metrics``.

GET
---
This endpoint returns statistics about users and recent transactions.
Per day statistics will be calculated and returned for the last 7 days.::

    {
      overallBalance: <int>,
      countTransactions: <int>,
      contUsers: <int>,
      avgBalance: <int>,
      days: [
        {
          date: <Date>,
          overallNumber: <int>,
          distinctUsers: <int>,
          dayBalance: <float>,
          dayBalancePositive: <int>,
          dayBalanceNegative: <int>
        }
      ]
    }

All balances are given in cents and all averages are rounded to the nearest cent value.
