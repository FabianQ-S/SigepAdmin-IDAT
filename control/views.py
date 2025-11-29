from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Contenedor, validate_iso_6346


def index(request):
    """Página principal con buscador de contenedores"""
    return render(request, "tracking/index.html")


def buscar_contenedor(request):
    """Busca un contenedor por código ISO (HTMX)"""
    codigo = request.GET.get("codigo", "").upper().strip()

    # Debug: imprimir si es HTMX
    print(f"[DEBUG] Búsqueda - código: {codigo}, es_htmx: {request.htmx}")

    if not codigo:
        return HttpResponse("")

    # Validar formato ISO 6346
    try:
        validate_iso_6346(codigo)
    except ValidationError as e:
        return render(
            request,
            "tracking/partials/_error.html",
            {"error": str(e.message) if hasattr(e, "message") else str(e.messages[0])},
        )

    # Buscar contenedor
    try:
        contenedor = (
            Contenedor.objects.select_related("arribo", "arribo__buque", "transitario")
            .prefetch_related("eventos")
            .get(codigo_iso=codigo)
        )

        ultimo_evento = contenedor.eventos.order_by("-fecha_hora").first()

        return render(
            request,
            "tracking/partials/_resultado.html",
            {
                "contenedor": contenedor,
                "ultimo_evento": ultimo_evento,
            },
        )
    except Contenedor.DoesNotExist:
        return render(
            request, "tracking/partials/_no_encontrado.html", {"codigo": codigo}
        )


def detalle_contenedor(request, codigo_iso):
    """Página de detalle del contenedor con timeline completo"""
    contenedor = get_object_or_404(
        Contenedor.objects.select_related(
            "arribo", "arribo__buque", "transitario"
        ).prefetch_related("eventos"),
        codigo_iso=codigo_iso.upper(),
    )

    eventos = contenedor.eventos.select_related("buque").order_by("-fecha_hora")

    # Obtener aprobaciones (pueden no existir)
    aprobacion_financiera = getattr(contenedor, "aprobacion_financiera", None)
    aprobacion_aduanera = getattr(contenedor, "aprobacion_aduanera", None)

    return render(
        request,
        "tracking/detalle.html",
        {
            "contenedor": contenedor,
            "eventos": eventos,
            "aprobacion_financiera": aprobacion_financiera,
            "aprobacion_aduanera": aprobacion_aduanera,
        },
    )


def sobre_nosotros(request):
    """Página Sobre Nosotros"""
    return render(request, "tracking/sobre_nosotros.html")


def quejas_sugerencias(request):
    """Página de Quejas y Sugerencias"""
    return render(request, "tracking/quejas.html")
