from rest_framework import viewsets, mixins, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .serializers import TransactionSerializer
from .serializers import TransactionValueZero, TransactionValueError
from .models import User, Transaction


class UserViewSet(viewsets.ViewSet):

    @staticmethod
    def create(request) -> Response:
        name = request.data.get('name')
        mail_address = request.data.get('mail_address')
        if name is None:
            return Response(data={'msg': "No name provided"}, status=status.HTTP_400_BAD_REQUEST)
        user = User(name=name, mail_address=mail_address)
        user.save()
        return Response(data=user.to_full_dict())

    @staticmethod
    def list(request) -> Response:
        users = User.objects.filter(active=True)

        return Response(data={'entries': [x.to_dict() for x in users]})

    @staticmethod
    def retrieve(request, pk=None) -> Response:
        user = User.objects.get(id=pk)
        return Response(data=user.to_full_dict())


class UserTransactionViewSet(viewsets.ViewSet):
    """ViewSet for Transactions per User

    The url must provide a primary key for a user.
    """
    @staticmethod
    def list(request, user_pk=None) -> Response:
        """List transactions for a single user

        :param request: Request send from the client
        :param user_pk: Primary key to identify a user
        :return: Response
        """
        user = User.objects.filter(id=user_pk)
        paginator = LimitOffsetPagination()
        paginator.default_limit = 100
        transactions = paginator.paginate_queryset(Transaction.objects.filter(user=user), request)
        return Response(data={'transactions': [x.to_dict() for x in transactions]}, status=status.HTTP_200_OK)

    @staticmethod
    def retrieve(request, pk=None, user_pk=None) -> Response:
        """Retrieve single transaction for a user

        :param request: Request send from the client
        :param pk: Primary key to identify a transaction
        :param user_pk: Primary key to identify a user
        :return: Response
        """
        user = User.objects.get(id=user_pk)
        transactions = list(Transaction.objects.filter(user=user, id=pk))
        assert len(transactions) == 1
        return Response(data=transactions[0].to_full_dict())

    @staticmethod
    def create(request, user_pk=None) -> Response:
        """Create a new transaction for a user

        :param request: Request send from the client
        :param user_pk: Primary key to identify a user
        :return: Response
        """
        value = request.data.get('value')
        if value is None:
            return Response(data={'msg': 'Value missing'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = TransactionSerializer(data={'user': user_pk, 'value': value})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response(data={'msg': e})
        except TransactionValueZero as e:
            return Response(data={'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TransactionValueError as e:
            return Response(data={'msg': str(e)}, status=status.HTTP_403_FORBIDDEN)


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

