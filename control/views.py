import base64
import logging
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_GET

from .imo_client import imo_client
from .models import Arribo, Contenedor, Queja, QuejaContenedor, validate_iso_6346
from .sunat_client import sunat_client

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


# =============================================
# GENERACIÓN DE PDFs CON WEASYPRINT
# =============================================


def _get_logo_base64(logo_name):
    """Obtiene el logo como base64 para incrustar en el PDF"""
    logo_path = Path(settings.BASE_DIR) / "theme" / "static" / "images" / logo_name
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None


def _generate_pdf_response(html_content, filename):
    """Genera una respuesta HTTP con el PDF usando WeasyPrint"""
    try:
        from weasyprint import HTML
    except ImportError:
        return HttpResponse(
            "WeasyPrint no está instalado. Ejecute: pip install weasyprint",
            status=500,
        )

    pdf = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def pdf_ficha_contenedor(request, codigo_iso):
    """
    Genera PDF de Ficha Completa del Contenedor (Admin)
    Incluye toda la información: datos, origen/destino, aprobaciones, timeline
    """
    contenedor = get_object_or_404(
        Contenedor.objects.select_related(
            "arribo",
            "arribo__buque",
            "transitario",
            "aprobacion_aduanera",
            "aprobacion_financiera",
            "aprobacion_pago_transitario",
        ).prefetch_related("eventos"),
        codigo_iso=codigo_iso.upper(),
    )

    eventos = contenedor.eventos.select_related("buque").order_by("-fecha_hora")
    logo_base64 = _get_logo_base64("SigepAdminLogo.jpeg")

    html_content = render_to_string(
        "pdf/admin_ficha_contenedor.html",
        {
            "contenedor": contenedor,
            "eventos": eventos,
            "logo_base64": logo_base64,
            "fecha_generacion": timezone.now(),
        },
    )

    filename = f"ficha_contenedor_{codigo_iso}_{timezone.now().strftime('%Y%m%d')}.pdf"
    return _generate_pdf_response(html_content, filename)


def pdf_manifiesto_arribo(request, arribo_id):
    """
    Genera PDF del Manifiesto de Arribo (Admin)
    Lista de todos los contenedores asociados al arribo de un buque
    """
    arribo = get_object_or_404(
        Arribo.objects.select_related("buque").prefetch_related(
            "contenedores",
            "contenedores__transitario",
            "contenedores__aprobacion_aduanera",
            "contenedores__aprobacion_financiera",
        ),
        pk=arribo_id,
    )

    contenedores = arribo.contenedores.all().order_by("direccion", "codigo_iso")
    total_import = contenedores.filter(direccion="IMPORT").count()
    total_export = contenedores.filter(direccion="EXPORT").count()

    # Resumen por transitario
    transitarios_dict = defaultdict(lambda: {"total": 0, "import": 0, "export": 0})
    for c in contenedores:
        nombre = c.transitario.nombre_comercial if c.transitario else "Sin transitario"
        transitarios_dict[nombre]["total"] += 1
        if c.direccion == "IMPORT":
            transitarios_dict[nombre]["import"] += 1
        else:
            transitarios_dict[nombre]["export"] += 1

    resumen_transitarios = [{"nombre": k, **v} for k, v in transitarios_dict.items()]

    logo_base64 = _get_logo_base64("SigepAdminLogo.jpeg")

    html_content = render_to_string(
        "pdf/admin_manifiesto_arribo.html",
        {
            "arribo": arribo,
            "contenedores": contenedores,
            "total_import": total_import,
            "total_export": total_export,
            "resumen_transitarios": resumen_transitarios,
            "logo_base64": logo_base64,
            "fecha_generacion": timezone.now(),
        },
    )

    buque_name = arribo.buque.nombre.replace(" ", "_")
    fecha = arribo.fecha_eta.strftime("%Y%m%d")
    filename = f"manifiesto_arribo_{buque_name}_{fecha}.pdf"
    return _generate_pdf_response(html_content, filename)


def pdf_gate_pass(request, codigo_iso):
    """
    Genera PDF del Gate Pass / Orden de Entrega (Admin)
    Documento de autorización para retiro del contenedor
    Solo se genera si todas las aprobaciones están completas
    """
    contenedor = get_object_or_404(
        Contenedor.objects.select_related(
            "arribo",
            "arribo__buque",
            "transitario",
            "aprobacion_aduanera",
            "aprobacion_financiera",
            "aprobacion_pago_transitario",
        ),
        codigo_iso=codigo_iso.upper(),
    )

    # Verificar que todas las aprobaciones estén completas
    aduana_ok = contenedor.esta_liberado_aduana
    pago_ok = contenedor.esta_pagado
    transitario_ok = contenedor.transitario_ha_pagado

    if not (aduana_ok and pago_ok and transitario_ok):
        return HttpResponse(
            "No se puede generar Gate Pass: faltan aprobaciones pendientes.",
            status=400,
        )

    fecha_emision = timezone.now()
    horas_validez = 48
    fecha_vencimiento = fecha_emision + timedelta(hours=horas_validez)

    logo_base64 = _get_logo_base64("SigepAdminLogo.jpeg")

    html_content = render_to_string(
        "pdf/admin_gate_pass.html",
        {
            "contenedor": contenedor,
            "fecha_emision": fecha_emision,
            "fecha_vencimiento": fecha_vencimiento,
            "horas_validez": horas_validez,
            "logo_base64": logo_base64,
        },
    )

    filename = f"gate_pass_{codigo_iso}_{fecha_emision.strftime('%Y%m%d')}.pdf"
    return _generate_pdf_response(html_content, filename)


