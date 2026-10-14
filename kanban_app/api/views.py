from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from kanban_app.api.permissions import IsBoardOwnerOrMember
from kanban_app.api.serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateOutputSerializer,
    BoardUpdateSerializer,
    EmailCheckSerializer,
    TaskListSerializer,
    UserSerializer
)
from kanban_app.models import Board, Task

User = get_user_model()


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
            .annotate(**self._board_counts())
            .filter(self._board_access_filter())
            .distinct()
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
        """Select the input or output serializer for the board action."""
        if self.action == 'create':
            return BoardCreateSerializer
        if self.action == 'partial_update':
            return BoardUpdateSerializer
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

    def partial_update(self, request, *args, **kwargs):
        """Update supplied board fields and return owner and member details."""
        board = self.get_object()
        serializer = self.get_serializer(
            board, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        if getattr(board, '_prefetched_objects_cache', None) is not None:
            board._prefetched_objects_cache = {}

        return Response(BoardUpdateOutputSerializer(board).data)


class TaskViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]
    queryset = Task.objects.all()

    def assigned_to_me(self, request, *args, **kwargs):
        tasks = Task.objects.filter(assignee=request.user)
        return Response(TaskListSerializer(tasks, many=True).data)

    def reviewing(self, request, *args, **kwargs):
        tasks = Task.objects.filter(reviewer=request.user)
        return Response(TaskListSerializer(tasks, many=True).data)


class CommentViewSet(ModelViewSet):

    pass


class EmailCheckView(APIView):
    """Look up a registered user by email."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return user details for a valid, registered email."""
        email = request.query_params.get('email')

        if not email:
            return Response(
                {'error': 'Email parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EmailCheckSerializer(data={'email': email})
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email=serializer.validated_data['email']).first()
        if user:
            return Response(UserSerializer(user).data)
        return Response(status=status.HTTP_404_NOT_FOUND)
