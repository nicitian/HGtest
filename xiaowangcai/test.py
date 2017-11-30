# coding=utf-8
import json
from decimal import *
d = Decimal('100')
d = d.quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)
print d

commodities = '[{"name": "\u7d20\u8bf4 2016\u590f\u88c5\u65b0\u6b3e\u6f6e\u97e9\u7248\u663e\u7626\u54c8\u4f26\u88e4\u5973\u4f11\u95f2\u897f\u88c5\u88e4\u4e5d\u5206\u5c0f\u811a\u88e4\u5b50", "url": "https://item.taobao.com/item.htm?spm=a1z10.3-c.w4002-14151064745.31.zwynxw&id=531656012254", "num": 1, "displayprice": "79", "pic_path": "http://upload.shouzhuanvip.com/FgzBlTToE9wc1Rhp52GbfnipwkSY", "unitprice": "79"}, {"name": "\u7d20\u8bf4 2016\u9ad8\u7aef\u5b9a\u5236\u767e\u642d\u73cd\u73e0\u914d\u9970\u88d9\u88e4\u659c\u8fb9\u4e0d\u5bf9\u79f0\u522b\u9488\u534a\u8eab\u88d9\u88d9\u88e4\u5973", "url": "https://item.taobao.com/item.htm?spm=a1z10.3-c.w4002-14151064745.40.zwynxw&id=531341884622", "num": 1, "displayprice": "99", "pic_path": "http://upload.shouzhuanvip.com/FpN5bOSYv9if-jEM4-74No2jFJy5", "unitprice": "99"}, {"name": "\u7d20\u8bf4 2016\u590f\u88c5\u65b0\u6b3e\u6f6e\u97e9\u7248\u4e2d\u8896\u6761\u7eb9\u5bbd\u677e\u8759\u8760\u8896\u7eaf\u68c9\u5706\u9886T\u6064\u6253\u5e95\u886b", "url": "https://item.taobao.com/item.htm?spm=a1z10.3-c.w4002-14151064745.55.zwynxw&id=531602839529", "num": 1, "displayprice": "49", "pic_path": "http://upload.shouzhuanvip.com/FoMnkUI63dBhchFaKScIo3enaVkR", "unitprice": "49"}]'
def dianzi():
        return reduce(lambda a, b: a + b, map(lambda a: Decimal(a["unitprice"]) * Decimal(a["num"]),
                                              json.loads(commodities)))

print dianzi()

