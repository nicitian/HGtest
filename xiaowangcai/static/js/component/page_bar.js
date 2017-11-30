(function() {
    var pagebar = $('#pagebar');
    var url = pagebar.data('url');
    var record_total = pagebar.data('record-total');
    var record_per_page = pagebar.data('record-per-page');
    var current_page = pagebar.data('current-page');
    var page_total = pagebar.data('page-total');
    function goPage(i) { (i < 1) && (i = 1); (i > page_total) && (i = page_total);
        var str = location.search;
        var strs = str.substr(1, str.length).split('&');
        var has_page = false,
        has_num = false;
        for (var index in strs) {
            str=strs[index];
            if (str.indexOf('page=')==0) {
                has_page = true;
                strs[index] = 'page=' + i
            }
            if (str.indexOf('num=')==0) {
                has_num = true;
                strs[index] = 'num=' + record_per_page
            }
        }
        if (!has_page) {
            strs.push('page=' + i)
        }
        if (!has_num) {
            strs.push('num=' + record_per_page)
        }
        location.search = '?' + strs.join('&')
    }
    pagebar.find('.first').bind('click',function(){goPage(1);});
    pagebar.find('.last').bind('click',function(){goPage(page_total);});
    pagebar.find('.prev').bind('click',function(){goPage(current_page-1);});
    pagebar.find('.next').bind('click',function(){goPage(current_page+1);});
    pagebar.find('.select').bind('change',function(){goPage($(this).val())});
})();