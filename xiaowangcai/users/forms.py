# encoding: utf-8
from django import forms
from django.core.validators import RegexValidator
from users.models import TBAccount, Bankcard

phoneValidator=RegexValidator(regex='\d{11}')
idcValidator=RegexValidator(regex='\d{17}.')

class SignupForm(forms.Form):
    phone=forms.CharField(label='手机号码',max_length=11,validators=[phoneValidator,])
    captcha=forms.CharField(label='验证码',max_length=6)
    password=forms.CharField(label='密码',max_length=32,
                             widget=forms.PasswordInput())
    inviter=forms.CharField(label='邀请人ID',max_length=10,required=False)
    qq=forms.CharField(label='QQ', max_length=20, required=False)

class IdcForm(forms.Form):
    idc_name = forms.CharField(label='姓名', max_length=32)
    #idc_number = forms.CharField(label='身份证号码', max_length=18, validators=[idcValidator])
    idc_photo1 = forms.CharField( max_length=255)
    idc_photo2 = forms.CharField( max_length=255)

class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=45)
    password = forms.CharField(label='密码',max_length=32,widget=forms.PasswordInput())
    persistent = forms.IntegerField(required=False)

class TBAccountForm(forms.ModelForm):
    class Meta:
        model = TBAccount
        exclude = ['status', 'user','verify_time','today_receive_orders','verify_admin','create_time','is_frozen','frozen_start_datetime','frozen_days', 'place']

class BankcardForm(forms.ModelForm):
    class Meta:
        model = Bankcard
        exclude = ['user','verify_status','verify_time','verify_admin','create_time']
        
class ImageUploadForm(forms.Form):
    image = forms.FileField()