$(document).ready(function() {
   $("body").tooltip({ selector: '[data-toggle=tooltip]' });

   $('#apagarpost').click(function() {
        $('div').fadeOut(1200);
   });

   $('[id^=comentario] .btn').click(function() {
        $(this).parent().parent().parent().fadeOut(1200);
   });
});