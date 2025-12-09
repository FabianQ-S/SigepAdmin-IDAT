from django import forms
from django.contrib import admin, messages
from django.urls import reverse
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


# ====== FORMULARIOS PERSONALIZADOS ======
class ArriboAdminForm(forms.ModelForm):
    """Formulario personalizado para Arribo que hace los campos de contenedores no obligatorios"""

    class Meta:
        model = Arribo
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer los campos de contenedores no obligatorios en el formulario
        # La validación real se hace en el modelo según tipo_operacion
        # Solo si los campos existen (no están en readonly_fields)
        if "contenedores_descarga" in self.fields:
            self.fields["contenedores_descarga"].required = False
        if "contenedores_carga" in self.fields:
            self.fields["contenedores_carga"].required = False


class AprobacionPagoTransitarioForm(forms.ModelForm):
    """Formulario para pago transitario con auto-completado de transitario desde contenedor"""

    class Meta:
        model = AprobacionPagoTransitario
        fields = "__all__"
        widgets = {
            # Transitario como campo hidden - se auto-completa desde JS
            "transitario": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar contenedores que NO tienen pago transitario registrado
        contenedores_con_pago = AprobacionPagoTransitario.objects.values_list(
            "contenedor_id", flat=True
        )
        self.fields["contenedor"].queryset = Contenedor.objects.exclude(
            id__in=contenedores_con_pago
        ).select_related("transitario")

        # Si es edición, incluir el contenedor actual
        if self.instance.pk:
            self.fields["contenedor"].queryset = Contenedor.objects.filter(
                id=self.instance.contenedor_id
            )

        # Transitario no es obligatorio en el form (se auto-asigna en save)
        if "transitario" in self.fields:
            self.fields["transitario"].required = False

    def clean(self):
        cleaned_data = super().clean()
        contenedor = cleaned_data.get("contenedor")

        # Auto-asignar transitario desde el contenedor
        if contenedor and contenedor.transitario:
            cleaned_data["transitario"] = contenedor.transitario
        elif contenedor and not contenedor.transitario:
            raise forms.ValidationError(
                "El contenedor seleccionado no tiene un transitario asignado."
            )

        return cleaned_data


class AprobacionAduaneraForm(forms.ModelForm):
    """Formulario para aprobación aduanera con validaciones y filtro de contenedores"""

    class Meta:
        model = AprobacionAduanera
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar contenedores que NO tienen aprobación aduanera registrada
        contenedores_con_aprobacion = AprobacionAduanera.objects.values_list(
            "contenedor_id", flat=True
        )
        self.fields["contenedor"].queryset = Contenedor.objects.exclude(
            id__in=contenedores_con_aprobacion
        ).select_related("arribo", "transitario")

        # Si es edición, incluir el contenedor actual
        if self.instance.pk:
            self.fields["contenedor"].queryset = Contenedor.objects.filter(
                id=self.instance.contenedor_id
            )

        # Agregar placeholder al número de despacho
        self.fields["numero_despacho"].widget.attrs.update(
            {
                "placeholder": "Ej: 118-2025-10-012345",
                "pattern": r"\d{3}-\d{4}-\d{2}-\d{6}(-\d{2})?",
            }
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
            "Identificación IMO",
            {
                "fields": ("imo_number", "nombre", "pabellon_bandera", "callsign"),
                "description": "Ingrese el número IMO y presione 'Consultar' para autocompletar los datos del buque",
            },
        ),
        (
            "Naviera",
            {"fields": ("naviera",)},
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
        ("Puerto de Registro", {"fields": ("puerto_registro",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    class Media:
        js = ("js/admin_imo_buque.js",)

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

    # Campos que se bloquean después de crear (datos de SUNAT que no deben cambiar)
    _campos_bloqueados_en_edicion = [
        "identificador_tributario",
        "razon_social",
        "nombre_comercial",
        "pais",
        "ciudad",
        "direccion",
    ]

    fieldsets = (
        (
            "Información de la Empresa",
            {
                "fields": (
                    "identificador_tributario",
                    "razon_social",
                    "nombre_comercial",
                    "codigo_scac",
                    "tipo_servicio",
                    "especialidad",
                ),
                "description": "Ingrese el RUC y presione 'Consultar' para autocompletar los datos desde SUNAT",
            },
        ),
        (
            "Ubicación (auto-completado desde SUNAT)",
            {"fields": ("pais", "ciudad", "direccion")},
        ),
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
                )
            },
        ),
        ("Observaciones", {"fields": ("observaciones",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    class Media:
        js = ("js/admin_sunat_ruc.js",)

    def get_readonly_fields(self, request, obj=None):
        """Bloquear campos de identificación y ubicación después de crear"""
        readonly = list(self.readonly_fields)
        if obj:  # Si es edición, bloquear datos de SUNAT
            readonly.extend(self._campos_bloqueados_en_edicion)
        return readonly

    def total_contenedores(self, obj):
        count = obj.contenedores.count()
        return format_html("<strong>{}</strong> contenedores", count)

    total_contenedores.short_description = "Total Contenedores"


# ====== INLINE PARA CONTENEDORES EN ARRIBO ======
class ContenedorInline(admin.TabularInline):
    """
    Inline de solo lectura para visualizar contenedores asociados a un Arribo.

    Los contenedores se agregan/editan/eliminan mediante:
    - Botón "+ Agregar Contenedor" que abre popup con formulario completo
    - Botón ✏️ en columna "Acciones" para editar/eliminar contenedores existentes
    """

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
    # Hacer todos los campos readonly - la edición se hace via botón de acciones
    readonly_fields = [
        "codigo_iso",
        "direccion",
        "tipo_tamaño",
        "transitario",
        "bl_referencia",
        "ubicacion_actual",
    ]
    # No permitir agregar desde inline - se usa el popup
    max_num = 0
    # Deshabilitar eliminación desde inline - se hace desde la vista de detalle
    can_delete = False
    # DESHABILITADO: show_change_link genera un h3 con __str__ que no se puede ocultar fácilmente
    # El botón de editar se agrega via JavaScript en la columna "Acciones"
    show_change_link = False
    verbose_name = "Contenedor registrado"
    verbose_name_plural = "Contenedores registrados"


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
    form = ArriboAdminForm  # Usar formulario personalizado
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
        "descargar_manifiesto",
    ]
    list_filter = ["estado", "tipo_operacion", "fecha_eta", "buque__naviera"]
    search_fields = ["buque__nombre", "buque__imo_number", "muelle_berth"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "fecha_eta"
    inlines = [ContenedorInline]
    # Habilitar autocomplete con búsqueda para el campo Buque
    autocomplete_fields = ["buque"]

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

    class Media:
        js = ("js/admin_contenedor_popup.js", "js/admin_arribo.js")

    def get_readonly_fields(self, request, obj=None):
        """Hacer campos de capacidad declarada de solo lectura después de crear el Arribo"""
        readonly = list(self.readonly_fields)
        if obj:  # Si es edición (obj existe), bloquear capacidad declarada
            readonly.extend(
                ["contenedores_descarga", "contenedores_carga", "tipo_operacion"]
            )
        return readonly

    def descargar_manifiesto(self, obj):
        """Botón para descargar el Manifiesto de Arribo en PDF"""
        url = reverse("control:pdf_manifiesto_arribo", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" target="_blank" '
            'style="background-color: #417690; color: white; padding: 5px 10px; '
            'border-radius: 4px; text-decoration: none; font-size: 11px;">'
            "📄 Manifiesto PDF</a>",
            url,
        )

    descargar_manifiesto.short_description = "PDF"

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
        "sello_principal_badge",
        "carrier",
        "ruta_resumen",
        "ultimo_estado_badge",
        "aprobaciones_badge",
        "estado_completo_badge",
        "acciones_pdf",
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
    readonly_fields = [
        "created_at",
        "updated_at",
        "ultimo_estado_badge",
    ]
    # Campos que serán readonly en edición (datos estructurales que no deben cambiar)
    _campos_bloqueados_en_edicion = [
        # Paso 1: Datos Fuente
        "codigo_iso",
        "arribo",
        "tipo_tamaño",
        "transitario",
        # Paso 2: Datos Auto-completados
        "bic_propietario",
        "direccion",
        "carrier",
        "consignatario",
        "tara_kg",
    ]
    date_hierarchy = "created_at"
    autocomplete_fields = ["arribo", "transitario"]
    inlines = [EventoContenedorInline]

    class Media:
        js = ("js/admin_sellos_chips.js", "js/admin_contenedor_form.js")

    def get_readonly_fields(self, request, obj=None):
        """Bloquear campos estructurales después de crear el Contenedor"""
        readonly = list(self.readonly_fields)
        if obj:  # Si es edición, bloquear datos estructurales
            readonly.extend(self._campos_bloqueados_en_edicion)
        return readonly

    fieldsets = (
        (
            "📋 Paso 1: Datos Fuente (presione ➡️ para auto-completar)",
            {
                "fields": (
                    "codigo_iso",
                    "arribo",
                    "tipo_tamaño",
                    "transitario",
                ),
                "description": "Ingrese estos datos primero. Cada campo tiene un botón ➡️ azul que auto-completa los campos relacionados.",
                "classes": ("wide",),
            },
        ),
        (
            "⚡ Paso 2: Datos Auto-completados",
            {
                "fields": (
                    "bic_propietario",
                    "direccion",
                    "carrier",
                    "consignatario",
                    "tara_kg",
                ),
                "description": "Estos campos se llenan automáticamente.",
            },
        ),
        (
            "📄 Documentación",
            {"fields": ("bl_referencia", "numero_sello")},
        ),
        (
            "🌍 Origen",
            {
                "fields": (
                    "origen_pais",
                    "origen_ciudad",
                    "origen_puerto",
                    "remitente",
                ),
                "description": "Presione ➡️ para auto-completar con datos del Puerto de Chancay.",
            },
        ),
        (
            "📍 Destino",
            {
                "fields": (
                    "destino_pais",
                    "destino_ciudad",
                    "destino_puerto",
                    "fecha_eta_destino",
                ),
                "description": "Presione ➡️ para auto-completar con datos del Puerto de Chancay.",
            },
        ),
        (
            "📦 Contenido y Pesos",
            {
                "fields": (
                    "mercancia_declarada",
                    "mercancia_peligrosa",
                    "peso_bruto_kg",
                ),
                "description": "Verá una referencia de la Tara arriba del campo Peso Bruto.",
            },
        ),
        (
            "📍 Ubicación y Fechas",
            {
                "fields": ("ubicacion_actual", "fecha_retiro_transitario"),
                "description": "Aparecerá ➡️ para sugerir ubicación según dirección.",
            },
        ),
        (
            "🕐 Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def acciones_pdf(self, obj):
        """Botones para descargar PDFs del contenedor"""
        ficha_url = reverse("control:pdf_ficha_contenedor", args=[obj.codigo_iso])

        # Verificar si está listo para Gate Pass
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
        puede_gate_pass = aduana_ok and financiera_ok and transitario_ok

        html = f'''
        <div style="display: flex; gap: 5px; flex-wrap: wrap;">
            <a href="{ficha_url}" target="_blank"
               style="background-color: #417690; color: white; padding: 4px 8px;
                      border-radius: 4px; text-decoration: none; font-size: 10px;">
               📄 Ficha
            </a>
        '''

        if puede_gate_pass:
            gate_pass_url = reverse("control:pdf_gate_pass", args=[obj.codigo_iso])
            html += f'''
            <a href="{gate_pass_url}" target="_blank"
               style="background-color: #28a745; color: white; padding: 4px 8px;
                      border-radius: 4px; text-decoration: none; font-size: 10px;">
               🚛 Gate Pass
            </a>
            '''
        else:
            html += """
            <span style="background-color: #6c757d; color: white; padding: 4px 8px;
                         border-radius: 4px; font-size: 10px; opacity: 0.6;">
               🚛 Gate Pass
            </span>
            """

        html += "</div>"
        return format_html(html)

    acciones_pdf.short_description = "PDF"

    def ruta_resumen(self, obj):
        """Muestra resumen de la ruta origen -> destino"""
        origen = obj.origen_puerto or obj.origen_ciudad or obj.origen_pais or "?"
        destino = obj.destino_puerto or obj.destino_ciudad or obj.destino_pais or "?"
        return f"{origen} → {destino}"

    ruta_resumen.short_description = "Ruta"

    def sello_principal_badge(self, obj):
        """Muestra el sello principal con badge"""
        sello = obj.get_sello_principal()
        total = len(obj.get_sellos_lista())

        if sello:
            if total > 1:
                return format_html(
                    '<span style="background-color: #1e40af; color: white; padding: 3px 8px; '
                    'border-radius: 4px; font-family: monospace; font-weight: bold;">'
                    '🔒 {}</span> <span style="color: #6b7280; font-size: 11px;">+{} más</span>',
                    sello,
                    total - 1,
                )
            return format_html(
                '<span style="background-color: #1e40af; color: white; padding: 3px 8px; '
                'border-radius: 4px; font-family: monospace; font-weight: bold;">🔒 {}</span>',
                sello,
            )
        return format_html('<span style="color: #dc2626;">⚠️ Sin sello</span>')

    sello_principal_badge.short_description = "Sello Principal"

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

    def get_changeform_initial_data(self, request):
        """Pre-llenar el campo arribo cuando viene desde el popup de Arribos"""
        initial = super().get_changeform_initial_data(request)
        arribo_id = request.GET.get("arribo")
        if arribo_id:
            initial["arribo"] = arribo_id
        return initial

    def response_add(self, request, obj, post_url_continue=None):
        """Cerrar ventana popup si viene con _popup=1"""
        from django.http import HttpResponse

        # Si es un popup (tiene _popup en GET o POST), cerrar la ventana
        is_popup = "_popup" in request.GET or "_popup" in request.POST
        if is_popup:
            return HttpResponse(
                f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Contenedor guardado</title>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 12px;
                            text-align: center;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            max-width: 400px;
                        }}
                        h2 {{ color: #27ae60; margin: 0 0 15px 0; }}
                        p {{ color: #666; margin: 0 0 20px 0; }}
                        .code {{ 
                            background: #f8f9fa; 
                            padding: 8px 16px; 
                            border-radius: 6px;
                            font-family: monospace;
                            font-size: 18px;
                            font-weight: bold;
                            color: #2c3e50;
                        }}
                        button {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            padding: 12px 30px;
                            border-radius: 6px;
                            font-size: 14px;
                            cursor: pointer;
                            margin-top: 20px;
                        }}
                        button:hover {{ opacity: 0.9; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div style="font-size: 50px; margin-bottom: 15px;">✅</div>
                        <h2>Contenedor Guardado</h2>
                        <p>Se ha registrado exitosamente:</p>
                        <div class="code">{obj.codigo_iso}</div>
                        <p style="margin-top: 15px; font-size: 13px; color: #999;">
                            La ventana se cerrará automáticamente...
                        </p>
                        <button onclick="window.close()">Cerrar ventana</button>
                    </div>
                    <script>
                        // Intentar cerrar automáticamente después de 1.5 segundos
                        setTimeout(function() {{
                            window.close();
                        }}, 1500);
                    </script>
                </body>
                </html>
                """
            )
        return super().response_add(request, obj, post_url_continue)


# ====== APROBACIÓN ADUANERA ADMIN ======
@admin.register(AprobacionAduanera)
class AprobacionAduaneraAdmin(admin.ModelAdmin):
    form = AprobacionAduaneraForm
    list_display = [
        "contenedor",
        "estado_coloreado",
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
            "Documentación DAM/DUA",
            {
                "fields": ("numero_despacho", "fecha_revision"),
                "description": "Número de despacho formato SUNAT: AAA-AAAA-RR-NNNNNN (ej: 118-2025-10-012345)",
            },
        ),
        (
            "Resultado",
            {
                "fields": ("aprobado", "fecha_levante", "observaciones"),
                "classes": ("wide",),
                "description": (
                    "⚠️ Si está APROBADO: Fecha de Levante y Documento son obligatorios. "
                    "Si NO está aprobado: Las Observaciones son obligatorias (motivo del rechazo)."
                ),
            },
        ),
        (
            "Documento Adjunto",
            {
                "fields": ("documento_adjunto", "preview_documento"),
                "description": "Documento legal de aprobación aduanera (PDF, JPG o PNG, máx. 5MB). Obligatorio si está aprobado.",
            },
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    class Media:
        js = ("js/admin_aprobacion_aduanera.js",)

    def estado_coloreado(self, obj):
        """Muestra el estado con color"""
        if obj.aprobado:
            return format_html(
                '<span style="color: white; background-color: #28a745; padding: 3px 8px; border-radius: 3px; font-weight: bold;">'
                "✓ Aprobado</span>"
            )
        return format_html(
            '<span style="color: white; background-color: #dc3545; padding: 3px 8px; border-radius: 3px; font-weight: bold;">'
            "✗ Pendiente</span>"
        )

    estado_coloreado.short_description = "Estado"

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
    form = AprobacionPagoTransitarioForm
    list_display = [
        "contenedor",
        "transitario",
        "monto_pagado",
        "fecha_pago",
        "tiene_documento",
    ]
    list_filter = ["transitario", "fecha_pago"]
    search_fields = [
        "contenedor__codigo_iso",
        "transitario__razon_social",
        "transitario__nombre_comercial",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "preview_documento",
        "transitario_display",
    ]
    date_hierarchy = "fecha_pago"
    autocomplete_fields = ["contenedor"]

    fieldsets = (
        (
            "Contenedor y Transitario",
            {
                "fields": ("contenedor", "transitario_display"),
                "description": "Seleccione el contenedor. El transitario se muestra automáticamente.",
            },
        ),
        (
            "Pago",
            {
                "fields": ("monto_pagado", "fecha_pago"),
                "description": "Ingrese los datos del pago realizado.",
            },
        ),
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

    class Media:
        js = ("js/admin_pago_transitario.js",)

    def transitario_display(self, obj):
        """Muestra el transitario del contenedor (solo lectura)"""
        if obj and obj.pk and obj.transitario:
            return format_html(
                '<span id="transitario-display" style="font-weight: bold; color: #4CAF50;">🏢 {}</span>',
                obj.transitario.razon_social,
            )
        elif obj and obj.contenedor_id:
            # Si tiene contenedor pero no se ha guardado aún
            try:
                contenedor = Contenedor.objects.select_related("transitario").get(
                    pk=obj.contenedor_id
                )
                if contenedor.transitario:
                    return format_html(
                        '<span id="transitario-display" style="font-weight: bold; color: #4CAF50;">🏢 {}</span>',
                        contenedor.transitario.razon_social,
                    )
            except Contenedor.DoesNotExist:
                pass
        return format_html(
            '<span id="transitario-display" style="color: #666; font-style: italic;">'
            "📋 Se seleccionará automáticamente el transitario del contenedor</span>"
        )

    transitario_display.short_description = "Transitario"

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

    def save_model(self, request, obj, form, change):
        """Auto-completar transitario desde el contenedor seleccionado"""
        if obj.contenedor and obj.contenedor.transitario:
            obj.transitario = obj.contenedor.transitario
        # Asegurar que pago_realizado siempre sea True
        obj.pago_realizado = True
        super().save_model(request, obj, form, change)


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
