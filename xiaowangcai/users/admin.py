from django.contrib import admin

from users.models import Blacklist, Record, Smscaptcha

from .models import User, TBAccount, Bankcard


# Register your models here.
admin.site.register(User)
admin.site.register(TBAccount)
admin.site.register(Bankcard)
admin.site.register(Blacklist)
admin.site.register(Record)
admin.site.register(Smscaptcha)
