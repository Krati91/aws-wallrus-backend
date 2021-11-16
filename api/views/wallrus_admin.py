from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from designs.models import Design
from ..serializers import DesignListSerializer, DesignDetailSerializer, PostListSerializer, PostDetailSerializer, NewArtistsSerializer, NewPostSerializer, OrderListSerializer, OrderDetailSerializer, AdminArtistDetailSerializer, UpdateArtistStatusSerializer, UpdateDesignStatusSerializer, UpdateOrderStatusSerializer, MonthlySalesSerializer
from posts.models import Post
from users.models import CustomUser, Interior_Decorator
from orders.models import Order


class DesignList(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_design_list(self):
        return Design.objects.all().order_by('-id')

    def get(self, request):
        objects = self.get_design_list()
        serializer = DesignListSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class DesignDetail(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_design_object(self, design_id):
        return get_object_or_404(Design, id=design_id)

    def get(self, request, design_id):
        object = self.get_design_object(design_id)
        serializer = DesignDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostList(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_post_list(self):
        return Post.objects.all().order_by('-id')

    def get(self, request):
        objects = self.get_post_list()
        serializer = PostListSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostDetail(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_post_object(self, post_slug):
        return get_object_or_404(Post, slug=post_slug)

    def get(self, request, post_slug):
        object = self.get_post_object(post_slug)
        serializer = PostDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CreatePost(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request):
        serializer = NewPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'The post has been created'}, status=status.HTTP_200_OK)
        return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class NewArtists(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_artist_objects(self, from_date, to_date):
        artists = CustomUser.objects.filter(type=1, is_active=True)

        return [artist for artist in artists if (artist.date_joined.date() >= from_date and artist.date_joined.date() <= to_date)]

    def get(self, request):
        curr_date = date.today()
        curr_month = curr_date.month
        curr_year = curr_date.year

        start_date = date(curr_year, curr_month, 1)

        objects = self.get_artist_objects(start_date, curr_date)
        serializer = NewArtistsSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OrderList(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_order_objects(self):
        return Order.objects.all().order_by('-id')

    def get(self, request):
        objects = self.get_order_objects()
        serializer = OrderListSerializer(instance=objects, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OrderDetail(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_order_object(self, order_id):
        return get_object_or_404(Order, id=order_id)

    def get(self, request, order_id):
        object = self.get_order_object(order_id)
        serializer = OrderDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AdminArtistDetail(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_user_object(self, artist_id):
        return get_object_or_404(CustomUser, id=artist_id, type=1)

    def get(self, request, artist_id):
        object = self.get_user_object(artist_id)
        print(object)
        serializer = AdminArtistDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ApproveArtist(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_user_object(self, artist_id):
        return get_object_or_404(CustomUser, id=artist_id, type=1)

    def patch(self, request, artist_id):
        object = self.get_user_object(artist_id)
        artist_status = request.GET['status']
        if artist_status == 'approve':
            data = {
                'is_active': True
            }
        elif artist_status == 'reject':
            data = {
                'is_active': False
            }
        serializer = UpdateArtistStatusSerializer(instance=object, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class ApproveDesign(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_design_object(self, design_id):
        return get_object_or_404(Design, id=design_id)

    def patch(self, request, design_id):
        object = self.get_design_object(design_id)
        design_status = request.GET['status']
        if design_status == 'approve':
            data = {
                'is_approved': True
            }
        elif design_status == 'reject':
            data = {
                'is_approved': False
            }
        serializer = UpdateDesignStatusSerializer(instance=object, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class ApproveOrder(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request, order_id):
        order_status = request.GET['status']
        if order_status == 'approve':
            data = {
                'order': order_id,
                'name': 'confirmed'
            }
        elif order_status == 'reject':
            data = {
                'order': order_id,
                'name': 'rejected'
            }
        serializer = UpdateOrderStatusSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Status Updated'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(data={'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class MonthlySales(APIView):
    def get_order_objects(self, from_date, to_date):
        orders = Order.objects.filter(
            created_at__gte=from_date) & Order.objects.filter(created_at__lte=to_date)
        return orders

    def get(self, request):
        cur_date = date.today()
        start_date = date(cur_date.year, cur_date.month, 1)

        objects = self.get_order_objects(start_date, cur_date)
        serializer = MonthlySalesSerializer(instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlyDecoratorsCount(APIView):
    def get_decorator_objects(self, from_date, to_date):
        decorators = Interior_Decorator.objects.filter(user__is_active=True)
        decorators = decorators.filter(
            user__date_joined__gte=from_date) & decorators.filter(user__date_joined__lte=to_date)
        return decorators

    def get(self, request):
        cur_date = date.today()
        start_date = date(cur_date.year, cur_date.month, 1)

        objects = self.get_order_objects(start_date, cur_date)
        serializer = MonthlySalesSerializer(instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
