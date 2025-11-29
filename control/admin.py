from django.contrib import admin, messages
from django.utils.html import format_html

from .models import (
    AprobacionAduanera,
    AprobacionFinanciera,
    AprobacionPagoTransitario,
    Arribo,
    Buque,
    Contenedor,
    EventoContenedor,
    Queja,
    QuejaContenedor,
    Transitario,
)


# ====== BUQUE ADMIN ======
@admin.register(Buque)
class BuqueAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "imo_number",
        "naviera",
        "pabellon_bandera",
        "teu_capacidad",
        "total_arribos",
    ]
    list_filter = ["naviera", "pabellon_bandera"]
    search_fields = ["nombre", "imo_number", "naviera", "callsign"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Información Básica",
            {"fields": ("nombre", "imo_number", "pabellon_bandera", "naviera")},
        ),
        (
            "Especificaciones Técnicas",
            {
                "fields": (
                    "eslora_metros",
                    "manga_metros",
                    "calado_metros",
                    "teu_capacidad",
                )
            },
        ),
        ("Identificación", {"fields": ("puerto_registro", "callsign")}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def total_arribos(self, obj):
        count = obj.arribos.count()
        return format_html("<strong>{}</strong> arribos", count)

    total_arribos.short_description = "Total Arribos"

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar si tiene arribos asociados
        if obj and obj.arribos.exists():
            return False
        return super().has_delete_permission(request, obj)


# ====== TRANSITARIO ADMIN ======
@admin.register(Transitario)
class TransitarioAdmin(admin.ModelAdmin):
    list_display = [
        "razon_social",
        "nombre_comercial",
        "identificador_tributario",
        "tipo_servicio",
        "estado_operacion",
        "especialidad",
        "total_contenedores",
        "calificacion",
    ]
    list_filter = [
        "estado_operacion",
        "tipo_servicio",
        "especialidad",
        "es_activo",
        "pais",
    ]
    search_fields = [
        "razon_social",
        "nombre_comercial",
        "identificador_tributario",
        "contacto_principal",
        "email_contacto",
    ]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Información de la Empresa",
            {
                "fields": (
                    "razon_social",
                    "nombre_comercial",
                    "identificador_tributario",
                    "codigo_scac",
                    "tipo_servicio",
                    "especialidad",
                )
            },
        ),
        ("Ubicación", {"fields": ("pais", "ciudad", "direccion")}),
        (
            "Contacto",
            {
                "fields": (
                    "contacto_principal",
                    "telefono_contacto",
                    "telefono_emergencia",
                    "email_contacto",
                    "email_facturacion",
                    "sitio_web",
                )
            },
        ),
        (
            "Operación",
            {
                "fields": (
                    "estado_operacion",
                    "licencia_operador",
                    "fecha_vencimiento_licencia",
                    "zona_cobertura",
                    "limite_credito",
                    "calificacion",
                    "es_activo",
                )
            },
        ),
        ("Observaciones", {"fields": ("observaciones",), "classes": ("collapse",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def total_contenedores(self, obj):
        count = obj.contenedores.count()
        return format_html("<strong>{}</strong> contenedores", count)

    total_contenedores.short_description = "Total Contenedores"


# ====== INLINE PARA CONTENEDORES EN ARRIBO ======
class ContenedorInline(admin.TabularInline):
    model = Contenedor
    extra = 0
    fields = [
        "codigo_iso",
        "direccion",
        "tipo_tamaño",
        "transitario",
        "bl_referencia",
        "ubicacion_actual",
    ]
    readonly_fields = []
    can_delete = True
    show_change_link = True


# ====== INLINE PARA EVENTOS EN CONTENEDOR ======
class EventoContenedorInline(admin.TabularInline):
    model = EventoContenedor
    extra = 1
    fields = [
        "tipo_evento",
        "fecha_hora",
        "ubicacion_puerto",
        "ubicacion_ciudad",
        "ubicacion_pais",
        "buque",
        "medio_transporte",
        "referencia_viaje",
    ]
    readonly_fields = []
    can_delete = True
    ordering = ["-fecha_hora"]
    autocomplete_fields = ["buque"]
    classes = ["collapse"]
    verbose_name = "Evento de Tracking"
    verbose_name_plural = "Timeline de Eventos"


# ====== ARRIBO ADMIN ======
@admin.register(Arribo)
class ArriboAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "buque",
        "fecha_eta",
        "fecha_etd",
        "tipo_operacion",
        "estado",
        "contenedores_descarga",
        "contenedores_carga",
        "total_contenedores_badge",
    ]
    list_filter = ["estado", "tipo_operacion", "fecha_eta", "buque__naviera"]
    search_fields = ["buque__nombre", "buque__imo_number", "muelle_berth"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "fecha_eta"
    inlines = [ContenedorInline]

    fieldsets = (
        (
            "Información del Arribo",
            {"fields": ("buque", "estado", "tipo_operacion", "muelle_berth")},
        ),
        ("Fechas", {"fields": ("fecha_eta", "fecha_etd", "fecha_arribo_real")}),
        (
            "Capacidad Declarada",
            {
                "fields": (
                    "contenedores_descarga",
                    "contenedores_carga",
                    "servicios_contratados",
                ),
                "description": "Cantidad de contenedores declarados para descarga (import) y carga (export)",
            },
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def total_contenedores(self, obj):
        """Total de contenedores registrados en el sistema"""
        return obj.contenedores.count()

    total_contenedores.short_description = "Contenedores Registrados"

    def total_contenedores_badge(self, obj):
        """Badge visual para contenedores"""
        total = obj.contenedores.count()
        declarado = obj.contenedores_descarga + obj.contenedores_carga
        color = (
            "green" if total == declarado else "orange" if total < declarado else "red"
        )
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}/{}</span>',
            color,
            total,
            declarado,
        )

    total_contenedores_badge.short_description = "Contenedores (Real/Declarado)"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Mensaje informativo sobre contenedores
        total = obj.contenedores.count()
        declarado = obj.contenedores_descarga + obj.contenedores_carga
        if total < declarado:
            messages.warning(
                request, f"Faltan {declarado - total} contenedores por registrar."
            )
        elif total > declarado:
            messages.error(
                request, f"Hay {total - declarado} contenedores de más registrados."
            )


# ====== CONTENEDOR ADMIN ======
@admin.register(Contenedor)
class ContenedorAdmin(admin.ModelAdmin):
    list_display = [
        "codigo_iso",
        "arribo",
        "direccion",
        "tipo_tamaño",
        "carrier",
        "ruta_resumen",
        "ultimo_estado_badge",
        "aprobaciones_badge",
        "estado_completo_badge",
    ]
    list_filter = [
        "direccion",
        "tipo_tamaño",
        "mercancia_peligrosa",
        "transitario",
        "arribo__buque",
        "carrier",
    ]
    search_fields = [
        "codigo_iso",
        "bl_referencia",
        "transitario__razon_social",
        "transitario__nombre_comercial",
        "destino_puerto",
        "origen_puerto",
        "carrier",
    ]
    readonly_fields = ["created_at", "updated_at", "ultimo_estado_badge"]
    date_hierarchy = "created_at"
    autocomplete_fields = ["arribo", "transitario"]
    inlines = [EventoContenedorInline]

    fieldsets = (
        (
            "Información Básica",
            {
                "fields": (
                    "codigo_iso",
                    "bic_propietario",
                    "arribo",
                    "direccion",
                    "tipo_tamaño",
                    "transitario",
                    "carrier",
                )
            },
        ),
        ("Documentación", {"fields": ("bl_referencia", "numero_sello")}),
        (
            "Origen",
            {
                "fields": (
                    "origen_pais",
                    "origen_ciudad",
                    "origen_puerto",
                    "remitente",
                ),
                "description": "Información del punto de origen del contenedor",
            },
        ),
        (
            "Destino",
            {
                "fields": (
                    "destino_pais",
                    "destino_ciudad",
                    "destino_puerto",
                    "consignatario",
                    "fecha_eta_destino",
                ),
                "description": "Información del punto de destino del contenedor",
            },
        ),
        (
            "Contenido y Pesos",
            {
                "fields": (
                    "mercancia_declarada",
                    "mercancia_peligrosa",
                    "peso_bruto_kg",
                    "tara_kg",
                )
            },
        ),
        (
            "Ubicación y Fechas",
            {"fields": ("ubicacion_actual", "fecha_retiro_transitario")},
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def ruta_resumen(self, obj):
        """Muestra resumen de la ruta origen -> destino"""
        origen = obj.origen_puerto or obj.origen_ciudad or obj.origen_pais or "?"
        destino = obj.destino_puerto or obj.destino_ciudad or obj.destino_pais or "?"
        return f"{origen} → {destino}"

    ruta_resumen.short_description = "Ruta"

    def ultimo_estado_badge(self, obj):
        """Muestra el último evento/estado del contenedor"""
        evento = obj.ultimo_evento
        if evento:
            color_map = {
                "GATE_OUT_EMPTY": "#6c757d",
                "GATE_IN_FULL": "#17a2b8",
                "LOADED": "#007bff",
                "DEPARTED": "#6610f2",
                "IN_TRANSIT": "#fd7e14",
                "TRANSSHIPMENT": "#e83e8c",
                "ARRIVED": "#20c997",
                "DISCHARGED": "#28a745",
                "GATE_OUT_FULL": "#28a745",
                "DELIVERED": "#155724",
                "GATE_IN_EMPTY": "#6c757d",
                "CUSTOMS_HOLD": "#dc3545",
                "CUSTOMS_RELEASED": "#28a745",
                "INSPECTION": "#ffc107",
                "DAMAGED": "#dc3545",
            }
            color = color_map.get(evento.tipo_evento, "#6c757d")
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span><br>'
                '<small style="color: #666;">{} - {}</small>',
                color,
                evento.get_tipo_evento_display(),
                evento.ubicacion_puerto,
                evento.fecha_hora.strftime("%d/%m/%Y"),
            )
        return format_html('<span style="color: #999;">Sin eventos</span>')

    ultimo_estado_badge.short_description = "Último Estado"

    def aprobaciones_badge(self, obj):
        """Muestra el estado de aprobaciones"""
        aprobaciones = []

        # Aprobación Aduanera
        if hasattr(obj, "aprobacion_aduanera"):
            estado = "APROBADO" if obj.aprobacion_aduanera.aprobado else "PENDIENTE"
            aprobaciones.append(("🛃 Aduana", estado))
        else:
            aprobaciones.append(("🛃 Aduana", "PENDIENTE"))

        # Aprobación Financiera
        if hasattr(obj, "aprobacion_financiera"):
            estado = "APROBADO" if obj.aprobacion_financiera.aprobado else "PENDIENTE"
            aprobaciones.append(("💰 Financiera", estado))
        else:
            aprobaciones.append(("💰 Financiera", "PENDIENTE"))

        # Aprobación Pago Transitario
        if hasattr(obj, "aprobacion_pago_transitario"):
            estado = (
                "PAGADO"
                if obj.aprobacion_pago_transitario.pago_realizado
                else "PENDIENTE"
            )
            aprobaciones.append(("🚚 Transitario", estado))
        else:
            aprobaciones.append(("🚚 Transitario", "PENDIENTE"))

        html = "<div>"
        for nombre, estado in aprobaciones:
            color = {
                "APROBADO": "green",
                "RECHAZADO": "red",
                "PENDIENTE": "orange",
                "PAGADO": "green",
            }.get(estado, "gray")
            html += f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 3px; margin: 2px; display: inline-block; font-size: 11px;">{nombre}: {estado}</span><br>'
        html += "</div>"
        return format_html(html)

    aprobaciones_badge.short_description = "Aprobaciones"

    def estado_completo_badge(self, obj):
        """Badge del estado completo del contenedor"""
        # Verificar si todas las aprobaciones están OK
        aduana_ok = (
            hasattr(obj, "aprobacion_aduanera") and obj.aprobacion_aduanera.aprobado
        )
        financiera_ok = (
            hasattr(obj, "aprobacion_financiera") and obj.aprobacion_financiera.aprobado
        )
        transitario_ok = (
            hasattr(obj, "aprobacion_pago_transitario")
            and obj.aprobacion_pago_transitario.pago_realizado
        )

        if aduana_ok and financiera_ok and transitario_ok:
            return format_html(
                '<span style="background-color: green; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">✓ LISTO PARA RETIRO</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 5px 10px; border-radius: 3px;">⏳ EN PROCESO</span>'
            )

    estado_completo_badge.short_description = "Estado General"

    actions = ["marcar_listo_retiro", "verificar_aprobaciones"]

    def marcar_listo_retiro(self, request, queryset):
        """Acción para verificar y marcar contenedores listos para retiro"""
        count = 0
        for contenedor in queryset:
            aduana_ok = (
                hasattr(contenedor, "aprobacion_aduanera")
                and contenedor.aprobacion_aduanera.aprobado
            )
            financiera_ok = (
                hasattr(contenedor, "aprobacion_financiera")
                and contenedor.aprobacion_financiera.aprobado
            )
            transitario_ok = (
                hasattr(contenedor, "aprobacion_pago_transitario")
                and contenedor.aprobacion_pago_transitario.pago_realizado
            )

            if aduana_ok and financiera_ok and transitario_ok:
                count += 1

        if count > 0:
            messages.success(
                request, f"{count} contenedor(es) están listos para retiro."
            )
        else:
            messages.warning(
                request, "Ningún contenedor seleccionado está listo para retiro."
            )

    marcar_listo_retiro.short_description = "Verificar contenedores listos para retiro"

    def verificar_aprobaciones(self, request, queryset):
        """Verificar estado de aprobaciones"""
        for contenedor in queryset:
            pendientes = []
            if not hasattr(contenedor, "aprobacion_aduanera"):
                pendientes.append("Aduanera")
            elif not contenedor.aprobacion_aduanera.aprobado:
                pendientes.append("Aduanera (no aprobada)")

            if not hasattr(contenedor, "aprobacion_financiera"):
                pendientes.append("Financiera")
            elif not contenedor.aprobacion_financiera.aprobado:
                pendientes.append("Financiera (no aprobada)")

            if not hasattr(contenedor, "aprobacion_pago_transitario"):
                pendientes.append("Pago Transitario")
            elif not contenedor.aprobacion_pago_transitario.pago_realizado:
                pendientes.append("Pago Transitario (no pagado)")

            if pendientes:
                messages.warning(
                    request,
                    f"{contenedor.codigo_iso}: Pendiente - {', '.join(pendientes)}",
                )
            else:
                messages.success(
                    request, f"{contenedor.codigo_iso}: Todas las aprobaciones OK"
                )

    verificar_aprobaciones.short_description = "Verificar aprobaciones de contenedores"


# ====== APROBACIÓN ADUANERA ADMIN ======
@admin.register(AprobacionAduanera)
class AprobacionAduaneraAdmin(admin.ModelAdmin):
    list_display = [
        "contenedor",
        "aprobado",
        "numero_despacho",
        "fecha_revision",
        "fecha_levante",
        "tiene_documento",
    ]
    list_filter = ["aprobado", "fecha_revision", "fecha_levante"]
    search_fields = ["contenedor__codigo_iso", "numero_despacho"]
    readonly_fields = ["created_at", "updated_at", "preview_documento"]
    date_hierarchy = "fecha_revision"
    autocomplete_fields = ["contenedor"]

    fieldsets = (
        ("Contenedor", {"fields": ("contenedor",)}),
        (
            "Documentación",
            {"fields": ("numero_despacho", "fecha_revision", "observaciones")},
        ),
        ("Resultado", {"fields": ("aprobado", "fecha_levante"), "classes": ("wide",)}),
        (
            "Documento Adjunto",
            {
                "fields": ("documento_adjunto", "preview_documento"),
                "description": "Sube el documento aduanero en formato PDF, JPG o PNG (máximo 5MB)",
            },
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def tiene_documento(self, obj):
        """Indica si tiene documento adjunto"""
        if obj.documento_adjunto:
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: gray;">✗ No</span>')

    tiene_documento.short_description = "Documento"

    def preview_documento(self, obj):
        """Muestra preview del documento adjunto"""
        if not obj.documento_adjunto:
            return format_html('<em style="color: gray;">No hay documento adjunto</em>')

        file_url = obj.documento_adjunto.url
        file_name = obj.documento_adjunto.name.split("/")[-1]
        file_extension = file_name.split(".")[-1].lower()

        # Si es imagen, mostrar preview
        if file_extension in ["jpg", "jpeg", "png"]:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />'
                "</a><br>"
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">📄 Ver documento completo</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                "</div>",
                file_url,
                file_url,
                file_url,
                file_url,
            )
        # Si es PDF, mostrar enlace
        elif file_extension == "pdf":
            return format_html(
                '<div style="margin: 10px 0;">'
                "📄 <strong>{}</strong><br>"
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">👁️ Ver PDF</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                "</div>",
                file_name,
                file_url,
                file_url,
            )

        return format_html(
            '<a href="{}" target="_blank">📎 {}</a>', file_url, file_name
        )

    preview_documento.short_description = "Vista Previa del Documento"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.aprobado:
            messages.success(
                request,
                f"Aprobación aduanera APROBADA para {obj.contenedor.codigo_iso}",
            )
        else:
            messages.warning(
                request,
                f"Aprobación aduanera PENDIENTE para {obj.contenedor.codigo_iso}",
            )


# ====== APROBACIÓN FINANCIERA ADMIN ======
@admin.register(AprobacionFinanciera)
class AprobacionFinancieraAdmin(admin.ModelAdmin):
    list_display = [
        "contenedor",
        "aprobado",
        "numero_factura",
        "monto_usd",
        "fecha_emision",
        "fecha_pago",
        "tiene_documento",
    ]
    list_filter = ["aprobado", "fecha_emision", "fecha_pago"]
    search_fields = ["contenedor__codigo_iso", "numero_factura"]
    readonly_fields = ["created_at", "updated_at", "preview_documento"]
    date_hierarchy = "fecha_pago"
    autocomplete_fields = ["contenedor"]

    fieldsets = (
        ("Contenedor", {"fields": ("contenedor",)}),
        (
            "Factura",
            {"fields": ("numero_factura", "servicios_facturados", "monto_usd")},
        ),
        ("Fechas", {"fields": ("fecha_emision", "fecha_vencimiento", "fecha_pago")}),
        ("Estado", {"fields": ("aprobado", "observaciones")}),
        (
            "Factura Adjunta",
            {
                "fields": ("documento_adjunto", "preview_documento"),
                "description": "Sube la factura en formato PDF, JPG o PNG (máximo 5MB)",
            },
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def tiene_documento(self, obj):
        """Indica si tiene documento adjunto"""
        if obj.documento_adjunto:
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: gray;">✗ No</span>')

    tiene_documento.short_description = "Factura"

    def preview_documento(self, obj):
        """Muestra preview del documento adjunto"""
        if not obj.documento_adjunto:
            return format_html('<em style="color: gray;">No hay factura adjunta</em>')

        file_url = obj.documento_adjunto.url
        file_name = obj.documento_adjunto.name.split("/")[-1]
        file_extension = file_name.split(".")[-1].lower()

        # Si es imagen, mostrar preview
        if file_extension in ["jpg", "jpeg", "png"]:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />'
                "</a><br>"
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">📄 Ver factura completa</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                "</div>",
                file_url,
                file_url,
                file_url,
                file_url,
            )
        # Si es PDF, mostrar enlace
        elif file_extension == "pdf":
            return format_html(
                '<div style="margin: 10px 0;">'
                "📄 <strong>{}</strong><br>"
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">👁️ Ver PDF</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                "</div>",
                file_name,
                file_url,
                file_url,
            )

        return format_html(
            '<a href="{}" target="_blank">📎 {}</a>', file_url, file_name
        )

    preview_documento.short_description = "Vista Previa de la Factura"


# ====== APROBACIÓN PAGO TRANSITARIO ADMIN ======
@admin.register(AprobacionPagoTransitario)
class AprobacionPagoTransitarioAdmin(admin.ModelAdmin):
    list_display = [
        "contenedor",
        "transitario",
        "pago_realizado",
        "monto_pagado",
        "fecha_pago",
        "tiene_documento",
    ]
    list_filter = ["pago_realizado", "transitario", "fecha_pago"]
    search_fields = [
        "contenedor__codigo_iso",
        "transitario__razon_social",
        "transitario__nombre_comercial",
    ]
    readonly_fields = ["created_at", "updated_at", "preview_documento"]
    date_hierarchy = "fecha_pago"
    autocomplete_fields = ["contenedor", "transitario"]

    fieldsets = (
        ("Contenedor y Transitario", {"fields": ("contenedor", "transitario")}),
        ("Pago", {"fields": ("monto_pagado", "fecha_pago", "pago_realizado")}),
        (
            "Comprobante de Pago",
            {
                "fields": ("documento_adjunto", "preview_documento"),
                "description": "Sube el comprobante de pago en formato PDF, JPG o PNG (máximo 5MB)",
            },
        ),
        ("Observaciones", {"fields": ("observaciones",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def tiene_documento(self, obj):
        """Indica si tiene documento adjunto"""
        if obj.documento_adjunto:
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: gray;">✗ No</span>')

    tiene_documento.short_description = "Comprobante"

    def preview_documento(self, obj):
        """Muestra preview del documento adjunto"""
        if not obj.documento_adjunto:
            return format_html(
                '<em style="color: gray;">No hay comprobante adjunto</em>'
            )

        file_url = obj.documento_adjunto.url
        file_name = obj.documento_adjunto.name.split("/")[-1]
        file_extension = file_name.split(".")[-1].lower()

        # Si es imagen, mostrar preview
        if file_extension in ["jpg", "jpeg", "png"]:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />'
                "</a><br>"
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">📄 Ver comprobante completo</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                "</div>",
                file_url,
                file_url,
                file_url,
                file_url,
            )
        # Si es PDF, mostrar enlace
        elif file_extension == "pdf":
            return format_html(
                '<div style="margin: 10px 0;">'
                "📄 <strong>{}</strong><br>"
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">👁️ Ver PDF</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                "</div>",
                file_name,
                file_url,
                file_url,
            )

        return format_html(
            '<a href="{}" target="_blank">📎 {}</a>', file_url, file_name
        )

    preview_documento.short_description = "Vista Previa del Comprobante"


# ====== INLINE PARA CONTENEDORES EN QUEJA ======
class QuejaContenedorInline(admin.TabularInline):
    model = QuejaContenedor
    extra = 1
    autocomplete_fields = ["contenedor"]


# ====== QUEJA ADMIN ======
@admin.register(Queja)
class QuejaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "categoria",
        "estado_coloreado",
        "nombre_cliente",
        "email_cliente",
        "tiene_imagenes",
        "fecha_creacion",
    ]
    list_filter = ["categoria", "estado", "fecha_creacion"]
    search_fields = ["nombre_cliente", "email_cliente", "descripcion"]
    readonly_fields = ["fecha_creacion", "updated_at", "preview_imagenes"]
    date_hierarchy = "fecha_creacion"
    inlines = [QuejaContenedorInline]

    fieldsets = (
        ("Información de la Queja", {"fields": ("categoria", "estado")}),
        ("Cliente", {"fields": ("nombre_cliente", "email_cliente")}),
        ("Descripción", {"fields": ("descripcion",)}),
        (
            "Imágenes Adjuntas",
            {"fields": ("imagen1", "imagen2", "imagen3", "preview_imagenes")},
        ),
        (
            "Auditoría",
            {"fields": ("fecha_creacion", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["marcar_en_proceso", "marcar_solucionada", "marcar_archivada"]

    def estado_coloreado(self, obj):
        """Muestra el estado con colores según el proceso"""
        colores = {
            "SIN_ESTADO": ("#f8fafc", "#94a3b8"),  # blanco/gris
            "EN_PROCESO": ("#0ea5e9", "#0284c7"),  # azul
            "SOLUCIONADA": ("#22c55e", "#16a34a"),  # verde
            "ARCHIVADA": ("#eab308", "#ca8a04"),  # amarillo
        }
        bg, border = colores.get(obj.estado, ("#f8fafc", "#94a3b8"))
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 10px; '
            "border-radius: 12px; border: 2px solid {}; font-size: 11px; "
            'font-weight: 600; text-shadow: 0 1px 1px rgba(0,0,0,0.3);">{}</span>',
            bg,
            "#fff" if obj.estado != "SIN_ESTADO" else "#334155",
            border,
            obj.get_estado_display(),
        )

    estado_coloreado.short_description = "Estado"
    estado_coloreado.admin_order_field = "estado"

    def tiene_imagenes(self, obj):
        """Indicador de si tiene imágenes adjuntas"""
        count = sum([1 for img in [obj.imagen1, obj.imagen2, obj.imagen3] if img])
        if count > 0:
            return format_html('<span style="color: green;">📷 {}</span>', count)
        return format_html('<span style="color: gray;">—</span>')

    tiene_imagenes.short_description = "Img"

    def preview_imagenes(self, obj):
        """Vista previa de las imágenes en el admin"""
        html = ""
        for i, img in enumerate([obj.imagen1, obj.imagen2, obj.imagen3], 1):
            if img:
                html += format_html(
                    '<a href="{}" target="_blank"><img src="{}" style="max-height: 100px; margin: 5px; border: 1px solid #ccc; border-radius: 4px;"></a>',
                    img.url,
                    img.url,
                )
        return format_html(html) if html else "Sin imágenes"

    preview_imagenes.short_description = "Vista previa"

    def marcar_en_proceso(self, request, queryset):
        """Marcar quejas como en proceso"""
        updated = queryset.filter(estado="SIN_ESTADO").update(estado="EN_PROCESO")
        messages.success(request, f"{updated} queja(s) marcada(s) como EN PROCESO.")

    marcar_en_proceso.short_description = "Marcar como EN PROCESO"

    def marcar_solucionada(self, request, queryset):
        """Marcar quejas como solucionadas"""
        updated = queryset.filter(estado__in=["SIN_ESTADO", "EN_PROCESO"]).update(
            estado="SOLUCIONADA"
        )
        messages.success(request, f"{updated} queja(s) marcada(s) como SOLUCIONADA.")

    marcar_solucionada.short_description = "Marcar como SOLUCIONADA"

    def marcar_archivada(self, request, queryset):
        """Marcar quejas como archivadas"""
        updated = queryset.update(estado="ARCHIVADA")
        messages.success(request, f"{updated} queja(s) marcada(s) como ARCHIVADA.")

    marcar_archivada.short_description = "Marcar como ARCHIVADA"


# ====== EVENTO CONTENEDOR ADMIN ======
# NOTA: No se registra en el admin principal para mantener el listado limpio.
# Los eventos se administran desde dentro de cada Contenedor (inline).
class EventoContenedorAdmin(admin.ModelAdmin):
    list_display = [
        "contenedor_codigo",
        "tipo_evento",
        "fecha_hora",
        "ubicacion_completa",
        "buque",
        "medio_transporte",
        "referencia_viaje",
    ]
    list_filter = ["tipo_evento", "medio_transporte", "ubicacion_pais", "fecha_hora"]
    search_fields = [
        "contenedor__codigo_iso",
        "ubicacion_puerto",
        "ubicacion_ciudad",
        "ubicacion_pais",
        "buque__nombre",
        "referencia_viaje",
    ]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "fecha_hora"
    autocomplete_fields = ["contenedor", "buque"]
    ordering = ["-fecha_hora"]

    fieldsets = (
        ("Contenedor", {"fields": ("contenedor",)}),
        ("Evento", {"fields": ("tipo_evento", "fecha_hora")}),
        (
            "Ubicación",
            {"fields": ("ubicacion_puerto", "ubicacion_ciudad", "ubicacion_pais")},
        ),
        ("Transporte", {"fields": ("buque", "medio_transporte", "referencia_viaje")}),
        ("Notas", {"fields": ("notas",), "classes": ("collapse",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def contenedor_codigo(self, obj):
        """Muestra el código ISO del contenedor"""
        return format_html(
            '<a href="/admin/control/contenedor/{}/change/" style="font-weight: bold;">{}</a>',
            obj.contenedor.id,
            obj.contenedor.codigo_iso,
        )

    contenedor_codigo.short_description = "Contenedor"
    contenedor_codigo.admin_order_field = "contenedor__codigo_iso"

    def ubicacion_completa(self, obj):
        """Muestra la ubicación completa"""
        parts = [obj.ubicacion_puerto]
        if obj.ubicacion_ciudad:
            parts.append(obj.ubicacion_ciudad)
        parts.append(obj.ubicacion_pais)
        return ", ".join(parts)

    ubicacion_completa.short_description = "Ubicación"

    actions = ["duplicar_evento_para_otros"]

    def duplicar_evento_para_otros(self, request, queryset):
        """Duplicar un evento para múltiples contenedores (útil para eventos masivos)"""
        if queryset.count() != 1:
            messages.error(request, "Selecciona exactamente UN evento para duplicar.")
            return

        evento_original = queryset.first()
        messages.info(
            request,
            f'Evento "{evento_original.get_tipo_evento_display()}" seleccionado. '
            f"Usa la función de importación para aplicar a múltiples contenedores.",
        )

    duplicar_evento_para_otros.short_description = (
        "Preparar para duplicar a otros contenedores"
    )


# ====== CONFIGURACIÓN DEL ADMIN SITE ======
admin.site.site_header = "SIGEP Admin - Sistema de Gestión Portuaria del Perú"
admin.site.site_title = "SIGEP Admin Perú"
admin.site.index_title = "Panel de Administración - Operaciones Portuarias"
