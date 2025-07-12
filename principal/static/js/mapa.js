// mostrar el mapa al cargar la página
document.addEventListener("DOMContentLoaded", function(){
    // coordenadas iniciales en cdmx
    var iniLat = 19.432608;
    var iniLng = -99.133209;

    // obtiene los valores actuales de los campos ocultos
    var latInput = document.getElementById('latitud');
    var lngInput = document.getElementById('longitud');
    var lat = latInput.value ? parseFloat(latInput.value) : iniLat;
    var lng = lngInput.value ? parseFloat(lngInput.value) : iniLng;

    // inicia el mapa centrado en la ubicacion predefinida con zoom 13
    var mapa = L.map('mapa').setView([lat, lng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(mapa);

    var marcador = null;

    // muestra el marcador si hay coordenadas en los campos ocultos (editar libro)
    if (latInput.value && lngInput.value) {
        marcador = L.marker([lat, lng]).addTo(mapa);
    }

    // al hacer clic en el mapa, mueve o crea el marcador y actualiza los campos
    mapa.on('click', function(e) {
        var newLat = e.latlng.lat.toFixed(6);
        var newLng = e.latlng.lng.toFixed(6);

        latInput.value = newLat;
        lngInput.value = newLng;

        if (marcador) {
            marcador.setLatLng(e.latlng);
        } else {
            marcador = L.marker(e.latlng).addTo(mapa);
        }
    });
});