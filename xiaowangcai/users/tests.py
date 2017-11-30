from django.test import TestCase

from users.models import User

# Create your tests here.
class UserTestCase(TestCase):
    def test_set_user_buyer_level(self):
        users={
            1:[User(buyer_orders=0),
               User(buyer_orders=1),
               User(buyer_orders=2),
               User(buyer_orders=25),
               User(buyer_orders=48),
               User(buyer_orders=49)],
            2:[User(buyer_orders=50),
               User(buyer_orders=51),
               User(buyer_orders=75),
               User(buyer_orders=120),
               User(buyer_orders=148),
               User(buyer_orders=149)],
        }
        for level in users:
            for u in users[level]:
                u.set_user_level('b')
                self.assertEqual(level, u.buyer_level,'orders:%d ,level:%d ,should:%d'%(u.buyer_orders,u.buyer_level,level))