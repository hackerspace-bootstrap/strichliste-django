from django.conf.urls import url, include
from rest_framework import routers

from strichliste.strichliste.views import UserViewSet, TransactionViewSet

router = routers.DefaultRouter()

router.register('user', UserViewSet)
router.register('transaction', TransactionViewSet)

urlpatterns = [url(r'', include(router.urls))]
