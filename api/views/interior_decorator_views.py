from datetime import date
import calendar
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser
from product.models import Product, Collection
from orders.models import Order

from ..serializers import CollectionSerializer, DecoratorSnippetSerializer, FavouriteSerializer, MyOrderSerializer


class DecoratorSnippet(APIView):
    permission_classes = [IsAuthenticated]

    def get_decorator_object(self, decorator_email):
        return get_object_or_404(CustomUser, type=2, email=decorator_email, is_active=True)

    def get(self, request):
        object = self.get_decorator_object(request.user)
        serializer = DecoratorSnippetSerializer(instance=object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DecoratorFavourites(APIView):
    permission_classes = [IsAuthenticated]

    def get_product_objects(self, decorator_email):
        return Product.objects.filter(favourited_by__email=decorator_email, favourited_by__is_active=True)

    def get(self, request):
        objects = self.get_product_objects(request.user)
        serializer = FavouriteSerializer(instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DecoratorCollections(APIView):
    permission_classes = [IsAuthenticated]

    def get_collections(self, decorator_email):
        return Collection.objects.filter(user__email=decorator_email, user__is_active=True)

    def get(self, request):
        objects = self.get_collections(request.user)
        serializer = CollectionSerializer(instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get_order_objects(self, decorator_email):
        return Order.objects.filter(user__email=decorator_email, user__is_active=True).order_by('-id')

    def get(self, request):
        objects = self.get_order_objects(request.user)
        serializer = MyOrderSerializer(instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
