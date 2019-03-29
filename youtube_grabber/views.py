from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
from .models import KeyWord, YoutubeClip
from .serializers import KeyWordSerializer, YoutubeClipsSerializer, UserSerializer
from rest_framework.exceptions import NotFound, ParseError
import datetime


class KeyList(generics.ListCreateAPIView):
    queryset = KeyWord.objects.all()
    serializer_class = KeyWordSerializer


class KeyDelete(generics.DestroyAPIView):
    serializer_class = KeyWordSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        queryset = KeyWord.objects.all().filter(pk=pk)
        return queryset


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class YoutubeClipList(generics.ListAPIView):
    serializer_class = YoutubeClipsSerializer
    page_size = 10

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        queryset = YoutubeClip.objects.filter(key_word_id=pk)
        if 'date__gte' in self.request.query_params and 'date__lte' in self.request.query_params:
            date__gte = self.request.query_params.get('date__gte')
            date__lte = self.request.query_params.get('date__lte')
            try:
                gte = datetime.datetime.strptime(date__gte, '%d.%m.%Y')
                lte = datetime.datetime.strptime(date__lte, '%d.%m.%Y')
            except:
                raise ParseError(detail="Wrong gte or lte format")
            return queryset.filter(uploaded__range=(gte, lte))
        if queryset:
            return queryset
        else:
            raise NotFound()


class LoginView(APIView):
    permission_classes = ()
    serializer_class = UserSerializer

    def post(self, request, ):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)
