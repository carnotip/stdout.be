jQuery.fn.sort = function() {  
   return this.pushStack([].sort.apply(this, arguments), []);  
 };  
  
function newest_first(a, b){
    a = $(a).attr("data-timestamp")
    b = $(b).attr("data-timestamp")
    return parseInt(a) < parseInt(b) ? 1 : -1;  
};  

function hide_comments() {
    var anchor = $.url.attr("anchor") || '';
    if (anchor.indexOf("comment") == -1) {
        $("div#comments h2").one('inview', function(){
            $("div#comments div").fadeIn("slow");
        });
        $("div#comments div").hide();
    }
}

function toggle_all () {
    var checked = $(this).attr("checked");
    $(this).closest("div.filter").find("input:enabled").attr("checked", checked);
}

function filter_rows (checked) {
    var rows = $();
    checked.each(function () {
        var show = $(this).attr("checked")
        if (show) {
            var type = $(this).attr("id").split("-")[1];
            var matches = $("." + type).closest("tr");
            rows = rows.add(matches)         
        }
    });
    return rows;
}

function redraw_latest_writing (checked) {
        $("tr").hide()
        $('table tr').sort(newest_first).appendTo('table');
        filter_rows(checked).slice(0, 7).show();
        return false;
}

$(document).ready(function () {
    hide_comments();
    
    $("div.comment").hover(function () {
        $(this).find("a.permalink").show();
    }, function () {
        $(this).find("a.permalink").hide();        
    });

    var toggle = $("div.filter input.toggle");
    var checkboxes = $("div.filter input:enabled").not("input.toggle");

    redraw_latest_writing(checkboxes);

    toggle.click(toggle_all);
    
    checkboxes.add(toggle).click(function () {
        // filter rows
        redraw_latest_writing(checkboxes);
    
        // if every type is checked, the global toggle should be checked as well
        // and vice versa
        var total = checkboxes.length;
        var active = checkboxes.filter(function () {
            return $(this).attr("checked"); 
        }).length
        if (total == active) {
            toggle.attr("checked", true)
        } else {
            toggle.attr("checked", false)
        }
    });

    var row = '<tr data-timestamp="200">\
                <td><a href="" class="badge guestpost">guest post</a></td>\
                <td>200 <a href="">This new thang</a></td>\
            </tr>'
});