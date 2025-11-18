from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import (
    Buque, Arribo, Contenedor, AprobacionAduanera,
    AprobacionFinanciera, AprobacionPagoTransitario,
    Transitario, Queja, QuejaContenedor
)


# ====== BUQUE ADMIN ======
@admin.register(Buque)
class BuqueAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'imo_number', 'naviera', 'pabellon_bandera', 'teu_capacidad', 'total_arribos']
    list_filter = ['naviera', 'pabellon_bandera']
    search_fields = ['nombre', 'imo_number', 'naviera', 'callsign']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'imo_number', 'pabellon_bandera', 'naviera')
        }),
        ('Especificaciones Técnicas', {
            'fields': ('eslora_metros', 'manga_metros', 'calado_metros', 'teu_capacidad')
        }),
        ('Identificación', {
            'fields': ('puerto_registro', 'callsign')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_arribos(self, obj):
        count = obj.arribos.count()
        return format_html('<strong>{}</strong> arribos', count)
    total_arribos.short_description = 'Total Arribos'

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar si tiene arribos asociados
        if obj and obj.arribos.exists():
            return False
        return super().has_delete_permission(request, obj)


# ====== TRANSITARIO ADMIN ======
@admin.register(Transitario)
class TransitarioAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'nombre_comercial', 'identificador_tributario', 'tipo_servicio',
                   'estado_operacion', 'especialidad', 'total_contenedores', 'calificacion']
    list_filter = ['estado_operacion', 'tipo_servicio', 'especialidad', 'es_activo', 'pais']
    search_fields = ['razon_social', 'nombre_comercial', 'identificador_tributario', 'contacto_principal', 'email_contacto']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Información de la Empresa', {
            'fields': ('razon_social', 'nombre_comercial', 'identificador_tributario', 'codigo_scac',
                      'tipo_servicio', 'especialidad')
        }),
        ('Ubicación', {
            'fields': ('pais', 'ciudad', 'direccion')
        }),
        ('Contacto', {
            'fields': ('contacto_principal', 'telefono_contacto', 'telefono_emergencia',
                      'email_contacto', 'email_facturacion', 'sitio_web')
        }),
        ('Operación', {
            'fields': ('estado_operacion', 'licencia_operador', 'fecha_vencimiento_licencia',
                      'zona_cobertura', 'limite_credito', 'calificacion', 'es_activo')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_contenedores(self, obj):
        count = obj.contenedores.count()
        return format_html('<strong>{}</strong> contenedores', count)
    total_contenedores.short_description = 'Total Contenedores'


# ====== INLINE PARA CONTENEDORES EN ARRIBO ======
class ContenedorInline(admin.TabularInline):
    model = Contenedor
    extra = 0
    fields = ['codigo_iso', 'direccion', 'tipo_tamaño', 'transitario', 'bl_referencia', 'ubicacion_actual']
    readonly_fields = []
    can_delete = True
    show_change_link = True


# ====== ARRIBO ADMIN ======
@admin.register(Arribo)
class ArriboAdmin(admin.ModelAdmin):
    list_display = ['id', 'buque', 'fecha_eta', 'fecha_etd', 'tipo_operacion', 'estado',
                   'contenedores_descarga', 'contenedores_carga', 'total_contenedores_badge']
    list_filter = ['estado', 'tipo_operacion', 'fecha_eta', 'buque__naviera']
    search_fields = ['buque__nombre', 'buque__imo_number', 'muelle_berth']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'fecha_eta'
    inlines = [ContenedorInline]

    fieldsets = (
        ('Información del Arribo', {
            'fields': ('buque', 'estado', 'tipo_operacion', 'muelle_berth')
        }),
        ('Fechas', {
            'fields': ('fecha_eta', 'fecha_etd', 'fecha_arribo_real')
        }),
        ('Capacidad Declarada', {
            'fields': ('contenedores_descarga', 'contenedores_carga', 'servicios_contratados'),
            'description': 'Cantidad de contenedores declarados para descarga (import) y carga (export)'
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_contenedores(self, obj):
        """Total de contenedores registrados en el sistema"""
        return obj.contenedores.count()
    total_contenedores.short_description = 'Contenedores Registrados'

    def total_contenedores_badge(self, obj):
        """Badge visual para contenedores"""
        total = obj.contenedores.count()
        declarado = obj.contenedores_descarga + obj.contenedores_carga
        color = 'green' if total == declarado else 'orange' if total < declarado else 'red'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}/{}</span>',
            color, total, declarado
        )
    total_contenedores_badge.short_description = 'Contenedores (Real/Declarado)'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Mensaje informativo sobre contenedores
        total = obj.contenedores.count()
        declarado = obj.contenedores_descarga + obj.contenedores_carga
        if total < declarado:
            messages.warning(request, f'Faltan {declarado - total} contenedores por registrar.')
        elif total > declarado:
            messages.error(request, f'Hay {total - declarado} contenedores de más registrados.')


# ====== CONTENEDOR ADMIN ======
@admin.register(Contenedor)
class ContenedorAdmin(admin.ModelAdmin):
    list_display = ['codigo_iso', 'arribo', 'direccion', 'tipo_tamaño', 'transitario', 'ubicacion_actual',
                   'aprobaciones_badge', 'estado_completo_badge']
    list_filter = ['direccion', 'tipo_tamaño', 'mercancia_peligrosa', 'transitario', 'arribo__buque']
    search_fields = ['codigo_iso', 'bl_referencia', 'transitario__razon_social', 'transitario__nombre_comercial']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['arribo', 'transitario']

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_iso', 'bic_propietario', 'arribo', 'direccion', 'tipo_tamaño', 'transitario')
        }),
        ('Documentación', {
            'fields': ('bl_referencia', 'numero_sello')
        }),
        ('Información de Origen/Destino', {
            'fields': ('origen_pais', 'origen_puerto', 'origen_remitente'),
            'description': 'Para IMPORT: origen real. Para EXPORT: destino.'
        }),
        ('Contenido y Pesos', {
            'fields': ('mercancia_declarada', 'mercancia_peligrosa', 'peso_bruto_kg', 'tara_kg')
        }),
        ('Ubicación y Fechas', {
            'fields': ('ubicacion_actual', 'fecha_retiro_transitario')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def aprobaciones_badge(self, obj):
        """Muestra el estado de aprobaciones"""
        aprobaciones = []

        # Aprobación Aduanera
        if hasattr(obj, 'aprobacion_aduanera'):
            estado = 'APROBADO' if obj.aprobacion_aduanera.aprobado else 'PENDIENTE'
            aprobaciones.append(('🛃 Aduana', estado))
        else:
            aprobaciones.append(('🛃 Aduana', 'PENDIENTE'))

        # Aprobación Financiera
        if hasattr(obj, 'aprobacion_financiera'):
            estado = 'APROBADO' if obj.aprobacion_financiera.aprobado else 'PENDIENTE'
            aprobaciones.append(('💰 Financiera', estado))
        else:
            aprobaciones.append(('💰 Financiera', 'PENDIENTE'))

        # Aprobación Pago Transitario
        if hasattr(obj, 'aprobacion_pago_transitario'):
            estado = 'PAGADO' if obj.aprobacion_pago_transitario.pago_realizado else 'PENDIENTE'
            aprobaciones.append(('🚚 Transitario', estado))
        else:
            aprobaciones.append(('🚚 Transitario', 'PENDIENTE'))

        html = '<div>'
        for nombre, estado in aprobaciones:
            color = {
                'APROBADO': 'green',
                'RECHAZADO': 'red',
                'PENDIENTE': 'orange',
                'PAGADO': 'green',
            }.get(estado, 'gray')
            html += f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 3px; margin: 2px; display: inline-block; font-size: 11px;">{nombre}: {estado}</span><br>'
        html += '</div>'
        return format_html(html)
    aprobaciones_badge.short_description = 'Aprobaciones'

    def estado_completo_badge(self, obj):
        """Badge del estado completo del contenedor"""
        # Verificar si todas las aprobaciones están OK
        aduana_ok = hasattr(obj, 'aprobacion_aduanera') and obj.aprobacion_aduanera.aprobado
        financiera_ok = hasattr(obj, 'aprobacion_financiera') and obj.aprobacion_financiera.aprobado
        transitario_ok = hasattr(obj, 'aprobacion_pago_transitario') and obj.aprobacion_pago_transitario.pago_realizado

        if aduana_ok and financiera_ok and transitario_ok:
            return format_html(
                '<span style="background-color: green; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">✓ LISTO PARA RETIRO</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 5px 10px; border-radius: 3px;">⏳ EN PROCESO</span>'
            )
    estado_completo_badge.short_description = 'Estado General'

    actions = ['marcar_listo_retiro', 'verificar_aprobaciones']

    def marcar_listo_retiro(self, request, queryset):
        """Acción para verificar y marcar contenedores listos para retiro"""
        count = 0
        for contenedor in queryset:
            aduana_ok = hasattr(contenedor, 'aprobacion_aduanera') and contenedor.aprobacion_aduanera.aprobado
            financiera_ok = hasattr(contenedor, 'aprobacion_financiera') and contenedor.aprobacion_financiera.aprobado
            transitario_ok = hasattr(contenedor, 'aprobacion_pago_transitario') and contenedor.aprobacion_pago_transitario.pago_realizado

            if aduana_ok and financiera_ok and transitario_ok:
                count += 1

        if count > 0:
            messages.success(request, f'{count} contenedor(es) están listos para retiro.')
        else:
            messages.warning(request, 'Ningún contenedor seleccionado está listo para retiro.')
    marcar_listo_retiro.short_description = 'Verificar contenedores listos para retiro'

    def verificar_aprobaciones(self, request, queryset):
        """Verificar estado de aprobaciones"""
        for contenedor in queryset:
            pendientes = []
            if not hasattr(contenedor, 'aprobacion_aduanera'):
                pendientes.append('Aduanera')
            elif not contenedor.aprobacion_aduanera.aprobado:
                pendientes.append('Aduanera (no aprobada)')

            if not hasattr(contenedor, 'aprobacion_financiera'):
                pendientes.append('Financiera')
            elif not contenedor.aprobacion_financiera.aprobado:
                pendientes.append('Financiera (no aprobada)')

            if not hasattr(contenedor, 'aprobacion_pago_transitario'):
                pendientes.append('Pago Transitario')
            elif not contenedor.aprobacion_pago_transitario.pago_realizado:
                pendientes.append('Pago Transitario (no pagado)')

            if pendientes:
                messages.warning(request, f'{contenedor.codigo_iso}: Pendiente - {", ".join(pendientes)}')
            else:
                messages.success(request, f'{contenedor.codigo_iso}: Todas las aprobaciones OK')
    verificar_aprobaciones.short_description = 'Verificar aprobaciones de contenedores'


# ====== APROBACIÓN ADUANERA ADMIN ======
@admin.register(AprobacionAduanera)
class AprobacionAduaneraAdmin(admin.ModelAdmin):
    list_display = ['contenedor', 'aprobado', 'numero_despacho', 'fecha_revision', 'fecha_levante', 'tiene_documento']
    list_filter = ['aprobado', 'fecha_revision', 'fecha_levante']
    search_fields = ['contenedor__codigo_iso', 'numero_despacho']
    readonly_fields = ['created_at', 'updated_at', 'preview_documento']
    date_hierarchy = 'fecha_revision'
    autocomplete_fields = ['contenedor']

    fieldsets = (
        ('Contenedor', {
            'fields': ('contenedor',)
        }),
        ('Documentación', {
            'fields': ('numero_despacho', 'fecha_revision', 'observaciones')
        }),
        ('Resultado', {
            'fields': ('aprobado', 'fecha_levante'),
            'classes': ('wide',)
        }),
        ('Documento Adjunto', {
            'fields': ('documento_adjunto', 'preview_documento'),
            'description': 'Sube el documento aduanero en formato PDF, JPG o PNG (máximo 5MB)'
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tiene_documento(self, obj):
        """Indica si tiene documento adjunto"""
        if obj.documento_adjunto:
            return format_html(
                '<span style="color: green;">✓ Sí</span>'
            )
        return format_html('<span style="color: gray;">✗ No</span>')
    tiene_documento.short_description = 'Documento'

    def preview_documento(self, obj):
        """Muestra preview del documento adjunto"""
        if not obj.documento_adjunto:
            return format_html('<em style="color: gray;">No hay documento adjunto</em>')

        file_url = obj.documento_adjunto.url
        file_name = obj.documento_adjunto.name.split('/')[-1]
        file_extension = file_name.split('.')[-1].lower()

        # Si es imagen, mostrar preview
        if file_extension in ['jpg', 'jpeg', 'png']:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />'
                '</a><br>'
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">📄 Ver documento completo</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                '</div>',
                file_url, file_url, file_url, file_url
            )
        # Si es PDF, mostrar enlace
        elif file_extension == 'pdf':
            return format_html(
                '<div style="margin: 10px 0;">'
                '📄 <strong>{}</strong><br>'
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">👁️ Ver PDF</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                '</div>',
                file_name, file_url, file_url
            )

        return format_html(
            '<a href="{}" target="_blank">📎 {}</a>',
            file_url, file_name
        )
    preview_documento.short_description = 'Vista Previa del Documento'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.aprobado:
            messages.success(request, f'Aprobación aduanera APROBADA para {obj.contenedor.codigo_iso}')
        else:
            messages.warning(request, f'Aprobación aduanera PENDIENTE para {obj.contenedor.codigo_iso}')


# ====== APROBACIÓN FINANCIERA ADMIN ======
@admin.register(AprobacionFinanciera)
class AprobacionFinancieraAdmin(admin.ModelAdmin):
    list_display = ['contenedor', 'aprobado', 'numero_factura', 'monto_usd', 'fecha_emision', 'fecha_pago', 'tiene_documento']
    list_filter = ['aprobado', 'fecha_emision', 'fecha_pago']
    search_fields = ['contenedor__codigo_iso', 'numero_factura']
    readonly_fields = ['created_at', 'updated_at', 'preview_documento']
    date_hierarchy = 'fecha_pago'
    autocomplete_fields = ['contenedor']

    fieldsets = (
        ('Contenedor', {
            'fields': ('contenedor',)
        }),
        ('Factura', {
            'fields': ('numero_factura', 'servicios_facturados', 'monto_usd')
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_vencimiento', 'fecha_pago')
        }),
        ('Estado', {
            'fields': ('aprobado', 'observaciones')
        }),
        ('Factura Adjunta', {
            'fields': ('documento_adjunto', 'preview_documento'),
            'description': 'Sube la factura en formato PDF, JPG o PNG (máximo 5MB)'
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tiene_documento(self, obj):
        """Indica si tiene documento adjunto"""
        if obj.documento_adjunto:
            return format_html(
                '<span style="color: green;">✓ Sí</span>'
            )
        return format_html('<span style="color: gray;">✗ No</span>')
    tiene_documento.short_description = 'Factura'

    def preview_documento(self, obj):
        """Muestra preview del documento adjunto"""
        if not obj.documento_adjunto:
            return format_html('<em style="color: gray;">No hay factura adjunta</em>')

        file_url = obj.documento_adjunto.url
        file_name = obj.documento_adjunto.name.split('/')[-1]
        file_extension = file_name.split('.')[-1].lower()

        # Si es imagen, mostrar preview
        if file_extension in ['jpg', 'jpeg', 'png']:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />'
                '</a><br>'
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">📄 Ver factura completa</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                '</div>',
                file_url, file_url, file_url, file_url
            )
        # Si es PDF, mostrar enlace
        elif file_extension == 'pdf':
            return format_html(
                '<div style="margin: 10px 0;">'
                '📄 <strong>{}</strong><br>'
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">👁️ Ver PDF</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                '</div>',
                file_name, file_url, file_url
            )

        return format_html(
            '<a href="{}" target="_blank">📎 {}</a>',
            file_url, file_name
        )
    preview_documento.short_description = 'Vista Previa de la Factura'


# ====== APROBACIÓN PAGO TRANSITARIO ADMIN ======
@admin.register(AprobacionPagoTransitario)
class AprobacionPagoTransitarioAdmin(admin.ModelAdmin):
    list_display = ['contenedor', 'transitario', 'pago_realizado', 'monto_pagado', 'fecha_pago', 'tiene_documento']
    list_filter = ['pago_realizado', 'transitario', 'fecha_pago']
    search_fields = ['contenedor__codigo_iso', 'transitario__razon_social', 'transitario__nombre_comercial']
    readonly_fields = ['created_at', 'updated_at', 'preview_documento']
    date_hierarchy = 'fecha_pago'
    autocomplete_fields = ['contenedor', 'transitario']

    fieldsets = (
        ('Contenedor y Transitario', {
            'fields': ('contenedor', 'transitario')
        }),
        ('Pago', {
            'fields': ('monto_pagado', 'fecha_pago', 'pago_realizado')
        }),
        ('Comprobante de Pago', {
            'fields': ('documento_adjunto', 'preview_documento'),
            'description': 'Sube el comprobante de pago en formato PDF, JPG o PNG (máximo 5MB)'
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tiene_documento(self, obj):
        """Indica si tiene documento adjunto"""
        if obj.documento_adjunto:
            return format_html(
                '<span style="color: green;">✓ Sí</span>'
            )
        return format_html('<span style="color: gray;">✗ No</span>')
    tiene_documento.short_description = 'Comprobante'

    def preview_documento(self, obj):
        """Muestra preview del documento adjunto"""
        if not obj.documento_adjunto:
            return format_html('<em style="color: gray;">No hay comprobante adjunto</em>')

        file_url = obj.documento_adjunto.url
        file_name = obj.documento_adjunto.name.split('/')[-1]
        file_extension = file_name.split('.')[-1].lower()

        # Si es imagen, mostrar preview
        if file_extension in ['jpg', 'jpeg', 'png']:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />'
                '</a><br>'
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">📄 Ver comprobante completo</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                '</div>',
                file_url, file_url, file_url, file_url
            )
        # Si es PDF, mostrar enlace
        elif file_extension == 'pdf':
            return format_html(
                '<div style="margin: 10px 0;">'
                '📄 <strong>{}</strong><br>'
                '<a href="{}" target="_blank" style="margin-top: 5px; display: inline-block;">👁️ Ver PDF</a> | '
                '<a href="{}" download style="margin-top: 5px; display: inline-block;">⬇️ Descargar</a>'
                '</div>',
                file_name, file_url, file_url
            )

        return format_html(
            '<a href="{}" target="_blank">📎 {}</a>',
            file_url, file_name
        )
    preview_documento.short_description = 'Vista Previa del Comprobante'


# ====== INLINE PARA CONTENEDORES EN QUEJA ======
class QuejaContenedorInline(admin.TabularInline):
    model = QuejaContenedor
    extra = 1
    autocomplete_fields = ['contenedor']


# ====== QUEJA ADMIN ======
@admin.register(Queja)
class QuejaAdmin(admin.ModelAdmin):
    list_display = ['id', 'categoria', 'estado', 'nombre_cliente', 'email_cliente', 'fecha_creacion']
    list_filter = ['categoria', 'estado', 'fecha_creacion']
    search_fields = ['nombre_cliente', 'email_cliente', 'descripcion']
    readonly_fields = ['fecha_creacion', 'updated_at']
    date_hierarchy = 'fecha_creacion'
    inlines = [QuejaContenedorInline]

    fieldsets = (
        ('Información de la Queja', {
            'fields': ('categoria', 'estado')
        }),
        ('Cliente', {
            'fields': ('nombre_cliente', 'email_cliente')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['marcar_como_resuelta', 'marcar_como_en_revision']

    def marcar_como_resuelta(self, request, queryset):
        """Marcar quejas como resueltas"""
        updated = queryset.filter(estado__in=['PENDIENTE', 'EN_REVISION']).update(estado='RESUELTO')
        messages.success(request, f'{updated} queja(s) marcada(s) como RESUELTO.')
    marcar_como_resuelta.short_description = 'Marcar como RESUELTO'

    def marcar_como_en_revision(self, request, queryset):
        """Marcar quejas como en revisión"""
        updated = queryset.filter(estado='PENDIENTE').update(estado='EN_REVISION')
        messages.success(request, f'{updated} queja(s) marcada(s) como EN_REVISION.')
    marcar_como_en_revision.short_description = 'Marcar como EN REVISIÓN'


# ====== CONFIGURACIÓN DEL ADMIN SITE ======
admin.site.site_header = "SIGEP Admin - Sistema de Gestión Portuaria del Perú"
admin.site.site_title = "SIGEP Admin Perú"
admin.site.index_title = "Panel de Administración - Operaciones Portuarias"

