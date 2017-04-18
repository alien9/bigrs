var fila={};
var contado={};
var contagem_id;
var timestamp;
var local_id=1;
$(document).ready(function(){
    $('.main>a').click(function(){
        var s=$('select[name=spot]').val();
        if(!s || (!s.length)){
            alert('Escolha uma direção para contar');
            return;
        }
        var t=$(this).attr('tipo');
        console.debug(t);
        if(!contado[t])contado[t]=0;
        var veiculo={
            ts:timestamp,
            spot_id:s,
            tipo:t,
            local_id:local_id,
            contagem_id:contagem_id
        };
        contado[t]++;
        fila[local_id]=veiculo;
        local_id++;
        setContagem();
    });
    $('select[name=spot]').change(function(){
        $.ajax('update_contagem', {dataType:'json',method:'POST',data:{contagem_id:contagem_id,spot_id:$('select[name=spot]').val()},success:function(h){
            console.debug(h);
        }})
    });


    var resize=function(){
        $(".main").css('height',($('body').height()-$('.head').height())+'px');
        $('.main>a').css('width', Math.floor($('body').width() / $('.main>a').length)+'px');
    };
    $(window).resize(resize);
    resize();
    var updatePlayer=function(){
        $.ajax('/get_player', {'success':function(h){
            if(!h.movie) alert('é preciso tocar um filme');
            setTimeout(updatePlayer, 3000);
            var spots=eval(h.spots);
            contagem_id=h.contagem_id;
            timestamp=h.ts;
            var selected=$('select[name=spot]').val();
            $('select[name=spot]').html('<option/>');
            for(var i=0;i<spots.length;i++){
                var option=document.createElement('option');
                $(option).attr('value', spots[i].id);
                $(option).text(spots[i].alias);
                if(selected==spots[i].id) $(option).attr('selected',true);
                $('select[name=spot]').append(option);
            }
            $('.filename').text(h.movie);
        }});
    };
    setTimeout(updatePlayer, 3000);
    setTimeout(upload, 10000);
});

function setContagem(){
    for(var tipo in contado){
        $("a[tipo="+tipo+"] .display").text(contado[tipo]);
    }
}
function upload(){
    var size=0;
    for(var k in fila) size++;
    if(size>0){
    $.ajax('/conta',{method:'POST',data:{fila:JSON.stringify(fila),csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},success:function(h){
        for(var local_id in h){
            delete(fila[local_id]);
        }
        setTimeout(upload,10000);
    }});
    }else{
        setTimeout(upload,10000);
    }
}