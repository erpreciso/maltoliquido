var geocoder;
var map;
var address;

function inizializza_mappa(div_id) {
	var myLatlng = new google.maps.LatLng(45.6927841, 8.8074389);
	geocoder = new google.maps.Geocoder();
    var mapOptions = {
      zoom: 8,
      center: myLatlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    map = new google.maps.Map(document.getElementById(div_id), mapOptions);
    google.maps.event.addListener(map, 'click', function(event) {
		var latlngStr = event.latLng.toString().split(',', 2);
		var lat = parseFloat(latlngStr[0].replace("(",""));
		var lng = parseFloat(latlngStr[1]);
		var latlng = new google.maps.LatLng(lat, lng);
		//alert(latlng.toString());
		geocoder.geocode({'latLng': latlng}, function(results, status) {
			if (status == google.maps.GeocoderStatus.OK) {
				if (results[0]) {
					for (i = 0; i < results[0].address_components.length; i++) {
						if (results[0].address_components[i].types[0] == "country") {
							alert(results[0].address_components[i].short_name);
						}
					}
					//alert(status);
				}
			}
		});
	});
		
}

$(window).ready(function(){
	//alert($("#corpo").text());
	inizializza_mappa("mappa_1");
});
