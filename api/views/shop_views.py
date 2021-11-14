from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import CustomUser
from product.models import Product, Application, Tag
from designs.models import Design
from ..serializers import *


class FilterList(APIView):
    '''
    Tags list by label for upload design form
    '''

    def get_tag_label_by_products(self, application_slug):
        return Product.objects.filter(
            application__slug=application_slug).values('tags__label').distinct()

    def get(self, request, application_slug):
        list = self.get_tag_label_by_products(application_slug)

        tags = Tag.objects.filter(label__in=list).values('label').distinct()
        serializer = FilterSerializer(instance=tags, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ApplicationProductList(APIView):
    permission_classes = [AllowAny]

    def get_objects(self, application_slug):
        return Product.objects.filter(is_active=True, application__slug=application_slug, application__is_active=True)

    def get(self, request, application_slug):
        object = self.get_objects(application_slug)
        serializer = ProductListSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductDetail(APIView):
    permission_classes = [AllowAny]

    def get_product_object(self, product_slug):
        return get_object_or_404(Product, is_active=True, slug=product_slug)

    def get(self, request, product_slug):
        object = self.get_product_object(product_slug)
        serializer = ProductDetailSerializer(instance=object)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OtherColorways(APIView):
    permission_classes = [AllowAny]

    def get_object(self, product_slug):
        designs = Product.objects.filter(
            is_active=True, slug=product_slug).values_list('design__name', flat=True)
        return Product.objects.filter(design__name=designs.first(), is_active=True).exclude(slug=product_slug)

    def get(self, request, product_slug):
        object = self.get_object(product_slug)
        serializer = ProductListSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OtherApplications(APIView):
    permission_classes = [AllowAny]

    def get_object(self, product_slug):
        applications = Product.objects.filter(
            is_active=True, slug=product_slug).values_list('application__name', flat=True)
        return Product.objects.filter(is_active=True).exclude(application__name=applications.first())

    def get(self, request, product_slug):
        object = self.get_object(product_slug)
        serializer = ProductListSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class SimilarDesigns(APIView):
    permission_classes = [AllowAny]

    def get_object(self, product_slug):
        applications = Product.objects.filter(
            is_active=True, slug=product_slug).values_list('application__name', flat=True)
        return Product.objects.filter(application__name=applications.first(), is_active=True).exclude(slug=product_slug)

    def get(self, request, product_slug):
        object = self.get_object(product_slug)
        serializer = ProductListSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class DesignerListView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, application_slug):
        design = Product.objects.filter(
            is_active=True, application__slug=application_slug).values_list('design__name', flat=True).distinct()
        return Design.objects.filter(name__in=design,is_approved=True).distinct()

    def get(self, request, application_slug):
        object = self.get_object(application_slug)
        serializer = DesignListSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class FilterTagList(APIView):
    permission_classes = [AllowAny]

    def get_object(self, tag_slug):
        design = Product.objects.filter(
            is_active=True, slug_tag=tag_slug).values_list('tags__name', flat=True).distinct()
        print(design)
        print(Product.objects.filter(tags__name__in=design).distinct())
        return Product.objects.filter(tags__name__in=design).distinct()

    def get(self, request, tag_slug):
        object = self.get_object(tag_slug)
        serializer = ProductListSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class LatestDesignList(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        object = Product.objects.order_by('-created_at')[:10]
        serializer = ProductListSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class DesignListView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        object = Product.objects.all()
        serializer = DesignSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ProductReviewView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        object = Reviews.objects.all()
        serializer = ProductReviewSerializer(instance=object, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)