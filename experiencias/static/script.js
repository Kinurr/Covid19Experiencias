$(document).ready(function() {
   $('#apagarpost').click(function() {
        $('div').fadeOut(1200);
   });

   $('[id^=comentario] .btn').click(function() {
        $(this).parent().parent().parent().fadeOut(1200);
   });

});