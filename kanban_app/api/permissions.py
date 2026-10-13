from rest_framework.permissions import BasePermission


class IsBoardOwnerOrMember(BasePermission):

    def has_object_permission(self, request, view, obj):
        """Allow owners and members access, but only owners may delete."""
        if view.action == "destroy":
            return obj.owner == request.user
        return request.user == obj.owner or obj.members.filter(
            pk=request.user.pk
        ).exists()
