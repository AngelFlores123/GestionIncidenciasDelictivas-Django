from django.shortcuts import render, redirect, get_object_or_404
from .models import ReportesIncidenciau
from django.core.paginator import Paginator

# Create your views here.
def home(request):
    reportes_list = ReportesIncidenciau.objects.all()  # Obtiene todos los reportes de la base de datos
    categoria = request.GET.get('categoria_filtro')
    impacto = request.GET.get('impacto_filtro')
    alcaldia = request.GET.get('alcaldia_filtro')
    fecha = request.GET.get('fecha_filtro')

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

    context = {
        'reportesID': pagina,
        'categoria': categoria,
        'impacto': impacto,
        'alcaldia': alcaldia,
        'fecha': fecha,
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