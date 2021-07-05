from rest_framework import serializers

from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'photo']


class CommentSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'comment']