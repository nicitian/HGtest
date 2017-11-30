from django.contrib import admin


from .models import Task, Store, Order, Appeal, AppealType,StoreRecentBuyer


# Register your models here.
admin.site.register(Store)
admin.site.register(Task)
admin.site.register(Order)
admin.site.register(Appeal)
admin.site.register(AppealType)
admin.site.register(StoreRecentBuyer)
