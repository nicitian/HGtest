# encoding: utf-8
from tasks.models import AppealType

AppealType.objects.create(pk=1,description='返款问题')
AppealType.objects.create(pk=2,description='商品错误')
AppealType.objects.create(pk=3,description='快递问题')
AppealType.objects.create(pk=4,description='其他问题')
AppealType.objects.create(pk=5,description='取消')
AppealType.objects.create(pk=6,description='买手做任务问题')
AppealType.objects.create(pk=7,description='买手确认收货好评问题')