def pdf_cliente_contenedor(request, codigo_iso):
    """
    Genera PDF de Ficha del Contenedor para Cliente (Censurado)
    Versión pública con información sensible oculta
    """
    contenedor = get_object_or_404(
        Contenedor.objects.select_related(
            "arribo",
            "arribo__buque",
            "transitario",
            "aprobacion_aduanera",
            "aprobacion_financiera",
            "aprobacion_pago_transitario",
        ).prefetch_related("eventos"),
        codigo_iso=codigo_iso.upper(),
    )

    eventos = contenedor.eventos.select_related("buque").order_by("-fecha_hora")[:10]
    ultimo_evento = contenedor.eventos.order_by("-fecha_hora").first()
    logo_base64 = _get_logo_base64("NuevoLogo.png")

    html_content = render_to_string(
        "pdf/cliente_ficha_contenedor.html",
        {
            "contenedor": contenedor,
            "eventos": eventos,
            "ultimo_evento": ultimo_evento,
            "logo_base64": logo_base64,
            "fecha_generacion": timezone.now(),
        },
    )

    filename = f"seguimiento_{codigo_iso}_{timezone.now().strftime('%Y%m%d')}.pdf"
    return _generate_pdf_response(html_content, filename)


# =============================================
# API CONSULTA SUNAT (RUC)
# =============================================


@staff_member_required
@require_GET
def consultar_ruc_sunat(request, ruc):
    """
    API interna para consultar RUC en SUNAT.
    Solo accesible para usuarios staff (administradores).

    Args:
        ruc: Número de RUC (11 dígitos)

    Returns:
        JsonResponse con los datos normalizados del contribuyente
    """
    # Consultar SUNAT
    datos_raw = sunat_client.consultar(ruc)

    # Normalizar datos
    datos = sunat_client.normalizar_datos(datos_raw)

    return JsonResponse(datos)


# =============================================
# API CONSULTA IMO (BUQUES)
# =============================================


@staff_member_required
@require_GET
def consultar_imo_buque(request, imo):
    """
    API interna para consultar información de buques por IMO.
    Solo accesible para usuarios staff (administradores).

    Args:
        imo: Número IMO del buque (7 dígitos)

    Returns:
        JsonResponse con los datos normalizados del buque
    """
    # Consultar API de IMO
    datos = imo_client.consultar_imo(imo)

    return JsonResponse(datos)


@staff_member_required
@require_GET
def obtener_datos_arribo(request, arribo_id):
    """
    API interna para obtener datos de un arribo.
    Usado para auto-llenar campos del formulario de contenedor.

    Args:
        arribo_id: ID del arribo

    Returns:
        JsonResponse con datos del arribo para auto-llenado
    """
    try:
        arribo = Arribo.objects.select_related("buque").get(pk=arribo_id)

        # Obtener transitario asociado si existe (del primer contenedor o de relación directa)
        transitario_nombre = ""
        if hasattr(arribo, "transitario") and arribo.transitario:
            transitario_nombre = arribo.transitario.razon_social

        datos = {
            "success": True,
            "arribo": {
                "id": arribo.id,
                "tipo_operacion": arribo.tipo_operacion,
                "buque_nombre": arribo.buque.nombre,
                "naviera": arribo.buque.naviera or arribo.buque.nombre,
                "fecha_eta": arribo.fecha_eta.isoformat() if arribo.fecha_eta else None,
                "fecha_etd": arribo.fecha_etd.isoformat() if arribo.fecha_etd else None,
                "transitario_nombre": transitario_nombre,
                "muelle": arribo.muelle_berth,
            },
        }

        return JsonResponse(datos)

    except Arribo.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Arribo no encontrado"}, status=404
        )


def api_contenedor_data(request, contenedor_id):
    """
    API interna para obtener datos de un contenedor.
    Usado para auto-llenar el transitario en el formulario de pago.

    Args:
        contenedor_id: ID del contenedor

    Returns:
        JsonResponse con datos del contenedor incluyendo transitario
    """
    try:
        contenedor = Contenedor.objects.select_related("transitario").get(
            pk=contenedor_id
        )

        datos = {
            "success": True,
            "contenedor": {
                "id": contenedor.id,
                "codigo_iso": contenedor.codigo_iso,
                "direccion": contenedor.direccion,
            },
            "transitario": {
                "id": contenedor.transitario.id,
                "nombre": contenedor.transitario.razon_social,
                "nombre_comercial": contenedor.transitario.nombre_comercial or "",
            }
            if contenedor.transitario
            else None,
        }

        return JsonResponse(datos)

    except Contenedor.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Contenedor no encontrado"}, status=404
        )
