from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Post, Vote 
from .serializers import PostSerializer, VoteSerializer

# Create your views here.
class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Specifies who has permission to call or read our api.

    def perform_create(self, serializer): # This auto sets the current user as the poster of an api call.
        serializer.save(poster=self.request.user) 


class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Specifies who has permission to call or read our api.

    def delete(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=self.kwargs['pk'], poster=self.request.user) #checks if the post belongs to the current user, if not the user will not be able to delete!
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('This is not your post!')

   
class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self): # This function returns a queryset
        user = self.request.user 
        post = Post.objects.get(pk=self.kwargs['pk']) 
        return Vote.objects.filter(voter=user, post=post) 

    def perform_create(self, serializer): # When someone votes, the vote gets properly saved. 
        if self.get_queryset().exists(): #prevents a user from voting on the same item
            raise ValidationError('You have already voted for this post :)') 
        serializer.save(voter=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']) )

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete() 
            return Response(status=status.HTTP_204_NO_CONTENT) 
        else:
            raise ValidationError('You  never voted for this post... silly!') 
