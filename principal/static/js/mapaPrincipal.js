document.addEventListener("DOMContentLoaded", function(){
    var iniLat = 19.432608;
    var iniLng = -99.133209;

    // coloca el mapa en el div con id 'mapa', zoom 13
    var mapa = L.map('mapa').setView([iniLat, iniLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(mapa);

    var semillasFC  = turf.featureCollection([]);
    var clientesFC  = turf.featureCollection([]);
    var cdmx_divFC = turf.featureCollection([]);

    semillas = JSON.parse(semillas);
    cdmx_division = JSON.parse(cdmx_division);
    console.log('CDMX Division:', cdmx_division);

    semillas.forEach(s => {
        const lat = parseFloat(s.latitud);
        const lng = parseFloat(s.longitud);
        if (Number.isFinite(lat) && Number.isFinite(lng)) {
            semillasFC.features.push( // se agrega un punto al feature collection con propiedades id y alcaldia
                turf.point([lng, lat], { id: String(s.gid), nombre: s.alcaldia || String(s.gid) })
            );
        }
    });

    if(alcaldia !== 'None'){
        // alcaldia tiene un valor, se filtra la division de la CDMX para obtener solo esa alcaldia
        console.log('if');
        const alcaldias = cdmx_division.features.filter(cd => cd.properties.nomgeo === alcaldia);
        alcaldias.forEach(cd => {
            const geom = cd.geometry;
            cdmx_divFC.features.push(
                turf.feature(geom, {
                    nombre: cd.properties.nomgeo || 'Desconocida'
                })
            );
        });
    }else{
        // alcaldia no tiene valor, se usan todas las alcaldias
        console.log('else');
        cdmx_division.features.forEach(cd => {
        const geom = cd.geometry;
            cdmx_divFC.features.push( // se agrega el poligono de la alcaldia al fc
                turf.feature(geom, { nombre: cd.nomgeo || 'Desconocida' })
            )
        });
    }

    //cdmx_division.features.forEach(cd => {
    //    const geom = cd.geometry;
    //    cdmx_divFC.features.push( // se agrega el poligono de la alcaldia al fc
    //        turf.feature(geom, { nombre: cd.nomgeo || 'Desconocida' })
    //    )
    //});

    fetch('/api/reportes/') // se obtienen los reportes desde la API
        .then(response => response.json()) // se convierte la respuesta a JSON
        .then(reportes => {
            reportes.forEach(r => {
            const lat = parseFloat(r.latitud);
            const lng = parseFloat(r.longitud);
            if(Number.isFinite(lat) && Number.isFinite(lng)){
                clientesFC.features.push(
                    turf.point([lng, lat], { clienteId: String(r.gid) })
                );
            }})

            //function bboxFromFC(fc, pad = 0.7){ // recuadro que contiene todos los puntos del feature collection con un margen extra (pad)
            //    const b = turf.bbox(fc); // [minX, minY, maxX, maxY]
            //    return [b[0]-pad, b[1]-pad, b[2]+pad, b[3]+pad];
            //}
        
            //const bbox = bboxFromFC(semillasFC, 0.2); // rectangulo que delimita los celdas de voronoi
            //let vor = turf.voronoi(semillasFC, { bbox });
            const bboxCDMX = turf.bbox(cdmx_divFC); // recuadro que contiene toda la CDMX
            let vor = turf.voronoi(semillasFC, { bbox: bboxCDMX });
            vor.features = vor.features.map(cell => {
                let clipped = null;
                cdmx_divFC.features.forEach(alcaldiaPoly => {
                    const inter = turf.intersect(cell, alcaldiaPoly); // se devuelve el area de la interseccion entre la celda y alcaldia (si hay interseccion)
                    if (inter) {
                        if (!clipped) {
                            clipped = inter;
                        } else {
                            clipped = turf.union(clipped, inter);
                        }
                    }
                });
                return clipped ? clipped : null;
            }).filter(cell => cell !== null); // se eliminan las celdas que no intersectan con ninguna alcaldia
        
            if(!vor || !vor.features || vor.features.length === 0){
                alert('No se pudo generar Voronoi');
            }
        
            const asignaciones = {}; // se asignan los puntos clientes a las celdas de voronoi
            vor.features.forEach((cell, idx) => { // cell es un poligono (celda) del diagrama e idx es su indice
                // por cada celda, se encuentra la semilla propietaria
                const pin = turf.pointOnFeature(cell); // punto interior de la celda
                const semillaCercana = turf.nearestPoint(pin, semillasFC); // punto semilla más cercano a un punto interior de la celda (semilla propietaria de la celda)
                const semillaId = semillaCercana.properties.id;
                const semillaAlcaldia = semillaCercana.properties.alcaldia || semillaId; // alcaldia de la semilla o su id si no tiene alcaldia

                // guardar metadata en la celda
                cell.properties = cell.properties || {};
                cell.properties.semillaId = semillaId;
                cell.properties.semillaAlcaldia = semillaAlcaldia;
                cell.properties._idx = idx;

                // identificar los puntos clientes dentro de la celda
                const ptsIn = turf.pointsWithinPolygon(clientesFC, cell);
                asignaciones[semillaId] = ptsIn.features; // los clientes (reportes de incidencias) son asignados a la celda
                cell.properties.cantidadClientes = ptsIn.features.length; // cantidad de incidencias en la celda
            });

            function colorPorCantidad(cantidad, min, max){ // función para obtener un color basado en la cantidad de incidencias
                const t = (cantidad - min) / (max - min); // normaliza la cantidad entre 0 y 1

                // escala de azul (#1e40af) a rojo (#ef4444)
                const r = Math.round(30 + t * (239 - 30)); 
                const g = Math.round(64 + t * (68 - 64));
                const b = Math.round(175 + t * (68 - 175));
                // azul para min incidencias, rojo para max incidencias
                return `rgb(${r},${g},${b})`;
            }

            const cantidades = vor.features.map(f => f.properties.cantidadClientes); // array de cantidades de incidencias por celda
            const minCant = Math.min(...cantidades);
            const maxCant = Math.max(...cantidades);
        
            const vorLayer = L.geoJSON(vor, { // estetica y eventos de los poligonos de voronoi
                style: f => ({
                    color: '#111827',
                    weight: 1.2,
                    fillColor: colorPorCantidad(f.properties.cantidadClientes, minCant, maxCant),
                    fillOpacity: 0.45
                }),
                onEachFeature: (f, layer) => {
                    layer.bindPopup(
                        `Incidencias en esta seccion: <b>${f.properties.cantidadClientes}</b><br>`
                    );
                    layer.on('mouseover', e => e.target.setStyle({ weight: 2.2, fillOpacity: 0.4 }).bringToFront());
                    layer.on('mouseout',  e => vorLayer.resetStyle(e.target));
                }
            }).addTo(mapa);
        
            //const semillasLayer = L.geoJSON(semillasFC, { // estetica y eventos de los puntos representativos del cluster (semillas)
            //    pointToLayer: (f, latlng) => L.circleMarker(latlng, {
            //        radius: 6, weight: 2, color: '#0f172a', fillColor: '#fbbf24', fillOpacity: 0.9
            //    }),
            //    onEachFeature: (f, l) => l.bindTooltip(`Semilla: ${f.properties.semillaId || f.properties.semillaAlcaldia}`, {direction:'top'})
            //}).addTo(mapa);
        
            //const clientesLayer = L.geoJSON(clientesFC, {
            //    pointToLayer: (f, latlng) => L.circleMarker(latlng, {
            //        radius: 4, weight: 1, color: '#1d4ed8', fillColor: '#93c5fd', fillOpacity: 0.9
            //    }),
            //    onEachFeature: (f, l) => l.bindTooltip(`Punto: ${f.properties.clienteId}`, {direction:'top'})
            //}).addTo(mapa);
        
            mapa.fitBounds(vorLayer.getBounds());
        });
});