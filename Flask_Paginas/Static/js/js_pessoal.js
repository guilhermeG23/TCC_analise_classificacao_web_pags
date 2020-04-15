//JS para sumir com os elementos 
//Só parte estetica

function confirmar() {
    var valores = "";
    $.each( $( ".mybuttons" ), function() {
        if ( document.getElementById(this.id).checked == true ) {
            mostrar("mostrar-" + this.id);
            valores = valores + "-" + document.getElementById(this.id).value;
        } else {
            sumir("mostrar-" + this.id);
        }
    });
    document.getElementById('pesquisar_dominios').value = valores;
}

function mostrar(aparecer) {
	var display = document.getElementById(aparecer).style.display;
    document.getElementById(aparecer).style.display = 'initial';
}

function sumir(aparecer) {
    var display = document.getElementById(aparecer).style.display;
    document.getElementById(aparecer).style.display = 'none';
}

function resetar_selecao() {
    $.each( $( ".mybuttons" ), function() {
        if ( document.getElementById(this.id).checked == true ) {
            document.getElementById(this.id).checked = false;   
        }
    });
    document.getElementById('modelo_nome').value = "";
    document.getElementById('pesquisar_dominios').value = "";
    document.getElementById('classificar_modelo').value = "";
    confirmar();
}

/* Estados da classificacao */
function aprovar() {
    document.getElementById('classificar_modelo').value = "Aprovado";
    document.getElementById('aprovacao_do_modelo').value = 0;
}
function bloquear() {
    document.getElementById('classificar_modelo').value = "Bloqueado";
    document.getElementById('aprovacao_do_modelo').value = 1;
}