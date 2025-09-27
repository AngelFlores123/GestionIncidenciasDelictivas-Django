# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class ReportesIncidenciau(models.Model):
    gid = models.AutoField(primary_key=True)
    id_delito = models.CharField()
    delito = models.CharField()
    categoria_delito = models.CharField()
    impacto_delito = models.CharField()
    anio_hecho = models.IntegerField()
    mes_hecho = models.CharField()
    alcaldia = models.CharField()
    cve_col = models.CharField()
    colonia = models.CharField()
    latitud = models.FloatField()
    longitud = models.FloatField()
    geom = models.PointField(srid=32614)

    def __str__(self):
        return self.gid

    class Meta:
        managed = False # indica que Django no debe gestionar la tabla (crear, modificar o eliminar)
        db_table = 'reportes_incidenciau'

class LimiteDeLasAlcaldas(models.Model):
    laid = models.AutoField(primary_key=True)
    wkb_geometry = models.PolygonField(blank=True, null=True)
    cvegeo = models.CharField(blank=True, null=True)
    cve_ent = models.CharField(blank=True, null=True)
    cve_mun = models.CharField(blank=True, null=True)
    nomgeo = models.CharField(blank=True, null=True) # nombre de la alcaldia

    class Meta:
        managed = False
        db_table = 'limite_de_las_alcaldas'