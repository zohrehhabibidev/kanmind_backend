from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from kanban_app.models import Board


class IsBoardOwnerOrMember(BasePermission):

    def has_object_permission(self, request, view, obj):
        """Allow owners and members access, but only owners may delete."""
        if view.action == "destroy":
            return obj.owner == request.user
        return request.user == obj.owner or obj.members.filter(
            pk=request.user.pk
        ).exists()


class CanCreateTask(BasePermission):
    """Allow only board members to create tasks."""

    def validate_board_id(self, board_id):
        try:
            if isinstance(board_id, float):
                raise ValueError
            return int(board_id)
        except (ValueError, TypeError):
            raise ValidationError({
                "board": ["A valid integer is required."]
            })

    def has_permission(self, request, view):
        if view.action != "create":
            return True

        board_id = request.data.get("board")
        if not board_id:
            return True

        board_id = self.validate_board_id(board_id)
        board = get_object_or_404(Board, pk=board_id)
        return board.members.filter(pk=request.user.pk).exists()
