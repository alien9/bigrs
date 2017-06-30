$(document).ready(function(){
    $(".lista_contagens a").click(function(){
        //alert($(this).attr('contagem'));
    });
    start();
});
function start(){
    console.debug('startando');
    $('.bairro_title').click(function(){
        var d=$(this).parent().find(".contagem_body");
        if(!d.is(':visible')){
            d.animate({
                height : d.scrollHeight
            },{duration:400,
                done:function(){d.hide();alert('ok')}
            });

        }else{
            d.animate({
                height : '0'
            },1000);

        }
    });
}