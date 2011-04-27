jQuery.fn.sort = function() {  
   return this.pushStack([].sort.apply(this, arguments), []);  
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
        var show = $(this).attr("checked");
        if (show) {
            var type = $(this).attr("id").split("-")[1];
            var matches = $("." + type).closest("tr");
            rows = rows.add(matches);      
        }
    });
    return rows;
}

function redraw_latest_writing (checked) {
        $("table#latest-writing tr").hide();
        filter_rows(checked).slice(0, 7).show();
        return false;
}

function filter_toggle (checkboxes, toggle) {
    return function(){
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
    }
}

function post_comment () {
    var data = $(this).serialize();
    // avoids people posting something twice
    $('form input, form textarea').attr('disabled', true);
    // ajax post
    $.post("/director/comments/", data)
        .success(function(response){
            $("#comments div.list").append(response).hide().fadeIn();
            $("form").remove();
        }).error(function(response){
            $("form").addClass("invalid");
            $('form input, form textarea').attr('disabled', false);
        });
    return false;
}

$(document).ready(function () {
    // hide comments, and only show them when a reader has reached the bottom of the blog post
    hide_comments();
    // ajaxy comment posting
    $("form").submit(post_comment);
    
    // hide all permalinks
    $("a.permalink").hide();
    
    // show a permalink when hovering over a comment
    $("article.comment").hover(function () {
        $(this).find("a.permalink").show();
    }, function () {
        $(this).find("a.permalink").hide();        
    });

    // manage / instantiate the toggling mechanism
    var toggle = $("div.filter input.toggle");
    var checkboxes = $("div.filter input:enabled").not("input.toggle");
    
    redraw_latest_writing(checkboxes);
    toggle.click(toggle_all);    
    checkboxes.add(toggle).click(filter_toggle(checkboxes, toggle));
});