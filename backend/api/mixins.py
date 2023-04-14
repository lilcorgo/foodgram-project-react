from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class RetrieveListViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):

    pass
