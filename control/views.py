import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Contenedor, Queja, QuejaContenedor, validate_iso_6346

logger = logging.getLogger(__name__)


def index(request):
    """Página principal con buscador de contenedores"""
    return render(request, "tracking/index.html")


def buscar_contenedor(request):
    """Busca un contenedor por código ISO (HTMX)"""
    codigo = request.GET.get("codigo", "").upper().strip()

    logger.debug(f"Búsqueda - código: {codigo}, es_htmx: {request.htmx}")

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


def validar_contenedor_queja(request):
    """Valida si un contenedor existe (HTMX) para el formulario de quejas"""
    codigo = request.GET.get("codigo", "").upper().strip()

    if not codigo:
        return HttpResponse("")

    # Validar formato ISO 6346
    try:
        validate_iso_6346(codigo)
    except ValidationError as e:
        error_msg = str(e.message) if hasattr(e, "message") else str(e.messages[0])
        return render(
            request,
            "tracking/partials/_contenedor_queja_error.html",
            {"error": error_msg, "codigo": codigo},
        )

    # Buscar contenedor
    try:
        contenedor = Contenedor.objects.select_related("transitario").get(
            codigo_iso=codigo
        )
        return render(
            request,
            "tracking/partials/_contenedor_queja_valido.html",
            {"contenedor": contenedor},
        )
    except Contenedor.DoesNotExist:
        return render(
            request,
            "tracking/partials/_contenedor_queja_error.html",
            {"error": "Contenedor no encontrado en el sistema", "codigo": codigo},
        )


def quejas_sugerencias(request):
    """Página de Quejas y Sugerencias"""
    # Obtener código de contenedor si viene desde detalle
    contenedor_codigo = request.GET.get("contenedor", "")
    contenedor_info = None

    if contenedor_codigo:
        try:
            contenedor_info = Contenedor.objects.select_related("transitario").get(
                codigo_iso=contenedor_codigo.upper()
            )
        except Contenedor.DoesNotExist:
            contenedor_info = None

    if request.method == "POST":
        # Procesar formulario de queja
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip()
        categoria = request.POST.get("categoria", "")
        descripcion = request.POST.get("descripcion", "").strip()
        contenedor_iso = request.POST.get("contenedor_iso", "").strip().upper()

        # Validaciones - TODOS los campos son obligatorios
        errors = []
        if not nombre:
            errors.append("El nombre es obligatorio.")
        if not email:
            errors.append("El correo electrónico es obligatorio.")
        if not categoria:
            errors.append("Debes seleccionar una categoría.")
        if not descripcion:
            errors.append("La descripción de la queja es obligatoria.")
        if not contenedor_iso:
            errors.append("El código de contenedor es obligatorio.")
        else:
            # Validar que el contenedor existe
            if not Contenedor.objects.filter(codigo_iso=contenedor_iso).exists():
                errors.append("El código de contenedor no existe en el sistema.")

        if errors:
            return render(
                request,
                "tracking/quejas.html",
                {
                    "errors": errors,
                    "contenedor_info": contenedor_info,
                    "contenedor_codigo": contenedor_codigo,
                    "categorias": Queja.CATEGORIA_CHOICES,
                    "form_data": {
                        "nombre": nombre,
                        "email": email,
                        "categoria": categoria,
                        "descripcion": descripcion,
                        "contenedor_iso": contenedor_iso,
                    },
                },
            )

        # Crear la queja
        queja = Queja.objects.create(
            nombre_cliente=nombre,
            email_cliente=email,
            categoria=categoria,
            descripcion=descripcion,
        )

        # Guardar imágenes (hasta 3)
        for key in ["imagen1", "imagen2", "imagen3"]:
            if key in request.FILES:
                setattr(queja, key, request.FILES[key])
        queja.save()

        # Vincular contenedor
        try:
            contenedor = Contenedor.objects.get(codigo_iso=contenedor_iso)
            QuejaContenedor.objects.create(queja=queja, contenedor=contenedor)
        except Contenedor.DoesNotExist:
            pass

        messages.success(
            request,
            "¡Tu queja ha sido registrada exitosamente! Nos comunicaremos contigo pronto.",
        )
        return redirect("control:quejas")

    # GET - Mostrar formulario
    return render(
        request,
        "tracking/quejas.html",
        {
            "contenedor_info": contenedor_info,
            "contenedor_codigo": contenedor_codigo,
            "categorias": Queja.CATEGORIA_CHOICES,
        },
    )
