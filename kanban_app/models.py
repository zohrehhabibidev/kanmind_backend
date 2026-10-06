from django.db import models

# Create your models here.


class Board(models.Model):
    title = models.CharField(max_length=250)
    members = models.ManyToManyField('auth.User', related_name='member_boards')
    owner = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='owned_boards')

    def __str__(self):
        return self.title
