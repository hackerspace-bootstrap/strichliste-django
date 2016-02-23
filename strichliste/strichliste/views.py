from rest_framework import viewsets

from .serializers import UserSerializer, TransactionSerializer
from .models import User, Transaction


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(active=True)
    serializer_class = UserSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

