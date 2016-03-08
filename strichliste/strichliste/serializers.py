from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, Transaction


class TransactionValue(ValidationError):
    pass


class TransactionValueZero(TransactionValue):
    pass


class TransactionValueLimit(TransactionValue):
    def __init__(self, value, limit):
        self.value = value
        self.limit = limit
        TransactionValue.__init__(self, [str(self)])


class TransactionValueHigh(TransactionValueLimit):
    def __str__(self):
        return "transaction value of {} exceeds the transaction maximum of {}".format(self.value, self.limit)


class TransactionValueLow(TransactionValueLimit):
    def __str__(self):
        return "transaction value of {} falls below the transaction minimum of {}".format(self.value, self.limit)


class TransactionResultLimit(TransactionValue):
    def __init__(self, value, limit, result):
        self.value = value
        self.limit = limit
        self.result = result
        TransactionValue.__init__(self, [str(self)])


class TransactionResultHigh(TransactionResultLimit):
    def __str__(self):
        return ("transaction value of {trans_val} leads to an overall account balance of {new} "
                "which goes beyond the upper account limit of {limit}").format(trans_val=self.value,
                                                                               new=self.result,
                                                                               limit=self.limit)


class TransactionResultLow(TransactionResultLimit):
    def __str__(self):
        return ("transaction value of {trans_val} leads to an overall account balance of {new} "
                "which goes below the lower account limit of {limit}").format(trans_val=self.value,
                                                                              new=self.result,
                                                                              limit=self.limit)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'balance', 'last_transaction')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'user', 'value', 'create_date')

    def validate_value(self, value):
        config = settings.APP_CONFIG
        max_transaction = config.upper_transaction_boundary
        min_transaction = config.lower_transaction_boundary
        if value == 0:
            raise TransactionValueZero("value must not be zero")
        elif value > max_transaction:
            raise TransactionValueHigh(value, max_transaction)
        elif value < min_transaction:
            raise TransactionValueLow(value, min_transaction)
        return value

    def validate(self, transaction):
        config = settings.APP_CONFIG
        user = transaction['user']
        value = transaction['value']
        if user is None:
            raise KeyError("User not found")
        max_account = config.upper_account_boundary
        min_account = config.lower_account_boundary
        new_balance = user.balance + value
        if new_balance > max_account:
            raise TransactionResultHigh(value, max_account, new_balance)
        elif new_balance < min_account:
            raise TransactionResultLow(value, min_account, new_balance)
        return transaction
