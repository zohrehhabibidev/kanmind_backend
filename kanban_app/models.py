from django.db import models

# Create your models here.


class Board(models.Model):
    title = models.CharField(max_length=250)
    members = models.ManyToManyField('auth.User', related_name='member_boards')
    owner = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='owned_boards')

    def __str__(self):
        return self.title


class Task(models.Model):
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks')

    title = models.CharField(max_length=250)
    description = models.TextField()

    class Status(models.TextChoices):
        TO_DO = 'to-do', 'To Do'
        IN_PROGRESS = 'in-progress', 'In Progress'
        REVIEW = 'review', 'Review'
        DONE = 'done', 'Done'

    status = models.CharField(max_length=20, choices=Status.choices)

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    priority = models.CharField(max_length=10, choices=Priority.choices)

    assignee = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    reviewer = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewing_tasks')

    due_date = models.DateField()
    creator = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='created_tasks')

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='authored_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.email} on {self.task.title}'
