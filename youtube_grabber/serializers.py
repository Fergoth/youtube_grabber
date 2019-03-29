from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import YoutubeClip, KeyWord


class KeyWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyWord
        fields = ('key_word', 'id')


class YoutubeClipsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='key_word.key_word', read_only=True)
    id = serializers.IntegerField(source='key_word.id', read_only=True)

    class Meta:
        model = YoutubeClip
        fields = ('title', 'id', 'url')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(email=validated_data['email'],
                    username=validated_data['username'],
                    )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user
