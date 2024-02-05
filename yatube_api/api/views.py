from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.exceptions import PermissionDenied

from .pagination import PostPagination
from .serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer,
    FollowSerializer
)
from posts.models import Post, Group, Follow

EXCEPTION_MESSAGES = 'Изменение чужого контента запрещено!'


class CheckAuthorMixin(viewsets.ModelViewSet):
    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied(EXCEPTION_MESSAGES)
        super(CheckAuthorMixin, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied(EXCEPTION_MESSAGES)
        super(CheckAuthorMixin, self).perform_destroy(instance)


class FollowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$following__name',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


class PostViewSet(CheckAuthorMixin):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(CheckAuthorMixin):
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
        return (
            Post.objects
            .select_related('author')
            .get(pk=self.kwargs.get('post_id'))
        )
