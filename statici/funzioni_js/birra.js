$(window).ready(function(){
	
	// carica le liste json
	var json = (function () {
		    var json = null;
		    $.ajax({
		        'async': false,
		        'global': false,
		        'url': "/liste/liste.json",
		        'dataType': "json",
		        'success': function (data) {
		            json = data;
		        }
		    });
		    return json;
		})();
	// pulsante per codice pagina
	//$(document).on('click',"#btn_1",function(){
		//alert($("section").html());
	//});
	// scrive la form inserimento birra se la pagina è vuota
	if(esiste_elemento(null, "birra", null) == false) {
		scrivi_form_inserimento(json, "form_birra", "attributi_birra", null);
	};
	
	// scrive form inserimento birra se necessita di essere modificata
	$(document).on('click',"#modifica",function(){
		var vecchio_contenuto = salva_contenuto();
		$(".birra").remove();
		scrivi_form_inserimento(json, "form_birra", "attributi_birra", vecchio_contenuto);
	});
	
	// scrive form inserimento acquisto
	$(document).on("click", "#acquisto", function(){
		var vecchio_contenuto = salva_contenuto();
		scrivi_form_inserimento(json, "form_acquisto", "attributi_acquisto", vecchio_contenuto);
	});
	
	// evita il POST al premere di ENTER
	$("input, select").keypress(function(event) { return event.keyCode != 13; });
	
});

function salva_contenuto(){
	vecchio_contenuto = new Object();
	vecchia_immagine_principale = new Object();
	$(".birra").children().each(function(){
		if ($(this).attr("class") == "immaginebirra") {
			vecchia_immagine_principale.src = $(".immaginebirra img").attr("src");
			vecchia_immagine_principale.href = $(".immaginebirra a").attr("href");
		}
		else if ($(this).attr("class") == "key") {
			vecchio_contenuto[$(this).attr("class")] = $(this).text();
		}
		else {
			vecchio_contenuto[$(this).attr("class")] = $(this).children("a").text();
		};
	});
	return [vecchio_contenuto, vecchia_immagine_principale];
};
function formatta_data(date) {
    var mm = date.getMonth() + 1;
    var dd = date.getDate();
    var yyyy = date.getFullYear();
    mm = (mm < 10) ? '0' + mm : mm;
    dd = (dd < 10) ? '0' + dd : dd;
    var hh = date.getHours();
    var min = date.getMinutes();
    var ss = date.getSeconds();
    hh = (hh < 10) ? '0' + hh : hh;
    min = (min < 10) ? '0' + min : min;
    ss = (ss < 10) ? '0' + ss : ss;
    return yyyy + "-" + mm + "-" + dd + " " + hh + ":" + min + ":" + ss;
};

function scrivi_form_inserimento(json, nome_form, attributi, vecchio_contenuto){
	var upload_url = $(".upload_url").text();
	elm_form = $(document.createElement("form"))
		.attr("enctype", "multipart/form-data")
		.attr("method", "POST")
		.attr("name", "birra")
		.attr("action", upload_url);
	
	// nome form
	var elm = $(document.createElement("div"));
	var inp = $(document.createElement("input"))
		.attr("name", "nome_form")
		.attr("type", "hidden")
		.attr("value", nome_form);
	elm_form.append(elm.append(inp));
	
	// key
	if (vecchio_contenuto) {
		var elm = $(document.createElement("div"));
		var inp = $(document.createElement("input"))
			.attr("name", "key")
			.attr("type", "hidden")
			.attr("value", vecchio_contenuto[0]["key"]);
		elm_form.append(elm.append(inp));
	}
	//utente
	var elm = $(document.createElement("div"));
	var inp = $(document.createElement("input"))
		.attr("name", "autore")
		.attr("required", "required")
		.attr("placeholder", "chi sei? inserisci il tuo nick");
	elm_form.append(elm.append(inp));
	//altri attributi
	for (var i = 0; i < json[attributi].length; i++) {
		var elm = $(document.createElement("div"));
		if (json[attributi][i].tipo == "input") {
			var inp = $(document.createElement("input"))
				.attr("name", json[attributi][i].ascii)
				.attr("placeholder", json[attributi][i].text);
			if (json[attributi][i].richiesto == true) {
				inp.attr("required", "required");
			}
			if (vecchio_contenuto && vecchio_contenuto[0][json[attributi][i].ascii]) {
				inp.attr("value", vecchio_contenuto[0][json[attributi][i].ascii]);
			}
			elm_form.append(elm.append(inp));
			}
		if (json[attributi][i].tipo == "file") {
			var inp = $(document.createElement("input"))
				.attr("name", json[attributi][i].ascii)
				.attr("placeholder", json[attributi][i].text)
				.attr("required", "required")
				.attr("type", "file");
			elm_form.append(elm.append(inp));
			}
		else if (json[attributi][i].tipo == "select") {
			var sel = $(document.createElement("select"))
				.attr("name", json[attributi][i].ascii);
			for (var j = 0; j < json[attributi][i].lista.length; j++) { 
				var opt = $(document.createElement("option"))
						.attr("value", json[attributi][i].lista[j].ascii)
						.text(json[attributi][i].lista[j].text);
				if (vecchio_contenuto && vecchio_contenuto[0][json[attributi][i].ascii] == json[attributi][i].lista[j].ascii) {
					opt.attr("selected", "selected");
				}
				sel.append(opt);
				}
			elm_form.append(elm.append(sel));
			}
		}
	
	// tasto submit
	var subm = $(document.createElement("input"))
		.attr("type", "submit")
		.attr("value", "Pubblica");
	elm_form.append(subm);
	$("#corpo").append(elm_form);
};

function esiste_elemento(
		tag_elemento,
        classe_elemento,
		id_elemento
		){
	if (id_elemento)
		{ return $("#" + id_elemento).length > 0; }
    else if (classe_elemento)
        { return $("." + classe_elemento).length > 0; }
        
	else if (tag_elemento)
		{ return $(tag_elemento).length > 0; }
	else
		{ return false; }
};
