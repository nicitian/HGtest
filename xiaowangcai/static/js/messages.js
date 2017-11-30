require.config({
	paths:{
		rongSDK: 'http://res.websdk.rongcloud.cn/RongIMClient-0.9.10.min',
		layer: '/static/js/lib/layer/layer',
	}
});
require(['jquery', 'rongSDK', 'laifu', 'layer'],
function($, RongIMClient, laifu, layer) {
	if(!window.localStorage){
		alert('浏览器版本过低，请使用chrome浏览器或IE8以上');
	}
	function Msg(userId,content,time,contentType,source) {
		this.userId = userId;
		this.content = content;
		this.time = time;
		this.contentType = contentType;
		this.source = source;
　　}
	function store_msg(msg){
		if(!msg instanceof Msg){
			return;
		}
		var userId=msg.userId;
		var msgs=localStorage[userId]?JSON.parse(localStorage[userId]):[];
		msgs.push(msg);
		localStorage[userId]=JSON.stringify(msgs);
	}
	function print_msg(msg){
		var dhtml;
		if(msg.source==0){
			dhtml='<li class="demo clearfix"><span class="triangle"></span><div class="article">'+msg.content+'</div><div class="sent-time">'+new Date(msg.time).Format('yyyy-MM-dd hh:mm:ss')+'</div></li>';
		}else{
			dhtml='<li class="demo clearfix fr"><span class="triangle right"></span><div class="article">'+msg.content+'</div><div class="sent-time">'+new Date(msg.time).Format('yyyy-MM-dd hh:mm:ss')+'</div></li>';
		}
		$('#chartct').append(dhtml);
	}
	function print_msgs(msgs){
		for(var i=0;i<msgs.length;i++){
			print_msg(msgs[i]);
		}
	}
	window.personList = $('#userlist');
	var addEnable=true;
    personList.nowSelected = -1;
    personList.flushPerson = function() {
    	delete personList.persons;
        personList.persons = $('.person');
    };
    personList.flushPerson();
    personList.selectSomebody = function(i) {
        with(personList) {
            if (i >= persons.size()) {
                return;
            }
            if(nowSelected>=0){
            	personList.persons.eq(nowSelected).removeClass('selected');
            }
            var person=personList.persons.eq(i);
            nowSelected = i;
            person.addClass('selected');
            var uid=person.data('user-id');
            $('#dtop').text(uid);
            $('#chartct').html('');
            var msgs=localStorage[uid]?JSON.parse(localStorage[uid]):[];
            var unread=person.find('.unread-msgs');
            var unreadNum=unread.find('.unread-num');
            unreadNum.text(0);
            unread.hide();
            print_msgs(msgs);
        }

    };
    personList.addSomebody = function(person) {
        personList.append('<li class="person" data-user-id="' + person.id + '" ><img class="person-photo" src="'+(person.photo?person.photo:'/static/image/web/user-default-photo.jpg')+'"/><div class="person-info"><span class="person-id">' + person.id + '</span><span class="unread-msgs">（<span class="unread-num">0</span>）</span></div></li>');
    	personList.flushPerson();
    };
    personList.get_now_user_id = function(){
    	with(personList){
    		if(nowSelected<0){
    			return -1;
    		}else{
    			return $(persons[nowSelected]).data('user-id');
    		}
    	}
    };
    personList.get_index_from_user_id = function(uid){
    	var index=-1;
    	$.each(personList.persons,function(i,e){
    		if(uid==$(e).data('user-id')){
    			index=i;
    			return;
    		}
    	});
    	return index;
    };
    personList.delegate('.person', 'click',
    function() {
    	with(personList){
    		selectSomebody(persons.index(this));
    	}
    });
    $('#bt-addnew').bind('click',
    function() {
        $('.bg-mask').show();
        $('#add-new-dialog').show();
    });
    $('#btn-add-cancel').bind('click',
    function() {
        $('.bg-mask').hide();
        $('#add-new-dialog').hide();
    });


    $('#btn-add-submit').bind('click',
    function() {
        var addNewId = $('#add-shouzhuan-id').val();
        var index = -1;
        if (!/[1-9][0-9]{4}/.test(addNewId)) {
            layer.msg("请输入正确的ID");
            return;
        }
        if(!addEnable){
        	return;
        }
        $.each(personList.persons,
        function(i, e) {
            if ($(e).data('user-id') == addNewId) {
                index = i;
                return;
            }
        });
        if (index >= 0) {
            personList.selectSomebody(index);
        } else {
        	addEnable=false;
            $.getJSON('/rest_web/users/user/publicinfo/' + addNewId,
            function(res) {
            	addEnable=true;
                if (res.code == 0) {
                    personList.addSomebody(res.data);
                    personList.selectSomebody(personList.persons.size() - 1);
                } else {
                    layer.msg("ID错误");
                }
            });
        }
        $('.bg-mask').hide();
        $('#add-new-dialog').hide();
    });
    /*rongyun*/
    window.RongIMClient=RongIMClient;
    RongIMClient.init("0vnjpoadnkdxz");
    var token = laifu.get_ry_token();
    if (token == null) {
        alert("系统繁忙，请稍后再试");
        return;
    }

    function start_private_chat(){
        buyer_id = $("#contact_to_buyer").data('buyer-id');
        if (buyer_id!=""){
            var addNewId = buyer_id;
            var index = -1;
            if (!/[1-9][0-9]{4}/.test(addNewId)) {
                return;
            }
            $.each(personList.persons,
            function(i, e) {
                if ($(e).data('user-id') == addNewId) {
                    index = i;
                    return;
                }
            });
            if (index >= 0) {
                personList.selectSomebody(index);
            } else {
                addEnable=false;
                $.getJSON('/rest_web/users/user/publicinfo/' + addNewId,
                function(res) {
                    addEnable=true;
                    if (res.code == 0) {
                        personList.addSomebody(res.data);
                        personList.selectSomebody(personList.persons.size() - 1);
                    } else {
                        layer.msg("ID错误");
                    }
                });
            }
        }
        return ;
    }


    RongIMClient.setConnectionStatusListener({
        onChanged: function(status) {
            switch (status) {
                //链接成功
            case RongIMClient.ConnectionStatus.CONNECTED:
                console.log('链接成功');
                start_private_chat();
                break;
                //正在链接
            case RongIMClient.ConnectionStatus.CONNECTING:
                console.log('正在链接');
                break;
                //重新链接
            case RongIMClient.ConnectionStatus.RECONNECT:
                console.log('重新链接');
                break;
                //其他设备登陆
            case RongIMClient.ConnectionStatus.OTHER_DEVICE_LOGIN:
                //连接关闭
            case RongIMClient.ConnectionStatus.CLOSURE:
                //未知错误
            case RongIMClient.ConnectionStatus.UNKNOWN_ERROR:
                //登出
            case RongIMClient.ConnectionStatus.LOGOUT:
                //用户已被封禁
            case RongIMClient.ConnectionStatus.BLOCK:
                break;
            }
        }
    });
    // 消息监听器
    RongIMClient.getInstance().setOnReceiveMessageListener({
        // 接收到的消息
        onReceived:
        function(message) {
            // 判断消息类型
            //window.rymsg=message;
            var msg=new Msg(message.getSenderUserId(),message.getContent(),message.getSentTime(),message.getMessageType().value,0);
            store_msg(msg);
            var now_uid=personList.get_now_user_id();
            if(now_uid==msg.userId){
            	print_msg(msg);
            }else{
            	var index=personList.get_index_from_user_id(msg.userId);
            	if(index<0){
            		$.ajax({
                			url:'/rest_web/users/user/publicinfo/' + msg.userId,
                			async:false,
                			dataType:'json',
                			success:function(res){
                    			if (res.code == 0) {
                    				personList.addSomebody(res.data);
                    				var index=personList.get_index_from_user_id(msg.userId);
                    				var unread=personList.persons.eq(index).find('.unread-msgs');
            						var unreadNum=unread.find('.unread-num');
            						unreadNum.text(parseInt(unreadNum.text())+1);
            						unread.show();
                				}
                			}
            		});
            	}else{
            		var unread=personList.persons.eq(index).find('.unread-msgs');
            		var unreadNum=unread.find('.unread-num');
            		unreadNum.text(parseInt(unreadNum.text())+1);
            		unread.show();
            	}
            }
            switch (message.getMessageType()) {
            case RongIMClient.MessageType.TextMessage:
                // do something...
                break;
            case RongIMClient.MessageType.ImageMessage:
                // do something...
                break;
            case RongIMClient.MessageType.VoiceMessage:
                // do something...
                break;
            case RongIMClient.MessageType.RichContentMessage:
                // do something...
                break;
            case RongIMClient.MessageType.LocationMessage:
                // do something...
                break;
            case RongIMClient.MessageType.DiscussionNotificationMessage:
                // do something...
                break;
            case RongIMClient.MessageType.InformationNotificationMessage:
                // do something...
                break;
            case RongIMClient.MessageType.ContactNotificationMessage:
                // do something...
                break;
            case RongIMClient.MessageType.ProfileNotificationMessage:
                // do something...
                break;
            case RongIMClient.MessageType.CommandNotificationMessage:
                // do something...
                break;
            case RongIMClient.MessageType.UnknownMessage:
                // do something...
                break;
            default:
                // 自定义消息
                // do something...
            }
        }
    });
    RongIMClient.connect(token, {
        onSuccess: function(userId) {
            // 此处处理连接成功。
            console.log("Login successfully." + userId);
        },
        onError: function(errorCode) {
            // 此处处理连接错误。
            var info = '';
            switch (errorCode) {
            case RongIMClient.callback.ErrorCode.TIMEOUT:
                info = '超时';
                break;
            case RongIMClient.callback.ErrorCode.UNKNOWN_ERROR:
                info = '未知错误';
                break;
            case RongIMClient.ConnectErrorStatus.UNACCEPTABLE_PROTOCOL_VERSION:
                info = '不可接受的协议版本';
                break;
            case RongIMClient.ConnectErrorStatus.IDENTIFIER_REJECTED:
                info = 'appkey不正确';
                break;
            case RongIMClient.ConnectErrorStatus.SERVER_UNAVAILABLE:
                info = '服务器不可用';
                break;
            case RongIMClient.ConnectErrorStatus.TOKEN_INCORRECT:
                info = 'token无效';
                break;
            case RongIMClient.ConnectErrorStatus.NOT_AUTHORIZED:
                info = '未认证';
                break;
            case RongIMClient.ConnectErrorStatus.REDIRECT:
                info = '重新获取导航';
                break;
            case RongIMClient.ConnectErrorStatus.PACKAGE_ERROR:
                info = '包名错误';
                break;
            case RongIMClient.ConnectErrorStatus.APP_BLOCK_OR_DELETE:
                info = '应用已被封禁或已被删除';
                break;
            case RongIMClient.ConnectErrorStatus.BLOCK:
                info = '用户被封禁';
                break;
            case RongIMClient.ConnectErrorStatus.TOKEN_EXPIRE:
                info = 'token已过期';
                break;
            case RongIMClient.ConnectErrorStatus.DEVICE_ERROR:
                info = '设备号错误';
                break;
            }
            console.log("失败:" + info);
        }
    });
	$('#send').bind('click',function(){
		var targetId=personList.get_now_user_id();
		var ipt=$('#ipt').val();
		if(targetId==-1){
			layer.msg('请选择发送对象');
			return;
		}
		if(!ipt){
			layer.msg('消息不能为空');
			return;
		}
		RongIMClient.getInstance().sendMessage(RongIMClient.ConversationType.PRIVATE, String(targetId), RongIMClient.TextMessage.obtain(ipt), null, {
           onSuccess: function () {
                var msg=new Msg(targetId,ipt,new Date().getTime(),RongIMClient.MessageType.TextMessage.value,1);
                $('#ipt').val('');
                store_msg(msg);
                print_msg(msg);
           },
           onError: function (x) {
                var info = '';
                switch (x) {
                    case RongIMClient.callback.ErrorCode.TIMEOUT:
                        info = '超时';
                        break;
                    case RongIMClient.callback.ErrorCode.UNKNOWN_ERROR:
                        info = '未知错误';
                        break;
                    case RongIMClient.SendErrorStatus.REJECTED_BY_BLACKLIST:
                        info = '在黑名单中，无法向对方发送消息';
                        break;
                    case RongIMClient.SendErrorStatus.NOT_IN_DISCUSSION:
                        info = '不在讨论组中';
                        break;
                    case RongIMClient.SendErrorStatus.NOT_IN_GROUP:
                        info = '不在群组中';
                        break;
                    case RongIMClient.SendErrorStatus.NOT_IN_CHATROOM:
                        info = '不在聊天室中';
                        break;
                    default :
                        info = x;
                        break;
                }
                layer.msg('发送失败:' + info);
           }
       });;
	});
});