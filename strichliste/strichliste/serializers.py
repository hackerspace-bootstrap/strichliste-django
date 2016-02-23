from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, Transaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'balance', 'last_transaction')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'user', 'value', 'create_date')

    def validate_value(self, value):
        raise ValidationError('Value not infinite')
