from django import forms

from management.models import Recharge, Notice


class RechargeForm(forms.ModelForm):
    class Meta:
        model = Recharge
        fields  = ['amount', 'bank_name','account_name']

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        exclude = ['create_time','publish_admin','update_time','important']