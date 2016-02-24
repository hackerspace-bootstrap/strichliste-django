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
