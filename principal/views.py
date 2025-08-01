from django.shortcuts import render, redirect, get_object_or_404
from .models import ReportesIncidenciau
from django.core.paginator import Paginator
import json
import random
from collections import defaultdict
import numpy as np

# Create your views here.
def home(request):
    reportes_list = ReportesIncidenciau.objects.all()  # Obtiene todos los reportes de la base de datos
    categoria = request.GET.get('categoria_filtro')
    impacto = request.GET.get('impacto_filtro')
    alcaldia = request.GET.get('alcaldia_filtro')
    fecha = request.GET.get('fecha_filtro')
    gruposIncidencias = request.GET.get('grupos_incidencias')

    # FILTROS

    if categoria: # si se selecciona una categoria, filtra los reportes por esa categoria
        reportes_list = reportes_list.filter(
            categoria_delito__icontains=categoria
        )
    if impacto:
        reportes_list = reportes_list.filter(
            impacto_delito__icontains=impacto
        )
    if alcaldia:
        reportes_list = reportes_list.filter(
            alcaldia__icontains=alcaldia
        )
    if fecha:
        if fecha == 'mas reciente':
            reportes_list = reportes_list.order_by('-anio_hecho')
        elif fecha == 'menos reciente':
            reportes_list = reportes_list.order_by('anio_hecho')

    paginador = Paginator(reportes_list, 15) # numero de reportes por pagina
    no_pag = request.GET.get('page')
    pagina = paginador.get_page(no_pag)

    # AGRUPAMIENTO DE INCIDENCIAS

    ubicaciones = list(ReportesIncidenciau.objects.values('gid', 'id_delito', 'latitud', 'longitud'))

    # Si se selecciona un grupo de incidencias, limita el numero de reportes en el mapa
    n = int(gruposIncidencias) if gruposIncidencias else 10
    n = min(n, len(ubicaciones))  # se limita n al tamano de la lista (no es necesario ya que en el template se limita el numero de reportes a mostrar)
    centroidesK = random.sample(ubicaciones, n) # selecciona n elementos aleatorios sin repetición
    
    # se vectorizan las ubicaciones de las incidencias y los centroides 
    ubicaciones_np = np.array([[u['latitud'], u['longitud']] for u in ubicaciones])
    centroides_np = np.array([[c['latitud'], c['longitud']] for c in centroidesK])
    distancias = np.linalg.norm(ubicaciones_np[:, np.newaxis, :] - centroides_np[np.newaxis, :, :], axis=2)  # calcula la distancia euclidiana entre cada ubicacion y cada centroide
    indices_min = np.argmin(distancias, axis=1)  # devuelve los indices de los centroides mas cercanos a cada ubicacion

    clusters = defaultdict(list)
    for idx_ubic, idx_centroide in enumerate(indices_min):
        centroide_gid = centroidesK[idx_centroide]['gid'] # obtiene el gid del centroide con el indice idx_centroide
        clusters[centroide_gid].append(ubicaciones[idx_ubic]) # agrupa las ubicaciones por el gid del centroide mas cercano
        
    # se saca el promedio de las ubicaciones de cada cluster para obtener un nuevo centroide mas representativo
    for centroide_gid, ubicaciones_cluster in clusters.items():
        latitudes = [u['latitud'] for u in ubicaciones_cluster]
        longitudes = [u['longitud'] for u in ubicaciones_cluster]
        promedio_lat = sum(latitudes) / len(latitudes)
        promedio_long = sum(longitudes) / len(longitudes)
        clusters[centroide_gid] = {
            'gid': centroide_gid,
            'latitud': promedio_lat,
            'longitud': promedio_long,
            #'ubicaciones': ubicaciones_cluster
            'noIncidencias': len(ubicaciones_cluster)  # numero de incidencias en el cluster
        }

    #for ubicacion in ubicaciones:
    #    distancias = {}
    #    for centroideK in centroidesK:
    #        distancia = ((ubicacion['latitud'] - centroideK['latitud']) ** 2 + (ubicacion['longitud'] - centroideK['longitud']) ** 2) ** 0.5
    #        distancias[centroideK['gid']] = distancia
    #    centroide_min = min(distancias, key=distancias.get) # gid (clave) del centroide con la distancia minima a la ubicacion actual
    #    clusters[centroide_min].append(ubicacion) # coloca la ubicacion en el cluster del centroide minimo correspondiente 

    context = {
        'reportesID': pagina,
        'categoria': categoria,
        'impacto': impacto,
        'alcaldia': alcaldia,
        'fecha': fecha,
        'gruposIncidencias': gruposIncidencias,
        #'ubicaciones': ubicaciones  # Convierte las ubicaciones a formato JSON para usar en el mapa
        'clusters': json.dumps(list(clusters.values())),  # convierte los clusters a formato JSON para usar en el mapa
    }
    
    return render(request, 'principal.html', context)

