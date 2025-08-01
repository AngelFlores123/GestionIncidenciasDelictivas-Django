clusters = JSON.parse(clusters);
document.addEventListener("DOMContentLoaded", function(){
    var iniLat = 19.432608;
    var iniLng = -99.133209;

    // inicia el mapa centrado en la ubicacion predefinida con zoom 13
    // coloca el mapa en el div con id 'mapa'
    var mapa = L.map('mapa').setView([iniLat, iniLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(mapa);

    var grupoClusters = L.featureGroup();
    clusters.forEach(function(cluster){
        var lat = cluster.latitud;
        var lng = cluster.longitud;
        var noIncidencias = cluster.noIncidencias;
        var marcador = L.marker([lat, lng]).addTo(mapa); // se crea un marcador en la ubicacion del cluster
        marcador.bindPopup("Número de incidencias: " + noIncidencias); // mensaje que indica la cantidad de incidencias del cluster (al hacer click)
        grupoClusters.addLayer(marcador); // los marcadores se agrupan
    });
    if(grupoClusters.getLayers().length > 0){
        mapa.fitBounds(grupoClusters.getBounds()); // ajusta el mapa para mostrar todos los marcadores
    }
});