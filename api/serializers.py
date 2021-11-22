
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import password_validation
from users.models import CustomUser, Interior_Decorator, RandomPassword, Artist, Firm
from user_details.models import Address, BusinessDetail, BankDetail

from django.db.models import Count
from .utils import get_tags_by_label, random_password_generator, Encrypt_and_Decrypt
from designs.models import Design, DesignTag, Colorway
from notifications.models import ArtistNotificationSettings
from product.models import Application, Product, ProductImages, Reviews, Tag, Collection
from posts.models import Post
from orders.models import Order, Item, OrderStatus


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            # 12 characters are more than enough.
            file_name = str(uuid.uuid4())[:12]
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    profile_picture = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'type',
                  'profile_picture', 'first_name', 'last_name', 'username',  'phone', 'bio')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        random_string = ''

        if password:
            instance.set_password(password)
        else:
            random_string = random_password_generator()
            instance.set_password(random_string)
        instance.save()

        if random_string:
            obj = RandomPassword.objects.create(
                user=instance, random_string=random_string)
            obj.save()

        return instance


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('user', 'type', 'line1', 'line2', 'city', 'state', 'pincode')


class BusinessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDetail
        fields = ('user', 'pan_card_number', 'brand_name',
                  'gst_number', 'phone', 'email')

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        pan_card_number = instance.pan_card_number
        gst_number = instance.gst_number
        if pan_card_number and gst_number:
            en = Encrypt_and_Decrypt()
            instance.pan_card_number = en.encrypt(pan_card_number)
            instance.gst_number = en.encrypt(gst_number)
            del en
        instance.save()
        return instance


class BankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetail
        fields = ('user', 'account_number', 'name',
                  'branch', 'ifsc_code', 'swift_code')

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        account_number = instance.account_number
        swift_code = instance.swift_code
        if account_number and swift_code:
            en = Encrypt_and_Decrypt()
            instance.account_number = en.encrypt(account_number)
            instance.swift_code = en.encrypt(swift_code)
            del en
        instance.save()
        return instance


class ApplistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['name', 'slug']


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password']

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value


##################################################### ARTIST SERIALIZERS ###################################################

class ArtistSnippetSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    total_designs = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()

    def get_level(self, obj):
        return obj.artist.level.get_name_display()

    def get_followers(self, obj):
        return obj.artist.followers.count()

    def get_total_designs(self, obj):
        return obj.artist.get_total_designs()

    def get_views(self, obj):
        # To Do Product views
        pass

    def get_member_since(self, obj):
        return obj.date_joined.date()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name',
                  'profile_picture',
                  'level', 'bio', 'total_designs', 'followers', 'views', 'member_since']


class DesignTagSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return get_tags_by_label(DesignTag, obj['label'])

    class Meta:
        model = DesignTag
        fields = ['label', 'tags']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        for tag in self.initial_data['tags']:
            self.instance.name = tag['name']

        self.instance.save()
        return self.instance


class ArtistNotificationSettingsSerailizer(serializers.ModelSerializer):
    follower_frequency = serializers.SerializerMethodField()
    payment_frequency = serializers.SerializerMethodField()
    design_view_frequency = serializers.SerializerMethodField()
    design_favorite_frequency = serializers.SerializerMethodField()
    design_purchase_frequency = serializers.SerializerMethodField()

    class Meta:
        model = ArtistNotificationSettings
        fields = ['follower_frequency', 'payment_frequency',
                  'design_view_frequency',
                  'design_favorite_frequency',
                  'design_purchase_frequency']

    def get_follower_frequency(self, obj):
        return obj.get_follower_frequency_display()

    def get_payment_frequency(self, obj):
        return obj.get_payment_frequency_display()

    def get_design_view_frequency(self, obj):
        return obj.get_design_view_frequency_display()

    def get_design_favorite_frequency(self, obj):
        return obj.get_design_favorite_frequency_display()

    def get_design_purchase_frequency(self, obj):
        return obj.get_design_purchase_frequency_display()

    def save(self, **kwargs):
        super().save(**kwargs)

        frequency_status = ['Immediately', 'Daily', 'Weekly', 'Monthly']

        self.instance.follower_frequency = frequency_status.index(
            self.initial_data['follower_frequency']) + 1

        self.instance.payment_frequency = frequency_status.index(
            self.initial_data['payment_frequency']) + 1

        self.instance.design_view_frequency = frequency_status.index(
            self.initial_data['design_view_frequency']) + 1

        self.instance.design_favorite_frequency = frequency_status.index(
            self.initial_data['design_favorite_frequency']) + 1

        self.instance.design_purchase_frequency = frequency_status.index(
            self.initial_data['design_purchase_frequency']) + 1

        self.instance.save()

        return self.instance


class UnderReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ['name']


class UploadDesignTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTag
        fields = ['name', 'label']


class ColowaySerializer(serializers.ModelSerializer):
    color_tags = UploadDesignTagSerializer(many=True)

    class Meta:
        model = Colorway
        fields = ['design', 'name', 'image_url', 'color_tags']

    def create(self, validated_data):
        color_tags = validated_data.pop('color_tags')
        instance = self.Meta.model(**validated_data)
        instance.save()

        for tag in color_tags:
            tag_obj, _ = DesignTag.objects.get_or_create(**tag)
            instance.color_tags.add(tag_obj)

        instance.save()

        return instance


class UploadDesignSerializer(serializers.ModelSerializer):
    applications = ApplistSerializer(many=True)
    tags = UploadDesignTagSerializer(many=True)

    class Meta:
        model = Design
        fields = ['artist', 'name', 'is_customizable', 'applications', 'tags']

    def create(self, validated_data):
        apps = validated_data.pop('applications')
        tags = validated_data.pop('tags')
        instance = self.Meta.model(**validated_data)
        instance.save()

        for app in apps:
            app_obj = Application.objects.get(**app)
            instance.applications.add(app_obj)
        for tag in tags:
            tag_obj = DesignTag.objects.get(**tag)
            instance.tags.add(tag_obj)

        instance.save()
        return instance


class UserTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = CustomUser
        fields = ['type']


############################################################## SHOP SERIALIZERS #######################################################

class FilterSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return get_tags_by_label(Tag, obj['label'])

    class Meta:
        model = Tag
        fields = ['label', 'tags']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTag
        fields = ['name', 'label']


class ProductImagesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = ProductImages
        fields = ['image']


class ProductListSerializer(serializers.ModelSerializer):
    productimages_set = ProductImagesSerializer(many=True)
    design_name = serializers.SerializerMethodField()
    colorway_name = serializers.SerializerMethodField()
    application = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()

    # def get_product_image(self, obj):
    #     return obj.get_display_image()

    def get_design_name(self, obj):
        return obj.design.name

    def get_colorway_name(self, obj):
        return obj.colorway.name

    def get_application(self, obj):
        return obj.application.name

    def get_artist(self, obj):
        return obj.get_artist_name()

    class Meta:
        model = Product
        fields = ['artist', 'design_name',
                  'application', 'colorway_name', 'productimages_set', 'slug']


class ReviewsSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    def get_reviewer(self, obj):
        return obj.get_reviewer_name()

    def get_profile_picture(self, obj):
        return obj.get_reviewer_picture()

    class Meta:
        model = Reviews
        fields = ['reviewer', 'profile_picture', 'rating',
                  'review', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    number_of_ratings = serializers.SerializerMethodField()
    base_cost = serializers.SerializerMethodField()
    productimages_set = ProductImagesSerializer(many=True)
    application = serializers.SerializerMethodField()
    colorway = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    reviews_set = ReviewsSerializer(many=True)
    design_name = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        return obj.get_average_rating()

    def get_number_of_ratings(self, obj):
        return obj.get_number_of_ratings()

    def get_artist(self, obj):
        return obj.get_artist_name()

    def get_application(self, obj):
        return obj.application.name

    def get_colorway(self, obj):
        return obj.colorway.name

    def get_base_cost(self, obj):
        return obj.get_base_cost()

    def get_design_name(self, obj):
        return obj.design.name

    class Meta:
        model = Product
        fields = ['application', 'colorway', 'design_name', 'productimages_set',
                  'artist', 'ratings', 'number_of_ratings', 'material', 'base_cost', 'reviews_set']


class ProfileImageSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = CustomUser
        fields = ['profile_picture']


class FeaturedArtistListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user = ProfileImageSerializer()
    no_of_designs = serializers.SerializerMethodField()
    no_of_followers = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['full_name', 'no_of_followers', 'no_of_designs', 'user']

    def get_full_name(self, obj):
        return obj.user.first_name+' '+obj.user.last_name

    def get_no_of_followers(self, obj):
        return obj.followers.count()

    def get_no_of_designs(self, obj):
        return Design.objects.filter(artist=obj.user).count()


class DesignListSerializer(serializers.ModelSerializer):
    designer = serializers.SerializerMethodField()

    class Meta:
        model = Design
        fields = ['designer']

    def get_designer(self, obj):
        return obj.get_artist_name()


# class ArtistListStatusSerializer(serializers.ModelSerializer):
#     full_name = serializers.SerializerMethodField()
#     status = serializers.SerializerMethodField()
#     profile_picture =ProductImagesSerializer(many=True)
#     class Meta:
#         model = Artist
#         fields = ['full_name','status','profile_picture']
#     def get_full_name(self,obj):
#         return obj.user.first_name+' '+obj.user.last_name

#     def get_status(self,obj):
#         # name = CustomUser.objects.get(email=self.context['request'].user)
#         temp = obj.followers.filter(user__email=self.context['request'].user).exists()
#         return temp


class ArtistListStatusSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    Unique_id = serializers.SerializerMethodField()
    Designs = serializers.SerializerMethodField()
    user = ProfileImageSerializer()
    design_images = serializers.SerializerMethodField()


    class Meta:
        model = Artist
        fields = ['full_name', 'followers',
                  'Designs', 'status', 'user', 'Unique_id', 'design_images']

    def get_full_name(self, obj):
        return obj.user.first_name+' '+obj.user.last_name

    def get_status(self, obj):
        # name = CustomUser.objects.get(email=self.context['request'].user)
        temp = Artist.objects.filter(
            followers__user__email=self.context['request'].user, pk=obj.user.id).exists()
        return temp

    def get_followers(self, obj):
        return obj.followers.count()

    def get_Unique_id(self, obj):
        return obj.user.Unique_id

    def get_Designs(self, obj):
        return Design.objects.filter(artist=obj.user).count()

    def get_design_images(self, obj):
        products = Product.objects.filter(design__artist=obj.user)
        images = [product.get_display_image() for product in products]
        return images[0:3]

class DesignSerializer(serializers.ModelSerializer):
    designer_name = serializers.SerializerMethodField()
    productimages_set = ProductImagesSerializer(many=True)
    designer_picture = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['designer_name', 'productimages_set', 'designer_picture']

    def get_designer_name(self, obj):
        return obj.get_artist_name()

    def get_designer_picture(self, obj):
        if obj.design.artist.profile_picture:
            return obj.design.artist.profile_picture.url
        else:
            return "/media/profile_pictures/unknown.png"


class ProductReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()

    class Meta:
        model = Reviews
        fields = ['reviewer', 'profile_picture', 'rating',
                  'review', 'created_at', 'product_slug']

    def get_reviewer(self, obj):
        return obj.get_reviewer_name()

    def get_profile_picture(self, obj):
        return "/media/"+obj.get_reviewer_picture()

    def get_product_slug(self, obj):
        return obj.product.slug

##################################################### FIRM SERIALIZERS ###################################################


class FirmUserListSerializer(serializers.ModelSerializer):
    commission = serializers.SerializerMethodField()
    total_sale = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    def get_commission(self, obj):
        return obj.get_commision_percent()

    def get_total_sale(self, obj):
        orders = Order.objects.filter(user=obj.user)
        order_cost = 0
        for order in orders:
            for item in order.items.all():
                order_cost += item.product.cost * item.quantity
        return order_cost

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_username(self, obj):
        return obj.user.username

    def get_is_verified(self, obj):
        return obj.user.is_active

    def get_level(self, obj):
        return obj.level.get_name_display()

    class Meta:
        model = Interior_Decorator
        fields = ['user', 'first_name',
                  'last_name', 'username', 'is_verified', 'level',
                  'commission', 'total_sale']


class FirmOrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_status(self, obj):
        order_status = obj.order_status.order_by('-id').first()
        if order_status:
            return order_status.name
        else:
            return None

    def get_user(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status']


class FirmUserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    business_details = BusinessDetailSerializer()
    bank_details = BankDetailSerializer()

    def get_type(self, obj):
        return obj.get_type_display()

    class Meta:
        model = CustomUser
        fields = ['profile_picture', 'first_name', 'last_name',
                  'email', 'phone', 'username', 'type', 'business_details', 'bank_details']


class FirmSalesGraphSerializer(serializers.ModelSerializer):
    order_cost = serializers.SerializerMethodField()

    def get_order_cost(self, obj):
        order_cost = 0
        for item in obj.items.all():
            order_cost += item.product.cost * item.quantity
        return order_cost

    class Meta:
        model = Order
        fields = ['created_at', 'order_cost']


class IntDecoratorDetailSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    business_details = BusinessDetailSerializer()
    bank_details = BankDetailSerializer()

    def get_level(self, obj):
        decorator = get_object_or_404(Interior_Decorator, user=obj.id)
        return decorator.level.get_name_display()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email',
                  'phone', 'level', 'business_details', 'bank_details']


class CardDetailSerializer(serializers.ModelSerializer):
    total_decorators = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()

    def get_total_decorators(self, obj):
        members = obj.get_members().count()
        return members

    def get_total_profit(self, obj):
        orders = Order.objects.filter(user=obj.user)
        order_cost = 0
        for order in orders:
            for item in order.items.all():
                order_cost += item.product.cost * item.quantity
        return order_cost

    class Meta:
        model = Firm
        fields = ['total_decorators', 'total_profit']


##################################################### WALLRUS ADMIN SERIALIZERS ###################################################
class DesignListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ['id', 'name', 'is_customizable']


class DesignDetailSerializer(serializers.ModelSerializer):
    tags = UploadDesignTagSerializer(many=True)
    applications = ApplistSerializer(many=True)
    colorway_set = ColowaySerializer(many=True)

    class Meta:
        model = Design
        fields = ['id', 'name', 'tags', 'is_customizable',
                  'applications', 'colorway_set']


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['created_at', 'title', 'category', 'slug']


class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']


class NewArtistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email']


class NewPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']


class OrderListSerializer(serializers.ModelSerializer):
    order_cost = serializers.SerializerMethodField()

    def get_order_cost(self, obj):
        order_cost = 0
        for item in obj.items.all():
            order_cost += item.product.cost * item.quantity
        return order_cost

    class Meta:
        model = Order
        fields = ['id', 'order_cost']


class ItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.product.get_display_image()

    def get_name(self, obj):
        return f'{obj.product.design.name}.{obj.product.colorway.name}.{obj.product.application}'

    def get_cost(self, obj):
        return obj.product.cost

    class Meta:
        model = Item
        fields = ['image', 'name', 'cost', 'quantity', 'width', 'height']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'items']


