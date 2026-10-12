from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from kanban_app.api.serializers import BoardSerializer
from kanban_app.models import Board


class BoardViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_queryset(self):
        return (
            self.queryset
            .filter(
                Q(owner=self.request.user) |
                Q(members=self.request.user)
            )
            .distinct()
            .annotate(
                member_count=Count('members', distinct=True),
                ticket_count=Count('tasks', distinct=True),
                tasks_to_do_count=Count(
                    'tasks',
                    filter=Q(tasks__status='to-do'),
                    distinct=True
                ),
                tasks_high_prio_count=Count(
                    'tasks',
                    filter=Q(tasks__priority='high'),
                    distinct=True
                )
            )
        )


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
