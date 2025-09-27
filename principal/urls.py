from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('crear_reporte/', views.crear_reporte),
    path('crear_reporte/guardar_reporte/', views.guardar_reporte),
    path('eliminar_reporte/<gid>/', views.eliminar_reporte),
    path('editar_reporte/<gid>/', views.editar_reporte),
    path('editar_reporte/actualizar_reporte/<gid>/', views.actualizar_reporte),
    path('api/reportes/', views.api_reportes, name='api_reportes'), # api para transferir datos de reportes en formato JSON
]