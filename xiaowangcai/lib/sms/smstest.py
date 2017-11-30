# encoding: utf-8
from CCPRestSDK import SMSService

#     这是请求的URL：
#     https://sandboxapp.cloopen.com:8883/2013-12-26/Accounts/8a48b5514e0b153e014e191131a106ca/SMS/TemplateSMS?sig=72EF04EFDFF59A0F18E54D7599CCEE9E
#     这是请求包体:
#     {"to": "15267001072", "datas": ["helloworld","10",], "templateId": "1", "appId": "8a48b5514e0b153e014e191181b806cd"}
#     这是响应包体:
#     {"templateSMS":{"dateCreated":"20150622112858","smsMessageSid":"201506221128583955827"},"statusCode":"000000"}
#     ********************************
#     smsMessageSid:201506221128583955827
#     dateCreated:20150622112858
#     statusCode:000000

result=SMSService.sendTemplateSMS('13592643118', ['helloworld','10'], 89306)
for k,v in result.iteritems():
    if k=='templateSMS': 
        for k,s in v.iteritems():
            print '%s:%s' % (k, s) 
    else: 
        print '%s:%s' % (k, v) 