from rest_framework import viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .serializers import TransactionSerializer
from .serializers import TransactionValueZero, TransactionValueError
from .models import User, Transaction


class UserViewSet(viewsets.ViewSet):
    """ViewSet for Users

    This ViewSet allows access to and creation of Users.
    Currently neither authentication nor authorization are supported

    """
    @staticmethod
    def create(request) -> Response:
        """Create a user

        :param request: HTTP Request
        :return: Response
        """
        name = request.data.get('name')
        mail_address = request.data.get('mail_address')
        if name is None:
            return Response(data={'msg': "No name provided"}, status=status.HTTP_400_BAD_REQUEST)
        user = User(name=name, mail_address=mail_address)
        user.save()
        return Response(data=user.to_full_dict())

    @staticmethod
    def list(request) -> Response:
        """List users

        :param request: HTTP Request
        :return: Response
        """
        paginator = LimitOffsetPagination()
        paginator.max_limit = 250
        paginator.default_limit = 100
        users = paginator.paginate_queryset(User.objects.filter(active=True), request)
        return Response(
            data={'entries': [x.to_dict() for x in users], 'limit': paginator.limit,
                  'offset': paginator.offset, 'overall_count': paginator.count},
            status=status.HTTP_200_OK)

    @staticmethod
    def retrieve(request, pk=None) -> Response:
        """Retrieve a user by primary key

        :param request: HTTP Request
        :param pk: User primary key
        :return:
        """
        user = User.objects.get(id=pk)
        return Response(data=user.to_full_dict())


class UserTransactionViewSet(viewsets.ViewSet):
    """ViewSet for Transactions per User

    The url must provide a primary key for a user.

    This ViewSet allows access to and creation of Transaction for a single User.
    Currently neither authentication nor authorization are supported
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
        return Response(data={'transactions': [x.to_dict() for x in transactions], 'limit': paginator.limit,
                              'offset': paginator.offset, 'overall_count': paginator.count},
                        status=status.HTTP_200_OK)

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
        if len(transactions) == 0:
            return Response(data={'msg': 'transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        assert len(transactions) == 1, "Primary key is not unique"
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


class TransactionViewSet(viewsets.ViewSet):

    @staticmethod
    def list(request):
        """List transactions for all users

        :param request: Request send from the client
        :return: Response
        """
        paginator = LimitOffsetPagination()
        paginator.default_limit = 100
        transactions = paginator.paginate_queryset(Transaction.objects.all(), request)
        return Response(data={'transactions': [x.to_dict() for x in transactions], 'limit': paginator.limit,
                              'offset': paginator.offset, 'overall_count': paginator.count},
                        status=status.HTTP_200_OK)

    @staticmethod
    def retrieve(request, pk=None) -> Response:
        """Retrieve single transaction

        :param request: Request send from the client
        :param pk: Primary key to identify a transaction
        :return: Response
        """
        transactions = list(Transaction.objects.filter(id=pk))
        if len(transactions) == 0:
            return Response(data={'msg': 'transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        assert len(transactions) == 1, "Private key should identify a single transaction"
        return Response(data=transactions[0].to_dict())

