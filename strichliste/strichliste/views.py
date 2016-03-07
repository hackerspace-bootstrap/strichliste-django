from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import UserSerializer, TransactionSerializer
from .serializers import TransactionValueZero
from .models import User, Transaction


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(active=True)
    serializer_class = UserSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        try:
            return viewsets.ModelViewSet.create(self, request=request, *args, **kwargs)
        except KeyError as e:
            return Response(data={'msg': e})
        except TransactionValueZero as e:
            return Response(data=e, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(data=e.detail, status=status.HTTP_403_FORBIDDEN)

