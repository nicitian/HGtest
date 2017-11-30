# encoding: utf-8
from decimal import Decimal

Const = {
    # 数据库模型编码#
    # 审核状态
    'model.verify.need_check': 0,
    'model.verify.check_pass': 1,
    'model.verify.check_deny': 2,

    # 用户flags状态位
    'model.user.flags.frezen': 1,  # 管理员拉黑某一用户
    'model.user.flags.normal': 0,  # 用户状态正常
    # 账户交易记录类型
    'model.record.pricipal': 0,   # 本金
    'model.record.commission': 1,  # 佣金

    'model.record.category.promote': 1,
    'model.record.category.recharge': 2,
    'model.record.category.principalreturn': 4,
    'model.record.category.signup': 5,
    'model.record.category.principalwithdraw': 6,
    'model.record.category.commissionwithdraw': 7,
    'model.record.category.taskpay': 8,
    'model.record.category.join': 9,  # 注册奖励, 针对没有推荐人的, 有推荐人的将在第一单垫资任务完成后

    # 平台
    'model.platform.taobao': 0,

    # 任务类型
    'model.task.type.mobile_taobao': 0,
    'model.task.type.pc_taobao': 1,
    'model.task.type.flow': 2,
    'model.task.type.special': 3,

    # 任务返款
    'model.task.return_type.platform': 0,
    'model.task.return_type.seller': 1,

    # 任务状态
    'model.task.status.need_payment': 0,
    'model.task.status.in_progress': 1,
    'model.task.status.closed': 2,
    'model.task.status.cancel': 3,
    'model.task.status.frozen': 4,

    # 订单类型
    'model.order.type.normal': 0,  # 普通刷单好评订单
    'model.order.type.keyword': 1,  # 关键词好评
    'model.order.type.image': 2,  # 图片好评
    'model.order.type.flow': 3,  # 流量任务
    'model.order.type.collect': 4,  # 收藏、加购物车任务
    'model.order.type.direct': 5,  # 直通车任务
    'model.order.type.advance': 6,  # 高级组合任务
    'model.order.type.max': 6,

    'model.ordergtype.comment': 1,  # 好评单
    'model.ordergtype.flow': 2,  # 流量单
    'model.ordergtype.collect': 3,  # 收藏单

    # 订单状态
    # 共同状态
    'model.order.status.init': 0,  # 未接单
    'model.order.status.received': 1,  # 已接单,待操作
    'model.order.status.seller_request_cancel': 2,  # 商家请求撤销
    'model.order.status.buyer_request_cancel': 3,  # 买手请求撤销
    'model.order.status.cancel': 2,  # 已撤销
    'model.order.status.completed': 10,  # 已完成
    'model.order.status.comment': 105,  # 待确认
    # 刷单订单
    'model.order.status.step1': 100,  # 已货比三家...
    'model.order.status.step2': 101,
    'model.order.status.step3': 102,  # 待返款
    'model.order.status.returnmoney': 103,  # 卖家已还款
    'model.order.status.deliver': 104,  # 已发货
    'model.order.status.affirm': 106,  # 已确认
    'model.order.status.step9': 107,  # 高级任务已浏览
    # 流量订单

    # 提醒
    'model.remind.evaluated': 0,
    'model.remind.appeal': 1,
    'model.remind.idc_verify': 2,
    'model.remind.bankcard_verify': 3,
    'model.remind.buyer_orders': 4,
    'model.remind.principal': 5,
    'model.remind.store_verify': 6,
    'model.remind.tb_verify': 7,
    'model.remind.commission': 8,
    'model.remind.no_money': 9,
    'model.remind.received': 10,
    'model.remind.flowReceived': 11,

    # 申诉
    'model.appeal.status.in_progress': 1,  # 进行中
    'model.appeal.status.closed': 2,  # 已完结

    # 申诉进程来源
    'model.appeal.progress.source.complainant': 1,  # 申诉人
    'model.appeal.progress.source.respondent': 2,  # 被申诉人
    'model.appeal.progress.source.platform': 3,  # 平台

    # 设备
    'model.device.unknown': 0,
    'model.device.android': 1,
    'model.device.ios': 2,
    'model.device.pc': 3,

    # 公告
    'model.notice.type.seller': 0,
    'model.notice.type.buyer': 1,

    # 提现
    'model.withdraw.type.principal': 0,
    'model.withdraw.type.commission': 1,

    # 报表
    'model.dailyreport.type.new_order_num': 1,
    'model.dailyreport.type.new_order_payment': 2,
    'model.dailyreport.type.finish_order_num': 3,
    'model.dailyreport.type.finish_order_payment': 4,
    'model.dailyreport.type.signup': 5,
    'model.dailyreport.type.promote': 6,
    'model.dailyreport.type.recharge': 7,
    'model.dailyreport.type.principal_withdraw': 8,
    'model.dailyreport.type.commission_withdraw': 9,
    'model.dailyreport.type.profit': 10,

    ##
    # 接口返回码#
    'code.success': 0,
    'code.request_error': -101,
    'code.system_error': -102,
    'code.username_exist': -103,
    'code.sms_error': -104,
    'code.inviter_not_exist': -105,
    'code.login_error': -106,
    'code.login_password_error': -107,
    'code.permission_deny': -110,
    'code.file.exceed.size': -111,
    'code.image.unknown.type': -112,
    'code.order.has.been.received': -113,
    'code.today.receive.orders.exceed': -114,
    'code.receive.time.error': -115,
    'code.password_error': -116,
    'code.user_not_exists': -117,
    'code.receive.in.blacklist': -118,
    'code.award.already.receive': -119,
    'code.amount.exceed': -120,
    'code.recent.buyer': -121,
    'code.store.exist': -122,
    'code.tbaccount.exist': -123,
    'code.insufficient.balance': -124,
    'code.tbaccount.exceed': -125,
    'code.bankcard.repeat': -126,
    'code.user.nonexists': -127,
    'code.order.steperror': -128,
    'code.order.unsupportaction': -129,
    'code.order.steplocked': -130,
    'code.order.uncancelable': -131,
    'code.login_accountlocked': -132,
    'code.notdelete.data': -133,
    'code.idc_verify.error': -134,
    'code.order.frozen': -135,
    'code.global.client_unsupport': -999,

    # 代码部分参数#
    'const.msperminute': 60000,
    'sms.valid.time': 10,
    'session.persistent.time': 2592000,
    'paginator.num': 10,
    'file.max.size': 5242880,  # 5MB
    'max.receive.ordersperday': 4,
    'total.lock.number': 1000,
    'notice.new.timedelta': 864000000,
    'ms.per.minute': 60000,
    'ms.per.hour': 3600000,
    'ms.per.day': 86400000,
    'ms.per.year': 31536000000L,
    'min.award': 0.01,
    'max.award': 0.15,
    'inviter.buyer.award': 8,
    'common.join.award': 8,
    'inviter.seller.award.ratio': Decimal('0.03'),
    'inviter.buyer.award.ratio': Decimal('0.05'),

    'qiniu.ak': 'jZxX75tMz4ql-aUBWikWO3FeBtvC6REtNSAJXrJJ',
    'qiniu.sk': 'Ge2dMG4tP1kYuFOdeqMTNE0lFuWpdjAJ-KAKBEvf',
    'qiniu.domain': 'http://upimg.shouzhuanvip.com/',
    'qiniu.workspace': 'shouzhuan',
    'qiniu.maxage': 7200,  # 秒
    'qiniu.safe': 60,

    #     'qiniu.ak':'CpvJv24NrovNCbsE4ow83yk--h7nrGllGFPvS7I2',
    #     'qiniu.sk':'gI5XGAIoEgc9Wvo8rhQMVZlOMoWxIGFXSw_biKNP',
    #     'qiniu.domain':'7xrkav.com1.z1.glb.clouddn.com',
    #     'qiniu.workspace':'shouzhuanvip',
    #     'qiniu.maxage':7200, #秒
    #     'qiniu.safe':60,

    #
    'app.order.type.mobile_tb': 0,
    'app.order.type.pc_tb': 1,
    'app.order.type.mobile_scan': 2,
    'app.order.type.mobile_tm': 3,
    'app.order.type.special': 4,
    # 等级
    # 'seller.level.limit':[100,300,500,1000,2000],
    # 'buyer.level.limit':[50,150,300,500,750],
    'seller.level.limit': [1000000000000, 2000000000000, 3000000000000, 4000000000000, 5000000000000],
    'buyer.level.limit': [1000000000000, 2000000000000, 3000000000000, 4000000000000, 5000000000000],

    # 商家支付
    'payment.commision.flow': Decimal('0.42'),  # 流量单
    'payment.commision.collect': Decimal('0.84'),  # 收藏单
    'payment.commision.direct': Decimal('0.3'),  # 直通车单
    'payment.commision.extra.keyword': Decimal('1'),  # 关键词好评额外佣金
    'payment.commision.extra.image': Decimal('3'),  # 图片好评额外佣金
    'payment.commision.base.deep': Decimal('1.0'),  # 隔天任务初始佣金
    'payment.commision.deep.step': Decimal('0.5'),  # 隔天任务 增长佣金

    # 各级商家别支付佣金。这里的级别是商品的价格的级别区间
    'payment.commision': {
        0: Decimal('6.5'),
        1: Decimal('7.5'),
        2: Decimal('8.0'),
        3: Decimal('8.5'),
        4: Decimal('10.5'),
        5: Decimal('12.5'),
        6: Decimal('15.5'),
        7: Decimal('18.5'),
        8: Decimal('22'),
        9: Decimal('27'),
        10: Decimal('36.5'),
        11: Decimal('46.5'),
        12: Decimal('57'),
        13: Decimal('67.5'),
        14: Decimal('78'),
        15: Decimal('90'),
        16: Decimal('110'),
        17: Decimal('135'),
        18: Decimal('160'),
    },
    'payment.commisionrate': Decimal('0.015'),

    'payment.fee.return': Decimal('0.8'),  # 平台返款服务费
    'payment.fee.multigood': Decimal('2'),  #

    # 买手获得
    # 各级别买手获得佣金。这里的级别是商品的价格的级别区间。
    'gain.commision': {
        0: Decimal('4.2'),
        1: Decimal('4.8'),
        2: Decimal('5.2'),
        3: Decimal('5.5'),
        4: Decimal('6.8'),
        5: Decimal('8.1'),
        6: Decimal('10.0'),
        7: Decimal('12.0'),
        8: Decimal('14.3'),
        9: Decimal('17.5'),
        10: Decimal('23.7'),
        11: Decimal('30.2'),
        12: Decimal('37.0'),
        13: Decimal('43.8'),
        14: Decimal('50.7'),
        15: Decimal('58.5'),
        16: Decimal('71.5'),
        17: Decimal('87.7'),
        18: Decimal('104'),
    },

    'gain.commisionrate': Decimal('0.00975'),

    'gain.commision.extra.keyword': Decimal('1'),  # 关键词好评额外佣金
    'gain.commision.extra.image': Decimal('3'),  # 图片好评额外佣金
    'gain.commision.flow': Decimal('0.27'),  # 流量单
    'gain.commision.collect': Decimal('0.54'),  # 收藏单
    'gain.commision.direct': Decimal('0.21'),  # 直通车单
    'gain.commision.base.deep': Decimal('0.65'),  # 隔天任务初始佣金
    'gain.commision.deep.step': Decimal('0.325'),  # 隔天任务 增长佣金

    'gain.commision.bonus.buyer.ratio': Decimal('0.65'),  # 加赏佣金刷手获得比例
    'gain.commision.bonus.plat.ratio': Decimal('0.35'),  # 加赏佣金平台获得比例
    # 平台盈利


    # user flags
    # 0-10 reserved, total 63
    'user.flags.locked': 2,
    'user.flags.supportfastreturn': 11,
    'user.flags.supportsellerrebate': 12,
    'user.flags.taskfreeverify': 13,
    'user.flags.joinawarded': 14,
}

