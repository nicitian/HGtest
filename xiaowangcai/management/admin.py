from django.contrib import admin
from management.models import Recharge, Notice, Administrator, Withdraw

# Register your models here.
admin.site.register(Administrator)
admin.site.register(Recharge)
admin.site.register(Withdraw)
admin.site.register(Notice)