from rest_framework.permissions import BasePermission


class IsBoardOwnerOrMember(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or obj.members.filter(
            pk=request.user.pk
        ).exists()
