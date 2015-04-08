$(window).ready(function(){
	$(document).on("click", "#commenta", aggiungi_form_commenti);
});

function aggiungi_form_commenti(){
	$(document).off("click", "#commenta", aggiungi_form_commenti);
	var frm = $(document.createElement("form"))
		.attr("action", "/commenti")
		.attr("method", "POST");
	var txt = $(document.createElement("textarea"))
		.attr("name", "commento");
	var sbm = $(document.createElement("input"))
		.attr("type", "submit");
	$("#corpo")
		.empty()
		.append(frm.append(txt).append(sbm));
};
