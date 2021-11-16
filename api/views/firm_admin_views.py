from datetime import date
import calendar
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Interior_Decorator, CustomUser, Firm
from ..serializers import CardDetailSerializer, FirmUserSerializer, FirmUserListSerializer, FirmOrderSerializer, FirmSalesGraphSerializer, IntDecoratorDetailSerializer, CardDetailSerializer
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

    def get_user_objects(self, firm, from_date, to_date):
        decorators = Interior_Decorator.objects.filter(
            firm__user__email=firm, firm__user__type=3)

        result = []
        if from_date and to_date:
            from_date_array = from_date.split('-')
            end_date_array = to_date.split('-')

            start_date = date(*list(map(int, from_date_array)))
            end_date = date(*list(map(int, end_date_array)))
            for decorator in decorators:
                if decorator.user.date_joined.date() >= start_date and decorator.user.date_joined.date() <= end_date:
                    result.append(decorator)
            return result
        return decorators

    def get(self, request):
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)
        objects = self.get_user_objects(request.user, from_date, to_date)
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

    def get_order_objects(self, firm_email, filter, year_filter):
        orders = Order.objects.filter(user__email=firm_email)
        if filter and year_filter:
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
            month = months.index(filter) + 1
            today = date.today()
            year = int(year_filter)
            start_date = date(year, month, 1)

            if month == today.month and year == today.year:
                end_date = today
            else:
                last_day_of_month = calendar.monthrange(year, month)[1]
                end_date = date(year, month, last_day_of_month)
            print(start_date, end_date)
            orders = orders.filter(created_at__gte=start_date) & orders.filter(
                created_at__lte=end_date)
        print(orders)
        return orders

    def get(self, request):
        filter = request.GET.get('month', None)
        year_filter = request.GET.get('year', None)
        object = self.get_order_objects(request.user, filter, year_filter)
        serializer = FirmSalesGraphSerializer(instance=object, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IntDecoratorDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_objects(self, decorator_id):
        return get_object_or_404(CustomUser, id=decorator_id, type=2)

    def get(self, request, decorator_id):
        object = self.get_user_objects(decorator_id)
        serializer = IntDecoratorDetailSerializer(instance=object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CardDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_object(self, firm_email):
        return get_object_or_404(Firm, user__email=firm_email, user__type=3)

    def get(self, request):
        user = self.get_user_object(request.user)
        serializer = CardDetailSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)
