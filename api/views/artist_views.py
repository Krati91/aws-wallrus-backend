from datetime import date
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from users.models import CustomUser, Artist, Interior_Decorator
from designs.models import DesignTag, Design
from django.contrib.auth import update_session_auth_hash
from ..serializers import *
from django.db.models import Count
import json


class ArtistSnippet(APIView):
    '''
    Fetch Details for Artist Snippet
    '''
    permission_classes = [IsAuthenticated]

    def get_object(self, user):
        return get_object_or_404(CustomUser, is_active=True, type=1, email=user)

    def get(self, request):
        user = self.get_object(request.user)
        serializer = ArtistSnippetSerializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


# class ArtistDesign(APIView):
#     '''
#     Fetch Artist Designs
#     '''

#     def get_object(self, user_id):
#         return get_object_or_404(CustomUser, is_active=True, type=1, pk=user_id)

#     def get(self, request, user_id):
#         user = self.get_object(user_id)
#         serializer = ArtistDesignSerializer(instance=user)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)


class DesignTagList(APIView):
    '''
    Tags list by label for upload design form
    '''

    def get(self, request):
        # back to original
        list = DesignTag.objects.values('label').distinct()
        serializer = DesignTagSerializer(instance=list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UploadDesign(APIView):
    '''
    To save a design in the database
    '''

    permission_classes = [IsAuthenticated]

    def get_user_obj(self, user_email):
        return get_object_or_404(CustomUser, type=1, email=user_email)

    def post(self, request):
        data = request.data

        for tag in data['tagDesignStyle']:
            style_tag = DesignTag.objects.filter(name=tag)
            if not style_tag.exists():
                DesignTag.objects.create(name=tag, label='Style')

        for tag in data['tagTheme']:
            style_tag = DesignTag.objects.filter(name=tag)
            if not style_tag.exists():
                DesignTag.objects.create(name=tag, label='Theme')

        style_tags = [{'label': 'Style',
                       'name': tag} for tag in data['tagDesignStyle']]

        theme_tags = [{'label': 'Theme',
                       'name': tag} for tag in data['tagTheme']]

        design_data = {
            'artist': request.user.id,
            'name': data['designName'],
            'is_customizable': True if data['customizable'] == 'Yes' else False,
            'applications': [{'name': app} for app in data['selectApp'] if app],
            'tags': style_tags + theme_tags
        }

        design_serializer = UploadDesignSerializer(data=design_data)
        if design_serializer.is_valid():
            design = design_serializer.save()
            if design:
                # adding new color tags if any
                color_tags = list(set([tag for colorway in data['colorway']
                                       for tag in colorway['tagColor']]))
                for tag in color_tags:
                    tag_obj = DesignTag.objects.filter(name=tag, label='Color')
                    if not tag_obj.exists():
                        DesignTag.objects.create(name=tag, label='Color')

                # adding colorways
                colorway_data = [{'design': design.pk,
                                  'name': colorway['name'],
                                  'image_url': colorway['link'],
                                  'color_tags': [{'label': 'Color',
                                                  'name': tag} for tag in colorway['tagColor']]

                                  }
                                 for colorway in data['colorway']]

                colorway_serializer = ColowaySerializer(
                    data=colorway_data, many=True)
                if colorway_serializer.is_valid():
                    colorway_serializer.save()
                else:
                    return Response(data=colorway_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response(data=design_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data='Design has been uploaded', status=status.HTTP_201_CREATED)


class UnderReviewView(APIView):
    '''
    List of Design with is_approved=False
    '''

    def get(self, request):
        # back to original
        list = Design.objects.filter(is_approved=False)
        serializer = UnderReviewSerializer(instance=list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)



class FeaturedArtistListView(APIView):
    '''
    Featured Artist List Based on Followers
    '''
    def get(self, request):
        # back to original
        user_list = Artist.objects.all().annotate(count_follower=Count('followers')).order_by('-count_follower')[:5]
        serializer = FeaturedArtistListSerializer(instance=user_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ArtistListStatus(APIView):
    '''
    Artist List with status
    '''

    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def get(self,request):
        user_list = Artist.objects.all().annotate(count_follower=Count('followers')).order_by('-count_follower')
        context = {'request': request} 
        serializer = ArtistListStatusSerializer(instance=user_list,context=context, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):        
        Art = Artist.objects.get(user__Unique_id=request.data['id'])
        Int_Dec = Interior_Decorator.objects.get(user = request.user.id)
        cond = Artist.objects.filter(user__Unique_id=request.data['id'], followers=Int_Dec).exists()
        print(cond)
        if cond:
            Art.followers.remove(Int_Dec)
            Art.save()
            return Response(data='Artist Removed', status=status.HTTP_200_OK)
        else:
            Art.followers.add(Int_Dec)
            Art.save()   
            return Response(data='Artist Added', status=status.HTTP_200_OK)