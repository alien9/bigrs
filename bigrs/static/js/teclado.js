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
        if(!contado[s]) contado[s]={};
        if(!contado[s][t])contado[s][t]=0;
        var veiculo={
            ts:timestamp,
            spot_id:s,
            tipo:t,
            local_id:local_id,
            contagem_id:contagem_id
        };
        contado[s][t]++;
        fila[local_id]=veiculo;
        local_id++;
        setContagem();
    });

    var updateContagens=function(){
        var spot_id=$('select[name=spot]').val();
        if(!spot_id) return;
        $.ajax('/update_contagens', {dataType:'json',method:'POST',data:{contagem_id:contagem_id,'spot_id':spot_id,csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},success:function(h){
            contado[spot_id]=h;
            setContagem();
        },'error':function(e){
            console.log('Erro: não foi possível receber os dados.');
            console.debug(e);
        }});

    };
    $('select[name=spot]').change(updateContagens);

    var resize=function(){
        $(".main").css('height',($('body').height()-$('.head').height())+'px');

        if($('body').height()>$('body').width()){ //vertical
            var w=Math.floor(($('body').height()-$('.head').height()) / $('.main>a').length);
            $('.main>a').css('width', (w+220)+'px');
            $('.main>a').css('height', w+'px');
            $('.main>a').css('display', 'block');
            $('.main>a').css('background-size', 'auto 100%');
            $('.main>a').css('text-align','left');

        }else{ //horizontal
            var w=Math.floor($('body').width() / $('.main>a').length);
            $('.main>a').css('width', w+'px');
            $('.main>a').css('height', (w+220)+'px');
            $('.main>a').css('display', 'inline-block');
            $('.main>a').css('background-size', '100% auto');
            $('.main>a').css('text-align','center');
        }


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
                if(!contado[spots[i].id]) contado[spots[i].id]={};
            }
            $('.filename').text(h.movie);
        },'error':function(e){
            console.log('Erro: não foi possível encontrar o video.');
            console.debug(e);
            setTimeout(updatePlayer, 3000);
        }});
    };
    updatePlayer();
    setTimeout(upload, 10000);
});

function setContagem(){
    $('.main>a .display').text('');
    var spot_id=$('select[name=spot]').val();
    if(!spot_id) return;
    for(var tipo in contado[spot_id]){
        $("a[tipo="+tipo+"] .display").text(contado[spot_id][tipo]);
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
        },'error':function(e){
            console.log('Erro: não foi possível enviar a contagem.');
            console.debug(e);
            setTimeout(upload, 10000);
        }});
    }else{
        setTimeout(upload,10000);
    }
}