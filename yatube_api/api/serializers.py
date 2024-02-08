from rest_framework import serializers

from posts.models import Post, Group, Comment, Follow, User
from rest_framework.exceptions import ValidationError


class AuthorMixin(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', required=False)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', required=False)
    following = serializers.CharField(source='following.username')

    class Meta:
        model = Follow
        fields = ('user', 'following',)
        read_only_fields = ('user',)

    def create(self, validated_data):
        following_username = validated_data.get('following')
        user = self.context['request'].user
        following = User.objects.get(username=following_username['username'])
        if following.username == user.username:
            raise ValidationError("Нельзя подписаться на самого себя")
        if Follow.objects.filter(
                user=user,
                following=following
        ).exists():
            raise ValidationError("Вы уже подписаны на этого пользователся")
        return Follow.objects.create(user=user, following=following)


class PostSerializer(AuthorMixin):

    class Meta:
        model = Post
        fields = ('id', 'text', 'author', 'image', 'group', 'pub_date')
        read_only_fields = ('author',)


class CommentSerializer(AuthorMixin):

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')
        read_only_fields = ('author', 'post')


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')
