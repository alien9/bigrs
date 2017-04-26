var fila={};
var contado={};
var contagem_id;
var timestamp;
var local_id=1;
$(document).ready(function(){
    $('.painel>a').click(conta);
    var loadContagem=function(){
        var spot_id=$('select[name=spot]').val();
        var spot_name=$('select[name=spot] option:selected').text();
        if(!spot_id) return;
        $.ajax('/update_contagens', {dataType:'json',method:'POST',data:{contagem_id:contagem_id,'spot_id':spot_id,csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},success:function(h){
            contado[spot_id]=h;
            draw(spot_id, spot_name);
            setContagem(spot_id);
        },'error':function(e){
            console.log('Erro: não foi possível receber os dados.');
            console.debug(e);
        }});

    };

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

    $('select[name=spot]').change(loadContagem);


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
            $('select[name=spot]').html('<option>escolha um ponto</option>');
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
            if(confirm('quer tentar de novo?')) setTimeout(updatePlayer, 3000);
        }});
    };
    updatePlayer();
    setTimeout(upload, 10000);
});

function setContagem(spot_id){
    $('.painel[spot='+spot_id+']>a.btn .display').text('');
    if(!spot_id) return;
    for(var tipo in contado[spot_id]){
        console.debug(tipo);
        console.log('.painel[spot='+spot_id+'] a[tipo='+tipo+'] .display');
        $('.painel[spot='+spot_id+'] a[tipo='+tipo+'] .display').text(contado[spot_id][tipo]);
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

function beep() {
    var snd = new Audio("data:audio/wav;base64,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qJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l//8elePK/Lf//IInrOF/FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j/12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf/pD6ElLqSX+rUmOQNpJFa/r+sa4e/pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA//uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid/9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN/9Robv/Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV/YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI/gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a/EEBUdU1KrXLf40GoiiFXK///qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd/+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt/WKi2N4d//uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF/Mg+0aohSIRobBAsMlO//Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W/rFRb/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU=");
    snd.play();
}

function draw(butt_id,spot_name){
    if(!contado[butt_id]) return;
    var d=$('<div class="painel" spot="'+butt_id+'"><a class="capital"><div class="display" style="line-height: 190px;">'+spot_name+'</div></a></div>');
    $('body').append(d);
    var tipos=[
        'carro',
        'moto',
        'microonibus',
        'onibus',
        'brt',
        'vuc',
        'caminhao',
        'pedestre',
        'bici'
    ];
    for(var i=0;i<tipos.length;i++){
        var k=tipos[i];
    //for(var k in contado[butt_id]){
        if(k in contado[butt_id])
            $(d).append($('<a style="background-image:url(/static/images/icons/'+k+'.png)" tipo="'+k+'" class="btn"><div class="display">0</div></a>'));
    }
    $('.painel[spot='+butt_id+']>a.btn').click(conta);
    resize();
}

var resize=function(){
    var artura=Math.floor(($('body').height()-$('.head').height())/3);
    $(".painel").css('height',artura+'px');
    if($('body').height()>$('body').width()){ //vertical
        var w=Math.floor(($('body').height()-$('.head').height()) / $('.painel>a').length);
        $('.painel>a').css('width', (w+220)+'px');
        $('.painel>a').css('height', w+'px');
        $('.painel>a').css('display', 'block');
        $('.painel>a').css('background-size', 'auto 100%');

    }else{ //horizontal
        var w=Math.floor($('body').width() / 11);
        $('.painel>a').css('width', w+'px');
        $('.painel, .painel>a').css('height', (w+20)+'px');
        $('.painel>a').css('display', 'inline-block');
        $('.painel>a').css('background-size', '100px 100px');
    }
};
var conta=function(){
    var t;
    if(!(t=$(this).attr('tipo'))) return;
    var s=$(this).parent().attr('spot');
    if(!s || (!s.length) || !(s.match(/\d+/))){
        alert('Escolha uma direção para contar');
        return;
    }
    beep();

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
    setContagem(s);
}