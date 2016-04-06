from django.conf.urls import url, include, patterns
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from strichliste.strichliste.views import UserViewSet, UserTransactionViewSet, TransactionViewSet

router = routers.DefaultRouter()

router.register('user', UserViewSet)
user_router = NestedSimpleRouter(router, r'user', lookup='user')
user_router.register(r'transaction', UserTransactionViewSet, base_name=r'user')

router.register('transaction', TransactionViewSet)

urlpatterns = [url(r'^', include(router.urls)), url(r'^', include(user_router.urls))]
