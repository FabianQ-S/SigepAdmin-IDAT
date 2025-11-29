from django.urls import path

from . import views

app_name = "control"

urlpatterns = [
    path("", views.index, name="index"),
    path("buscar/", views.buscar_contenedor, name="buscar"),
    path("tracking/<str:codigo_iso>/", views.detalle_contenedor, name="detalle"),
    path("sobre-nosotros/", views.sobre_nosotros, name="sobre_nosotros"),
    path("quejas/", views.quejas_sugerencias, name="quejas"),
    path(
        "quejas/validar-contenedor/",
        views.validar_contenedor_queja,
        name="validar_contenedor_queja",
    ),
]
