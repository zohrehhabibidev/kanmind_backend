from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView


class BoardViewSet(ModelViewSet):

    pass


class TaskViewSet(ModelViewSet):
    def assigned_to_me(self, request, *args, **kwargs):
        pass

    def reviewing(self, request, *args, **kwargs):
        pass


class CommentViewSet(ModelViewSet):

    pass


class EmailCheckView(APIView):

    def get(self, request, *args, **kwargs):
        pass
