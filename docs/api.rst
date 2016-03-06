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

1. **limit** — optional, limits the number of returned users
2. **offset** — optional, offset the list of users

These parameters allow pagination of arbitrary page sizes. A upper limit might be
imposed in the future. In that case the limit imposed by the server will be returned
in the corresponding field in the response.

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
The endpoint supports one parameters:

1. **value** — value of the transaction in the smallest currency unit

Errors
^^^^^^
If the **value** is not an integer or zero, a *400 BadRequest* response is returned.

The **value** is boundary checked, if those fail a *409 Forbidden* response is returned.

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

Metrics Endpoint
================

Settings Endpoint
=================
