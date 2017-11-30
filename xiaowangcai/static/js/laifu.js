define('laifu', ['jquery', 'lib/jquery.form'],
function($, jform) {
    Date.prototype.Format = function(fmt) { //author: meizz 
        var o = {
            "M+": this.getMonth() + 1,
            //月份 
            "d+": this.getDate(),
            //日 
            "h+": this.getHours(),
            //小时 
            "m+": this.getMinutes(),
            //分 
            "s+": this.getSeconds(),
            //秒 
            "q+": Math.floor((this.getMonth() + 3) / 3),
            //季度 
            "S": this.getMilliseconds() //毫秒 
        };
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
        for (var k in o) if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        return fmt;
    }
    return {
        get_user_id: function() {
            var uid = $('body').data('user-id');
            if (!uid || uid < 0) {
                $.getJSON("/rest_web/users/user/this",
                function(data) {
                    $('body').data('user-id', data.data.id)
                });
            }
            return $('body').data('user-id');
        },
        get_task_id: function() {
            var tid = $('body').data('task-id');
            return tid ? tid: -1;
        },
        get_order_id: function() {
            var oid = $('body').data('order-id');
            return oid ? oid: -1;
        },
        parse_search: function() {
            var arr = location.search.split(new RegExp("[\?|\&]"));
            var obj = {};
            for (var i = 0; i < arr.length; i++) {
                var ta = arr[i].split("=");
                if (ta.length > 1) {
                    obj[ta[0]] = ta[1];
                }
            }
            return obj;
        },
        pic_upload: function(input_id, img_id) {
            var input = $('#' + input_id);
            var img = $('#' + img_id);
            input.bind('change',
            function() {
                var form = $('<form method="post" action="/rest_web/users/user/uploadimage/' + window.laifu.get_user_id() + '" enctype="multipart/form-data"></form>');
                var upload = $('<input type="file" hidden="hidden" name="image" />');
                upload[0].files = input[0].files;
                form.append(upload);
                form.ajaxSubmit({
                    success: function(d) {
                        if (d.code == 0) {
                            img.attr('src', d.path);
                            input.data('path', d.path);
                        }
                    }
                });
            });
        },
        get_ry_token: function(){
            if(sessionStorage&&sessionStorage['ry_token']){
                return sessionStorage['ry_token'];
            }
            var token;
            $.ajax({
                url:'/rest_web/users/user/getrytoken/'+this.get_user_id(),
                async:false,
                dataType:'json',
                success:function(res){
                    if(res.code==0){
                        sessionStorage['ry_token']=res.data.token;
                        token=res.data.token;
                    }else{
                        token=null;
                    }
                }
            });
            return token;
        },
        filter_script:function(s){
            if(typeof(s)=="string"){
                return s.replace(/<script.*?>.*?<\/script>/ig, '');  
            }else{
                return s;
            }
        }
    }
})