$(document).ready(function() {
   $("body").tooltip({ selector: '[data-toggle=tooltip]' });

   $('#apagarpost').click(function() {
        $('div').fadeOut(1200);
   });

   $('[id^=comentario] .btn').click(function() {
        $(this).parent().parent().parent().fadeOut(1200);
   });


//  ##########################  Pagination Logic  ################################
   var numItems = $("#allContent .post-card").length;
   var limit = 12;
   $("#allContent .post-card:gt(" + (limit - 1) + ")").hide();

    var pagTotal = Math.ceil(numItems / limit);
    $('.pagination').append("<li class='page-item current-page active'><a class='page-link' href='javascript:void(0)'>" + 1 + "</a></li>")

    for(var i = 2; i <= pagTotal; i++) {
        $('.pagination').append("<li class='page-item current-page'><a class='page-link' href='javascript:void(0)'>" + i + "</a></li>");
    }

    $('.pagination').append("<li class='page-item' id='next-page'><a class='page-link' href='javascript:void(0)' aria-label='Next'><span aria-hidden='true'>&raquo;</span><span class='sr-only'>Next</span></a></li>");

    $(".pagination li.current-page").on("click", function() {
        if ($(this).hasClass("active")) {
            return false;
        } else {
            var currentPage = $(this).index();
            $(".pagination li").removeClass("active");
            $(this).addClass("active");
            $("#allContent .post-card").hide();
            var total = limit * currentPage;
            for (var i = total - limit; i < total; i++) {
                $("#allContent .post-card:eq(" + i + ")").show();
            }
        }
    });

    $("#next-page").on("click", function() {
        var currentPage = $(".pagination li.active").index();
        if (currentPage === pagTotal) {
            return false;
        } else {
            currentPage++;
            $(".pagination li").removeClass("active");
            $("#allContent .post-card").hide();
            var total = limit * currentPage;
            for (var i = total - limit; i < total; i++) {
                $("#allContent .post-card:eq(" + i + ")").show();
            }
            $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass("active");
        }

    });

    $("#previous-page").on("click", function() {
        var currentPage = $(".pagination li.active").index();
        if (currentPage === 1) {
            return false;
        } else {
            currentPage--;
            $(".pagination li").removeClass("active");
            $("#allContent .post-card").hide();
            var total = limit * currentPage;
            for (var i = total - limit; i < total; i++) {
                $("#allContent .post-card:eq(" + i + ")").show();
            }
            $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass("active");
        }

    });



//  ###############################################################################################

});