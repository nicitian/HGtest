from django.test import TestCase
from tasks import views
from tasks.models import Task
from shouzhuan.utils import *
from datetime import *

# Create your tests here.
class TaskTest(TestCase):
	def test(self):
		#self.assertEqual(get_stamp_by_datetime(datetime.utcnow()), msec_time())
		task=Task.objects.get(pk='8357382')
		self.assertFalse(task==None)
		task.verify_status=Const['model.task.status.need_payment']
		task.publish_start_date=date(2015, 10, 8)
		task.publish_start_time=time(10, 15, 00)
		task.publish_end_time=time(23,15,00)
		task.publish_num=10
		#task.save()
		views._generate_task_order(task)