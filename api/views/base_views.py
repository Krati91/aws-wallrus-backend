from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from users.models import CustomUser, Code
from user_details.models import Address, BankDetail, BusinessDetail
from product.models import Application
from django.contrib.auth import update_session_auth_hash
from ..serializers import *

from ..utils import Encrypt_and_Decrypt, send_mail_otp, send_otp, code_gen


class CustomUserCreate(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        print(request.data)

        fullname = request.data['fullNameKey'].split(' ')
        # firm = request.data.get('registered_firm', None)
        type = ['Artist', 'Interior Decorator', 'Organization']

        data = {}
        data['email'] = request.data['emailKey']
        data['password'] = request.data['passwordKey']
        data['type'] = type.index(request.data['accountTypeKey']) + 1
        data['profile_picture'] = request.data['profilePicKey']
        data['first_name'] = fullname[0]
        data['last_name'] = fullname[1] if len(fullname) >= 2 else ''
        data['username'] = request.data['userNameKey']
        data['phone'] = request.data['phoneNumberKey']
        data['bio'] = request.data['bioKey']

        # TO DO
        # personal_address = {}
        # business_address = {}

        # add_type = ['Personal Address', 'Office Address']

        # Create a new user
        reg_serializer = RegisterUserSerializer(data=data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            if new_user:

                # Create business details
                business_details = {
                    'user': new_user.pk,
                    'pan_card_number': request.data['panKey'],
                    'brand_name': request.data['organizationKey'],
                    'gst_number': request.data['gstKey'],
                    'phone': request.data['phoneNumberBusinessKey'],
                    'email': request.data['emailBusinessKey']
                }

                buss_serializer = BusinessDetailSerializer(
                    data=business_details)
                if buss_serializer.is_valid():
                    new_buss_details = buss_serializer.save()
                    if new_buss_details:
                        # To Do add business and personal address
                        personal_address = {
                            'user': new_user.pk,
                            'type': 1,
                            'line1': request.data['addressStreetAboutyouKey'],
                            'line2': request.data['addressApartmentAboutyouKey'],
                            'city': request.data['addressCityAboutyouKey'],
                            'pincode': request.data['addressPincodeAboutyouKey'],
                            'state': request.data['stateAboutyouKey']

                        }
                        business_address = {
                            'user': new_user.pk,
                            'type': 2,
                            'line1': request.data['addressStreetBusinessKey'],
                            'line2': request.data['addressApartmentBusinessKey'],
                            'city': request.data['cityBusinessKey'],
                            'pincode': request.data['pincodeBusinessKey'],
                            'state': request.data['stateBusinessKey']

                        }
                        bussadd_serializer = AddressSerializer(
                            data=business_address)
                        peradd_serializer = AddressSerializer(
                            data=personal_address)
                        print(bussadd_serializer)
                        print(peradd_serializer)
                        if peradd_serializer.is_valid():
                            if bussadd_serializer.is_valid():
                                bussadd_serializer.save()
                                peradd_serializer.save()

                else:
                    print(str(buss_serializer.errors))
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                # if account details were sent create bank details
                if request.data['accountNumberKey']:
                    bank_details = {
                        'user': new_user.pk,
                        'account_number': request.data['accountNumberKey'],
                        'name': request.data['bankNameKey'],
                        'branch': request.data['bankBranchKey'],
                        'swift_code': request.data['swiftCodeKey'],
                        'ifsc_code': request.data['ifscCodeKey']
                    }

                    bank_serializer = BankDetailSerializer(
                        data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                    else:
                        print(str(bank_serializer.errors))
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                return Response({'message': 'Thank you for signing up. Your profile is under review.'},
                                status=status.HTTP_201_CREATED)

        print(str(reg_serializer.errors))
        return Response(status=status.HTTP_400_BAD_REQUEST)


class Edit_Detail(APIView):
    '''
    Edit Detail
    '''
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, user_id, model_name, type=1):
        if model_name == Address:
            return model_name.objects.filter(user=user_id, type=type).first()
        return model_name.objects.get(user=user_id)

    def get(self, request, user_id=None, format=None):
        id = request.user.id
        en = Encrypt_and_Decrypt()
        if CustomUser.objects.filter(pk=id, is_active=True).exists():
            user_Businessinfo = self.get_object(id, BusinessDetail)
            user_Basicinfo = CustomUser.objects.get(pk=id)
            user_peradd = self.get_object(id, Address)
            user_busiadd = self.get_object(id, Address, type=2)
            serializer_buss = BusinessDetailSerializer(
                instance=user_Businessinfo)
            serialize_user_basic = RegisterUserSerializer(
                instance=user_Basicinfo)
            serializer_peraddress = AddressSerializer(instance=user_peradd)
            serializer_busiaddress = AddressSerializer(instance=user_busiadd)
            try:
                user_Bankinfo = self.get_object(id, BankDetail)
                serialize_bank = BankDetailSerializer(instance=user_Bankinfo)
                serializer = {'Business_Info': serializer_buss.data,
                              'User_Info': serialize_user_basic.data,
                              'User_Personal_Add_Info': serializer_peraddress.data,
                              'User_Business_Add_Info': serializer_busiaddress.data,
                              'Bank_Info': serialize_bank.data}
                serializer['Bank_Info']['swift_code'] = en.decrypt(
                    serializer['Bank_Info']['swift_code'])
                serializer['Bank_Info']['account_number'] = en.decrypt(
                    serializer['Bank_Info']['account_number'])
            except:
                serializer = {'Business_Info': serializer_buss.data,
                              'User_Info': serialize_user_basic.data, 'User_Personal_Add_Info': serializer_peraddress.data, 'User_Business_Add_Info': serializer_busiaddress.data}
            serializer['Business_Info']['pan_card_number'] = en.decrypt(
                serializer['Business_Info']['pan_card_number'])
            serializer['Business_Info']['gst_number'] = en.decrypt(
                serializer['Business_Info']['gst_number'])
            del serializer['Business_Info']['user']
            del serializer['User_Personal_Add_Info']['user']
            del serializer['User_Business_Add_Info']['user']
            if 'Bank_Info' in serializer:
                del serializer['Bank_Info']['user']
            del en
            return Response(serializer, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'User Doesnot exist'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        print(request.data)
        id = request.user.id
        en = Encrypt_and_Decrypt()
        user_personal = CustomUser.objects.get(pk=id)
        fullname = request.data['fullName'].split(' ')
        data = {}
        if request.data['profilePic'] == '':
            data['profile_picture'] = user_personal.profile_picture
        else:
            data['profile_picture'] = request.data['profilePic']
        data['email'] = user_personal.email
        data['password'] = user_personal.password
        data['type'] = user_personal.type
        data['first_name'] = fullname[0]
        data['last_name'] = fullname[1] if len(fullname) >= 2 else ''
        data['username'] = request.data['userName']
        data['phone'] = request.data['phoneNumber']
        data['bio'] = request.data['bio']
        reg_serializer = RegisterUserSerializer(user_personal, data=data)
        if reg_serializer.is_valid():
            user_status = reg_serializer.save()
            if user_status:
                # Update business details
                buis_detail = BusinessDetail.objects.filter(
                    user=user_personal).first()
                business_details = {
                    'user': user_status.pk,
                    'pan_card_number': en.encrypt(request.data['pan']),
                    'brand_name': request.data['organization'],
                    'gst_number': en.encrypt(request.data['gst']),
                    'phone': request.data['phoneNumberBusiness'],
                    'email': request.data['emailBusiness']
                }
                print(business_details)
                buss_serializer = BusinessDetailSerializer(
                    buis_detail, data=business_details)
                if buss_serializer.is_valid():
                    new_buss_details = buss_serializer.save()
                    if new_buss_details:
                        # To Do add business address
                        buis_add_inst = Address.objects.filter(
                            user=user_personal, type=2).first()
                        pers_add_inst = Address.objects.filter(
                            user=user_personal, type=1).first()
                        business_address = {
                            'user': user_status.pk,
                            'type': 2,
                            'line1': request.data['addressStreetBusiness'],
                            'line2': request.data['addressApartmentBusiness'],
                            'city': request.data['cityBusiness'],
                            'pincode': request.data['pincodeBusiness'],
                            'state': request.data['stateBusiness']

                        }
                        personal_address = {
                            'user': user_status.pk,
                            'type': 1,
                            'line1': request.data['addressStreetAboutyou'],
                            'line2': request.data['addressApartmentAboutyou'],
                            'city': request.data['addressCityAboutyou'],
                            'pincode': request.data['addressPincodeAboutyou'],
                            'state': request.data['stateAboutyou']

                        }
                        # print(business_address)
                        # bussadd_serializer = AddressSerializer(
                        #     buis_add_inst, data=business_address)
                        # print(bussadd_serializer)
                        # if bussadd_serializer.is_valid():
                        #     bussadd_serializer.save()
                        #     print(bussadd_serializer.save())
                        bussadd_serializer = AddressSerializer(
                            buis_add_inst, data=business_address)
                        peradd_serializer = AddressSerializer(
                            pers_add_inst, data=personal_address)
                        if peradd_serializer.is_valid():
                            if bussadd_serializer.is_valid():
                                bussadd_serializer.save()
                                peradd_serializer.save()

                else:
                    print(str(buss_serializer.errors))
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                Acc_no = en.encrypt(request.data['accountNumber'])
                swift_code = en.encrypt(request.data['swiftCode'])
                # if account details were sent create bank details
                if BankDetail.objects.filter(user=user_personal).first():
                    bank_acc_detail = BankDetail.objects.filter(
                        user=user_personal).first()

                    bank_details = {
                        'user': user_status.pk,
                        'account_number': Acc_no,
                        'name': request.data['bankName'],
                        'branch': request.data['bankBranch'],
                        'swift_code': swift_code,
                        'ifsc_code': request.data['ifscCode']
                    }
                    bank_serializer = BankDetailSerializer(
                        bank_acc_detail, data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                    else:
                        print(str(bank_serializer.errors))
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    bank_details = {
                        'user': user_status.pk,
                        'account_number': request.data['accountNumber'],
                        'name': request.data['bankName'],
                        'branch': request.data['bankBranch'],
                        'swift_code': request.data['swiftCode'],
                        'ifsc_code': request.data['ifscCode']
                    }
                    bank_serializer = BankDetailSerializer(data=bank_details)
                    if bank_serializer.is_valid():
                        bank_serializer.save()
                del en
                return Response({'message': 'Thank you for Updating !!'},
                                status=status.HTTP_201_CREATED)

        print(str(reg_serializer.errors))
        return Response(status=status.HTTP_400_BAD_REQUEST)


class NotificationSettings(APIView):
    '''
    For the notification settings of a user
    '''
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, user_type_notification_model, user):
        user = get_object_or_404(CustomUser, is_active=True, email=user)
        return get_object_or_404(user_type_notification_model, user=user.id)

    def get(self, request):
        serializer = None
        obj = None
        if request.user.get_type_display() == 'Artist':
            obj = self.get_object(ArtistNotificationSettings, request.user)
            serializer = ArtistNotificationSettingsSerailizer(instance=obj)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = None
        obj = None
        if request.user.get_type_display() == 'Artist':
            obj = self.get_object(ArtistNotificationSettings, request.user)
            serializer = ArtistNotificationSettingsSerailizer(
                instance=obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, partial=True)
        try:
            if request.data["password1"] and request.data["password2"] and request.data['password']:
                pass
        except:
            return Response({"Password": ["Error (Password Field is empty)"]},
                            status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            old_password = serializer.data.get("password")
            print(self.object.check_password(old_password))
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)

            else:
                if request.data["password1"] == request.data["password2"] and request.data["password"] == request.data["password1"]:
                    return Response({"New Password": ["Same as Old Password"]},
                                    status=status.HTTP_400_BAD_REQUEST)

                elif request.data["password1"] == request.data["password2"]:
                    self.object.set_password(request.data["password1"])
                    self.object.save()
                    return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppList(APIView):
    '''
    Fetch List of Applications
    '''

    def get(self, request):
        list = Application.objects.filter(is_active=True)
        serializer = ApplistSerializer(instance=list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserTypeView(APIView):
    '''
    User Type
    '''
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, user_id=None, format=None):
        user_Basicinfo = CustomUser.objects.get(pk=request.user.id)
        serializer_type = UserTypeSerializer(instance=user_Basicinfo)
        return Response(data=serializer_type.data, status=status.HTTP_200_OK)


class VerifyUserView(APIView):
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        OTP = request.data["OTP"]
        code = Code.objects.get(user=user)
        if str(code.number) == OTP:
            code.save()
            return Response(data="VERIFIED", status=status.HTTP_200_OK)
        else:
            return Response(data="NOT VERIFIED", status=status.HTTP_401_UNAUTHORIZED)


class SendOTPView(APIView):
    # authentication_classes=[BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = CustomUser.objects.get(pk=request.user.id)
        choice = request.data["choice"]
        email = user.email
        Code.objects.get(user=user).save()
        code = Code.objects.get(user=user).number
        phone_number = user.phone
        if choice == 'mobile':
            msg = 'Hii ! Your Verication Code for Login to Wallrus is ' + \
                str(code)+'.'
            send_otp(phone_number, msg)
            return Response(data="OTP Sent", status=status.HTTP_200_OK)
        elif choice == 'mail':
            msg = "Hii ! Your Verication Code for Login to Wallrus is " + code + "."
            send_mail_otp(email, msg)
            return Response(data="OTP Sent", status=status.HTTP_200_OK)


class EmailPhoneView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        choice = request.data["choice"]
        value = request.data["value"]
        code = code_gen()
        if choice == 'sms':
            msg = 'Hii ! Your Verication Code for Login to Wallrus is ' + \
                str(code)+'.'
            send_otp(value, msg)
            return Response(data=code, status=status.HTTP_200_OK)
        elif choice == 'email':
            msg = "Hii ! Your Verication Code for Login to Wallrus is " + \
                str(code) + "."
            send_mail_otp(value, msg)
            return Response(data=code, status=status.HTTP_200_OK)
