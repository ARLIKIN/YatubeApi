from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .pagination import PostPagination
from .serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer,
    FollowSerializer
)
from posts.models import Post, Group, User

EXCEPTION_MESSAGE = 'Изменения чужого контента запрещено!'


class BaseCheckAuthor(viewsets.ModelViewSet):
    def perform_update(self, serializer):
        self.check_author(serializer.instance.author)
        super(BaseCheckAuthor, self).perform_update(serializer)

    def perform_destroy(self, instance):
        self.check_author(instance.author)
        super(BaseCheckAuthor, self).perform_destroy(instance)

    def check_author(self, author):
        if author != self.request.user:
            raise PermissionDenied(EXCEPTION_MESSAGE)


class FollowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$following__username',)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.users.all()


class PostViewSet(BaseCheckAuthor):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(BaseCheckAuthor):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = self.get_post()
        serializer.save(
            author=self.request.user,
            post=post
        )

    def get_queryset(self):
        return self.get_post().comments.all()

    def get_post(self):
        return get_object_or_404(
            Post.objects
            .select_related('author'),
            pk=self.kwargs.get('post_id')
        )
