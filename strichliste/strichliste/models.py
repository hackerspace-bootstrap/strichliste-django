from django.db import models
from django.db.models import Sum


class User(models.Model):
    name = models.CharField(max_length=254, unique=True)
    create_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    mail_address = models.EmailField(null=True)

    @property
    def last_transaction(self):
        try:
            return self.transactions.last().create_date
        except AttributeError:
            return None

    @property
    def balance(self):
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
                             on_delete=models.PROTECT, db_index=True)
    create_date = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField()

    def to_dict(self):
        return {'id': self.id,
                'create_date': self.create_date,
                'value': self.value}

    class Meta:
        ordering = ('create_date',)