def crear_reporte(request):
    return render(request, 'crear_reporte.html')

def guardar_reporte(request):
    idDelito = request.POST.get('anio_hecho') + request.POST.get('mes_hecho') + request.POST.get('hora_delito') 
    delito = request.POST.get('delito')
    categoriaDelito = request.POST.get('categoria_delito')
    impactoDelito = request.POST.get('impacto_delito')
    anioHecho = request.POST.get('anio_hecho')
    mesHecho = request.POST.get('mes_hecho')
    alcaldia = request.POST.get('alcaldia')
    cveCol = request.POST.get('cve_col')
    colonia = request.POST.get('colonia')
    latitud = request.POST.get('latitud')
    longitud = request.POST.get('longitud')
    geom = f'SRID=32614;POINT({longitud} {latitud})' # dormato WKT (Well-Known Text), sirve para representar geometrías en texto

    nuevoReporte = ReportesIncidenciau.objects.create(
        id_delito=idDelito,
        delito=delito,
        categoria_delito=categoriaDelito,
        impacto_delito=impactoDelito,
        anio_hecho=anioHecho,
        mes_hecho=mesHecho,
        alcaldia=alcaldia,
        cve_col=cveCol,
        colonia=colonia,
        latitud=latitud,
        longitud=longitud,
        geom=geom
    )

    return redirect('/')

def eliminar_reporte(request, gid):
    reporte = get_object_or_404(ReportesIncidenciau, gid=gid)
    reporte.delete()
    return redirect('/')

def editar_reporte(request, gid): # tambien servira para visualizar informacion del reporte, incluyendo el mapa con la ubicacion del delito
    reporte = get_object_or_404(ReportesIncidenciau, gid=gid)
    return render(request, 'editar_reporte.html', {'reporte': reporte})

def actualizar_reporte(request, gid):
    reporte = get_object_or_404(ReportesIncidenciau, gid=gid)
    
    reporte.id_delito = request.POST.get('id_delito')
    reporte.delito = request.POST.get('delito')
    reporte.categoria_delito = request.POST.get('categoria_delito')
    reporte.impacto_delito = request.POST.get('impacto_delito')
    reporte.anio_hecho = request.POST.get('anio_hecho')
    reporte.mes_hecho = request.POST.get('mes_hecho')
    reporte.alcaldia = request.POST.get('alcaldia')
    reporte.cve_col = request.POST.get('cve_col')
    reporte.colonia = request.POST.get('colonia')
    reporte.latitud = request.POST.get('latitud')
    reporte.longitud = request.POST.get('longitud')
    reporte.geom = f'SRID=32614;POINT({reporte.longitud} {reporte.latitud})'
    
    reporte.save()
    
    return redirect('/')

#def ver_reporte(request, gid):
#    reporte = get_object_or_404(ReportesIncidenciau, gid=gid)
#    return render(request, 'principal/ver_reporte.html', {'reporte': reporte})