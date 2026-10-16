from django.contrib.auth import get_user_model
from rest_framework import serializers

from kanban_app.models import Board, Comment, Task

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


class TaskListSerializer(TaskDetailSerializer):
    class Meta(TaskDetailSerializer.Meta):
        fields = (
            TaskDetailSerializer.Meta.fields[:1]
            + ['board']
            + TaskDetailSerializer.Meta.fields[1:]
        )


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        required=False,
        allow_null=True
    )

    def validate(self, attrs):
        board = self.instance.board if self.instance else attrs.get('board')

        for field in ('assignee', 'reviewer'):
            user = attrs.get(field)
            if user and not board.members.filter(pk=user.pk).exists():
                raise serializers.ValidationError({
                    f'{field}_id': (
                        f'{field.capitalize()} must be a board member.'
                    )
                })

        return attrs

    class Meta:
        model = Task
        fields = [
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'reviewer_id',
            'due_date'
        ]


class TaskUpdateSerializer(TaskCreateSerializer):
    class Meta(TaskCreateSerializer.Meta):
        fields = [
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'reviewer_id',
            'due_date'
        ]


class TaskUpdateOutputSerializer(TaskDetailSerializer):
    class Meta(TaskDetailSerializer.Meta):
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date'
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


class CommentSerializer(serializers.ModelSerializer):
    """Serialize comments for API responses."""
    author = serializers.CharField(
        source='author.fullname',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
