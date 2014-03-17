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
	
	if(esiste_elemento(null, "birra", null) == false) {
		scrivi_form_inserimento_birra(json, null);
	};
	
	$(document).on('click',"#modifica",function(){
		var vecchio_contenuto = salva_contenuto();
		$(".birra").remove();
		scrivi_form_inserimento_birra(json, vecchio_contenuto);
	});
	
	// evita il POST al premere di ENTER
	$("input, select").keypress(function(event) { return event.keyCode != 13; });
	
});

function salva_contenuto(){
	vecchio_contenuto = new Object();
	vecchia_immagine_principale = new Object();
	$(".birra").children().each(function(){
		if ($(this).attr("class") == "immagineprincipale") {
			vecchia_immagine_principale.src = $(".immagineprincipale img").attr("src");
			vecchia_immagine_principale.href = $(".immagineprincipale a").attr("href");
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

function scrivi_form_inserimento_birra(json, vecchio_contenuto){
	var upload_url = $(".upload_url").text();
	elm_form = $(document.createElement("form"))
		.attr("enctype", "multipart/form-data")
		.attr("method", "POST")
		.attr("action", upload_url);
	//key
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
		.attr("placeholder", "chi sei?");
	elm_form.append(elm.append(inp));
	//altri attributi
	for (var i = 0; i < json.attributi_birra.length; i++) {
		var elm = $(document.createElement("div"));
		if (json.attributi_birra[i].tipo == "input") {
			var inp = $(document.createElement("input"))
				.attr("name", json.attributi_birra[i].ascii)
				.attr("required", "required")
				.attr("placeholder", json.attributi_birra[i].text);
			if (vecchio_contenuto && vecchio_contenuto[0][json.attributi_birra[i].ascii]) {
				inp.attr("value", vecchio_contenuto[0][json.attributi_birra[i].ascii]);
			}
			elm_form.append(elm.append(inp));
			}
		if (json.attributi_birra[i].tipo == "file") {
			var inp = $(document.createElement("input"))
				.attr("name", json.attributi_birra[i].ascii)
				.attr("placeholder", json.attributi_birra[i].text)
				.attr("required", "required")
				.attr("type", "file");
			elm_form.append(elm.append(inp));
			}
		else if (json.attributi_birra[i].tipo == "select") {
			var sel = $(document.createElement("select"))
				.attr("name", json.attributi_birra[i].ascii);
			for (var j = 0; j < json.attributi_birra[i].lista.length; j++) { 
				var opt = $(document.createElement("option"))
						.attr("value", json.attributi_birra[i].lista[j].ascii)
						.text(json.attributi_birra[i].lista[j].text);
				if (vecchio_contenuto && vecchio_contenuto[0][json.attributi_birra[i].ascii] == json.attributi_birra[i].lista[j].ascii) {
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