ERRMSG = {
    'tasks.order_create': u'您已经接过该任务',
}

verify_constraint = (
    (Const['model.verify.need_check'], 'model.verify.need_check'),
    (Const['model.verify.check_deny'], 'model.verify.check_deny'),
    (Const['model.verify.check_pass'], 'model.verify.check_pass'),
)

platform_constraint = (
    (Const['model.platform.taobao'], 'model.platform.taobao'),
)

task_type_constraint = (
    (Const['model.task.type.special'], 'model.task.type.special'),
    (Const['model.task.type.pc_taobao'], 'model.task.type.pc_taobao'),
    (Const['model.task.type.mobile_taobao'], 'model.task.type.mobile_taobao'),
    (Const['model.task.type.flow'], 'model.task.type.flow'),
)

return_type_constraint = (
    (Const['model.task.return_type.seller'], 'model.task.return_type.seller'),
    (Const['model.task.return_type.platform'], 'model.task.return_type.platform'),
)

task_status_constraint = (
    (Const['model.task.status.in_progress'], 'model.task.status.in_progress'),
    (Const['model.task.status.need_payment'], 'model.task.status.need_payment'),
    (Const['model.task.status.closed'], 'model.task.status.closed'),
    (Const['model.task.status.cancel'], 'model.task.status.cancel'),
)

