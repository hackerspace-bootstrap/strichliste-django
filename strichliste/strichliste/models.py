from django.db import models
from django.db.models import Sum


class User(models.Model):
    name = models.CharField(max_length=254, unique=True)
    create_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    mail_address = models.EmailField(null=True)
    balance = models.IntegerField(default=0)

    @property
    def last_transaction(self):
        try:
            return self.transactions.last().create_date
        except AttributeError:
            return None

    def calc_balance(self):
        """This calculates the balance of the user from its transaction

        During normal usage only the balance attribute should be used, this function
        only exists to check the calculation.

        This operation might be slow but does not have any side effects.

        :return: Calculated balance
        """
        return self.transactions.aggregate(sum=Sum('value'))['sum'] or 0

    def to_full_dict(self):
        return {'id': self.id, 'name': self.name, 'mail_address': self.mail_address,
                'balance': self.balance, 'last_transaction': self.last_transaction}

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'balance': self.balance, 'last_transaction': self.last_transaction}

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey('User', related_name='transactions',
                             on_delete=models.CASCADE, db_index=True)
    create_date = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField()
    double_entry = models.ForeignKey('Transaction', on_delete=models.PROTECT, null=True)

    def to_dict(self):
        return {'id': self.id,
                'create_date': self.create_date,
                'value': self.value,
                'user': self.user_id}

    class Meta:
        ordering = ('create_date',)

