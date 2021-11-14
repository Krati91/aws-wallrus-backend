from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Interior_Decorator, CustomUser
from ..serializers import FirmUserSerializer, FirmUserListSerializer, FirmOrderSerializer, FirmSalesGraphSerializer
from orders.models import Order


class FirmUserSnippet(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_object(self, firm_email):
        return get_object_or_404(CustomUser, email=firm_email, type=3)

    def get(self, request):
        object = self.get_user_object(request.user)
        serializer = FirmUserSerializer(instance=object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FirmUsersList(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_objects(self, firm):
        return Interior_Decorator.objects.filter(firm__user__email=firm, firm__user__type=3)

    def get(self, request):
        objects = self.get_user_objects(request.user)
        serializer = FirmUserListSerializer(instance=objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FirmOrders(APIView):
    permission_classes = [IsAuthenticated]

    def get_order_objects(self, firm_email):
        return Order.objects.filter(user__email=firm_email)

    def get(self, request):
        object = self.get_order_objects(request.user)
        serializer = FirmOrderSerializer(instance=object, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesGraph(APIView):
    permission_classes = [IsAuthenticated]

    def get_order_objects(self, firm_email):
        return Order.objects.filter(user__email=firm_email)

    def get(self, request):
        object = self.get_order_objects(request.user)
        serializer = FirmSalesGraphSerializer(instance=object, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

