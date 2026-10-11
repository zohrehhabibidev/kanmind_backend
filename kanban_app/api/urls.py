from django.urls import path
from kanban_app.api.views import BoardViewSet, CommentViewSet, EmailCheckView, TaskViewSet


urlpatterns = [
    path(
        'boards/',
        BoardViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='board-list'),

    path(
        'boards/<int:pk>/',
        BoardViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='board-detail'),

    path(
        'tasks/',
        TaskViewSet.as_view({'post': 'create'}),
        name='task-list'),

    path(
        'tasks/<int:pk>/',
        TaskViewSet.as_view(
            {'patch': 'partial_update', 'delete': 'destroy'}),
        name='task-detail'
    ),

    path(
        'tasks/assigned-to-me/',
        TaskViewSet.as_view({'get': 'assigned_to_me'}),
    ),

    path(
        'tasks/reviewing/',
        TaskViewSet.as_view({'get': 'reviewing'}),
    ),

    path(
        'tasks/<int:task_id>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comment-list'
    ),

    path(
        'tasks/<int:task_id>/comments/<int:pk>/',
        CommentViewSet.as_view(
            {'delete': 'destroy'}),
        name='comment-detail'
    ),

    path(
        'email-check/',
        EmailCheckView.as_view(),
        name='email-check'
    ),

]