order_type_constraint = (
    (Const['model.order.type.collect'], 'model.order.type.collect'),
    (Const['model.order.type.keyword'], 'model.order.type.keyword'),
    (Const['model.order.type.normal'], 'model.order.type.normal'),
    (Const['model.order.type.flow'], 'model.order.type.flow'),
    (Const['model.order.type.direct'], 'model.order.type.direct'),
    (Const['model.order.type.image'], 'model.order.type.image'),
    (Const['model.order.type.advance'], 'model.order.type.advance'),
)

order_status_constraint = (
    (Const['model.order.status.deliver'], 'model.order.status.deliver'),
    (Const['model.order.status.cancel'], 'model.order.status.cancel'),
    (Const['model.order.status.comment'], 'model.order.status.comment'),
    (Const['model.order.status.completed'], 'model.order.status.completed'),
    (Const['model.order.status.step3'], 'model.order.status.step3'),
    (Const['model.order.status.step2'], 'model.order.status.step2'),
    (Const['model.order.status.step1'], 'model.order.status.step1'),
    (Const['model.order.status.step9'], 'model.order.status.step9'),
    (Const['model.order.status.affirm'], 'model.order.status.affirm'),
    (Const['model.order.status.seller_request_cancel'], 'model.order.status.seller_request_cancel'),
    (Const['model.order.status.received'], 'model.order.status.received'),
    (Const['model.order.status.init'], 'model.order.status.init'),
    (Const['model.order.status.returnmoney'], 'model.order.status.returnmoney'),
    (Const['model.order.status.buyer_request_cancel'], 'model.order.status.buyer_request_cancel'),
)

device_constraint = (
    (Const['model.device.unknown'], 'model.device.unknown'),
    (Const['model.device.ios'], 'model.device.ios'),
    (Const['model.device.android'], 'model.device.android'),
    (Const['model.device.pc'], 'model.device.pc'),
)

appeal_status_constraint = (
    (Const['model.appeal.status.closed'], 'model.appeal.status.closed'),
    (Const['model.appeal.status.in_progress'], 'model.appeal.status.in_progress'),
)

appeal_progress_source_constraint = (
    (Const['model.appeal.progress.source.respondent'], 'model.appeal.progress.source.respondent'),
    (Const['model.appeal.progress.source.complainant'], 'model.appeal.progress.source.complainant'),
    (Const['model.appeal.progress.source.platform'], 'model.appeal.progress.source.platform'),
)

withdraw_constraint = (
    (Const['model.withdraw.type.commission'], 'model.withdraw.type.commission'),
    (Const['model.withdraw.type.principal'], 'model.withdraw.type.principal'),
)
