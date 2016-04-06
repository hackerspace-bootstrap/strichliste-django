from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import UserSerializer, TransactionSerializer
from .serializers import TransactionValueZero, TransactionValueError
from .models import User, Transaction


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(active=True)
    serializer_class = UserSerializer


class UserTransactionViewSet(viewsets.ViewSet):
    def list(self, request, user_pk=None):
        user = User.objects.filter(id=user_pk)
        transactions = Transaction.objects.filter(user=user)
        return Response(data={'transactions': [x.to_dict() for x in transactions]}, status=status.HTTP_200_OK)


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        _, _ = args, kwargs
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except KeyError as e:
            return Response(data={'msg': e})
        except TransactionValueZero as e:
            return Response(data={'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TransactionValueError as e:
            return Response(data={'msg': str(e)}, status=status.HTTP_403_FORBIDDEN)

