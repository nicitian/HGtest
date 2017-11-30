from shouzhuan.const import Const
def generate_constraint(name,prefix):
    print '%s_constraint=(' %name
    for k in Const:
        if k.startswith(prefix):
            print "    (Const['%s'],'%s'),"%(k,k)
    print ')'
    print

def model_constraint():
    generate_constraint('verify','model.verify.')
    generate_constraint('platform','model.platform.')
    generate_constraint('record','model.record.')
    generate_constraint('task_type','model.task.type.')
    generate_constraint('return_type','model.task.return_type.')
    generate_constraint('task_status','model.task.status.')
    generate_constraint('order_type','model.order.type.')
    generate_constraint('order_status','model.order.status.')
    generate_constraint('device','model.device.')
    generate_constraint('appeal_status','model.appeal.status.')
    generate_constraint('appeal_progress_source','model.appeal.progress.source.')
    generate_constraint('withdraw','model.withdraw.type.')
    
model_constraint()