    $(".max_min_button").click(function(){
    if($(this).html() == "-"){
        $(this).html("+");
    }
    else{
        $(this).html("-");
    }
    var thisParent = $(this).parent();
    $(thisParent).next(".commentbody").slideToggle();
});