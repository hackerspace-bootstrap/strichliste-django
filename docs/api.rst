*****************************
The strichliste API Reference
*****************************

User Endpoint
=============
The user endpoint is located at `/user` and supports both `GET` and `POST`
methods.

GET
---
A ´GET´ request returns a list of user. The endpoint supports two parameter:

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

The a user dictionaries contain the following keys:

1. **id** — user id
2. **name** — user name
3. **balance** — balance of the user
4. **last_transaction** — time of the last transaction of the user

POST
----

User Details Endpoint
=====================

Transaction Endpoint
====================

Metrics Endpoint
================

Settings Endpoint
=================
