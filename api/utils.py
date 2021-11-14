import random
import string
from cryptography.fernet import Fernet
from decouple import config
import twilio
from twilio.rest import Client
from product.models import Product
import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
from backend import settings
from django.core.mail import send_mail

def random_password_generator():
    password = ''
    for x in range(0, 6):
        password += random.choice(string.ascii_uppercase) + random.choice(
            string.ascii_lowercase) + random.choice(string.digits) + random.choice(string.punctuation)

    return password


class Encrypt_and_Decrypt:
    def __init__(self):
        self.key = config("key")
        self.fernet = Fernet(self.key)

    def encrypt(self, msg):
        encMessage = self.fernet.encrypt(bytes(str(msg), 'utf-8'))
        return encMessage.decode('utf-8')

    def decrypt(self, msg):
        msg = bytes(msg, 'utf-8')
        decMessage = self.fernet.decrypt(msg)
        return decMessage.decode('utf-8')


def get_tags_by_label(tag_model, label):
    return [{'name': tag.name}
            for tag in tag_model.objects.filter(label=label)]


# class Encrypt_and_Decrypt:
#     def __init__(self):
#         pass
#     def randomword(self, length):
#         s=string.ascii_lowercase+string.digits
#         return ''.join(random.sample(s,length))
#     def encrypt(self,msg):
#         message_bytes = str(msg).encode('ascii')
#         base64_bytes = base64.b64encode(message_bytes)
#         base64_message = base64_bytes.decode('ascii')
#         enc_data=self.randomword(10)+base64_message+self.randomword(10)
#         return enc_data
#     def decrypt(self,msg):
#         base64_message = str(msg[10:-10:])
#         base64_bytes = base64_message.encode('ascii')
#         message_bytes = base64.b64decode(base64_bytes)
#         message = message_bytes.decode('ascii')
#         return message

def send_otp(phone_number,message):
    account_sid=config("ACCOUNT_SID")
    auth_token=config("AUTH_TOKEN")
    print(account_sid)
    try:
        client = twilio.rest.Client(account_sid, auth_token)

        message = client.messages.create(
            body=message,
            to=f'{phone_number}',
            from_=config("SMS_NUMBER")
        )
        print(message.sid)
    except:
        print('Error')

def send_mail_otp(mail_id,message):
    # message = Mail(
    #     from_email='from_email@example.com',#mailid
    #     to_emails=mail_id,
    #     subject='Wallrus Verification Code',
    #     html_content=f'<strong>Hii ! Your Verication Code for Login to Wallrus is {code}</strong>')

    # sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
    # response = sg.send(message)
    # print(response.status_code, response.body, response.headers)
    mail_subject = "One Time Password"
    to_email = str(mail_id)
    print(to_email,to_email,settings.EMAIL_HOST_USER)
    send_mail(subject=mail_subject,message=message,from_email=settings.EMAIL_HOST_USER,recipient_list=[to_email, ],fail_silently=False)
    return True

def code_gen():
    number_list =[x for x in range(10)]
    code_items=[]
    for i in range(5):
        num =random.choice(number_list)
        code_items.append(num)
    code_string ="".join(str(items) for items in code_items)
    return code_string