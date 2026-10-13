from django.db.models import Count, Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from kanban_app.api.permissions import IsBoardOwnerOrMember
from kanban_app.api.serializers import (
    BoardCreateSerializer,
    BoardSerializer,
    BoardDetailSerializer,
)
from kanban_app.models import Board


class BoardViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_queryset(self):
        if self.action in ['list', 'create']:
            return self._get_board_list_queryset()
        return self.queryset

    def _get_board_list_queryset(self):
        return (
            self.queryset
            .filter(self._board_access_filter())
            .distinct()
            .annotate(**self._board_counts())
        )

    def _board_access_filter(self):
        return (
            Q(owner=self.request.user) |
            Q(members=self.request.user)
        )

    def _board_counts(self):
        return {
            'member_count': Count('members', distinct=True),
            'ticket_count': Count('tasks', distinct=True),
            'tasks_to_do_count': Count(
                'tasks',
                filter=Q(tasks__status='to-do'),
                distinct=True
            ),
            'tasks_high_prio_count': Count(
                'tasks',
                filter=Q(tasks__priority='high'),
                distinct=True
            )
        }

    def get_serializer_class(self):
        if self.action == 'create':
            return BoardCreateSerializer
        if self.action == 'retrieve':
            return BoardDetailSerializer
        return BoardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)
        board = self.get_queryset().get(id=board.id)
        output_serializer = BoardSerializer(board)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
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
