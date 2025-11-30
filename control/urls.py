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
    # PDFs - Admin
    path(
        "pdf/ficha/<str:codigo_iso>/",
        views.pdf_ficha_contenedor,
        name="pdf_ficha_contenedor",
    ),
    path(
        "pdf/manifiesto/<int:arribo_id>/",
        views.pdf_manifiesto_arribo,
        name="pdf_manifiesto_arribo",
    ),
    path(
        "pdf/gate-pass/<str:codigo_iso>/",
        views.pdf_gate_pass,
        name="pdf_gate_pass",
    ),
    # PDF - Cliente (versión censurada)
    path(
        "pdf/tracking/<str:codigo_iso>/",
        views.pdf_cliente_contenedor,
        name="pdf_cliente_contenedor",
    ),
]
