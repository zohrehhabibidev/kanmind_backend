from django.contrib.auth import get_user_model
from rest_framework import serializers

from kanban_app.models import Board, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Expose user IDs, email addresses and full names."""

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class EmailCheckSerializer(serializers.Serializer):
    """Validate the email query parameter."""
    email = serializers.EmailField()


class BoardSerializer(serializers.ModelSerializer):
    """Expose board summary fields and annotated counts."""
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id'
        ]


class BoardCreateSerializer(serializers.ModelSerializer):
    """Accept a title and member IDs for board creation."""

    class Meta:
        model = Board
        fields = ['title', 'members']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Accept title and member updates, including an empty member list."""

    class Meta:
        model = Board
        fields = ['title', 'members']
        extra_kwargs = {'members': {'allow_empty': True}}


class TaskDetailSerializer(serializers.ModelSerializer):
    """Expose task details with users and a comment count."""
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        """Return the number of comments associated with the task."""
        return obj.comments.count()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count'
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Expose board details with nested members and tasks."""
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateOutputSerializer(serializers.ModelSerializer):
    """Expose the updated board with owner and member details."""
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