class AdminArtistDetailSerializer(serializers.ModelSerializer):
    business_details = BusinessDetailSerializer()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username',
                  'business_details', 'address_set']


class UpdateArtistStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_active']


class UpdateDesignStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ['is_approved']


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['order', 'name']


class MonthlySalesSerializer(serializers.ModelSerializer):
    sales = serializers.SerializerMethodField()

    def get_sales(self, obj):
        order_cost = 0
        for item in obj.items.all():
            order_cost += item.product.cost * item.quantity
        return order_cost

    class Meta:
        model = Order
        fields = ['created_at', 'sales']


class MonthlyDecoratorCountSerializer(serializers.ModelSerializer):
    decorators_count = serializers.SerializerMethodField()

    def get_decorators_count(self, obj):
        return Interior_Decorator.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfDecorators=Count('user__date_joined')).order_by()

    class Meta:
        model = Interior_Decorator
        fields = ['decorators_count']


class MonthlyArtistCountSerializer(serializers.ModelSerializer):
    artists_count = serializers.SerializerMethodField()

    def get_artists_count(self, obj):
        return Artist.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfartists=Count('user__date_joined')).order_by()

    class Meta:
        model = Artist
        fields = ['artists_count']


class MonthlyBarChartSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        artists = Artist.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfartists=Count('user__date_joined')).order_by()
        decorators = Interior_Decorator.objects.filter(user__date_joined__date=obj[0]).values('user__date_joined__date').annotate(
            noOfDecorators=Count('user__date_joined')).order_by()
        return artists, decorators

    class Meta:
        model = Artist
        fields = ['count']

############################################# DECORATOR SERIALIZERS ###################################################################


class DecoratorSnippetSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()

    def get_level(self, obj):
        return obj.interior_decorator.level.get_name_display()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'level']


class FavouriteSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_artist(self, obj):
        return obj.design.get_artist_name()

    def get_image(self, obj):
        return obj.get_display_image()

    class Meta:
        model = Product
        fields = ['artist', 'image']


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.get_display_image()

    class Meta:
        model = Product
        fields = ['image']


class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    number_of_designs = serializers.SerializerMethodField()
    number_of_artists = serializers.SerializerMethodField()

    def get_number_of_designs(self, obj):
        designs = []
        for product in obj.products.all():
            if product.design not in designs:
                designs.append(product.design)
        return len(designs)

    def get_number_of_artists(self, obj):
        artists = []
        for product in obj.products.all():
            if product.design.artist not in artists:
                artists.append(product.design.artist)
        return len(artists)

    class Meta:
        model = Collection
        fields = ['name', 'products',
                  'number_of_designs', 'number_of_artists']


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.product.get_display_image()

    def get_name(self, obj):
        return f'{obj.product.design.name}.{obj.product.colorway.name}.{obj.product.application}'

    def get_cost(self, obj):
        return obj.product.cost

    def get_artist(self, obj):
        return obj.product.design.artist.first_name + ' ' + obj.product.design.artist.last_name

    class Meta:
        model = Item
        fields = ['image', 'name', 'cost',
                  'quantity', 'width', 'height', 'artist']


class MyOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    order_status = serializers.SerializerMethodField()

    def get_order_status(self, obj):
        return obj.order_status.all().order_by('-timestamp').first().name

    class Meta:
        model = Order
        fields = ['items', 'order_status']
