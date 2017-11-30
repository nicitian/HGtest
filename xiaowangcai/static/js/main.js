var laifu={
	get_user_id:function(){
		var uid=$('body').data('user-id');
		if(!uid||uid<0){
			$.getJSON("/rest_web/users/user/this",function(data) {
       			$('body').data('user-id',data.data.id)
    		});
		}
		return $('body').data('user-id');
	},
	get_task_id:function(){
		var tid=$('body').data('task-id');
		return tid?tid:-1;
	},
	get_order_id:function(){
		var oid=$('body').data('order-id');
		return oid?oid:-1;
	},
	parse_search:function(){
		var arr=location.search.split(new RegExp("[\?|\&]"));
		var obj={};
		for(var i=0;i<arr.length;i++){
			var ta=arr[i].split("=");
			if(ta.length>1){
				obj[ta[0]]=ta[1];
			}
		}
		return obj;
	},
	pic_upload:function(input_id, img_id) {
		if(!window.qiniu_token){
			console.log('get qiniu info');
			$.ajax({
            	type: "get",
            	async: false,
            	url: "/rest_web/users/user/qninfo",
            	contentType: "application/json; charset=utf-8",
            	dataType: "json",
            	success: function (res) {
            		if(res.code==0){
						window.qiniu_token=res.data.token;
						window.qiniu_expires=res.data.expires;
						window.qiniu_domain=res.data.domain;
					}else{
						alert('系统错误！');
					}
            	},
        	});
		}
        var input = $('#' + input_id) ;
        var img = $('#' + img_id) ;
        input.bind('change',
        function() {
        	var nowt=new Date().getTime();
        	if(nowt>window.qiniu_expires){
        		alert('页面已过期，请刷新后再试！');
        		return;
        	}
        	var uid=window.laifu.get_user_id();
            var form = $('<form method="post" action="http://upload.qiniu.com/" enctype="multipart/form-data"></form>');
            var upload = $('<input type="file" hidden="hidden" name="file" />');
            var token = $('<input type="text" hidden="hidden" name="token" />');
            //var key = $('<input type="text" hidden="hidden" name="key" />');
            upload[0].files = input[0].files;
            token.val(window.qiniu_token);
			console.log(window.qiniu_token);
            //var fname=upload[0].files[0].name;
            //key.val(uid+'/'+nowt+fname.substr(fname.lastIndexOf('.')));
            form.append(upload);
            form.append(token);
            //form.append(key);
            form.ajaxSubmit({
                success: function(d) {
                    if (d.key) {
                        img.attr('src', window.qiniu_domain+d.key);
                        input.data('path', window.qiniu_domain+d.key);
                    }else{
                    	alert('系统错误！');
                    }
                }
            });
        });
    }
};
(function() { 
	Date.prototype.Format = function (fmt) { //author: meizz 
	    var o = {
	        "M+": this.getMonth() + 1, //月份 
	        "d+": this.getDate(), //日 
	        "h+": this.getHours(), //小时 
	        "m+": this.getMinutes(), //分 
	        "s+": this.getSeconds(), //秒 
	        "q+": Math.floor((this.getMonth() + 3) / 3), //季度 
	        "S": this.getMilliseconds() //毫秒 
	    };
	    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
	    for (var k in o)
	    if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
	    return fmt;
	}
})(); 
