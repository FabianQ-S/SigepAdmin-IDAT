import re

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

# from django.utils.translation import gettext_lazy as _


# ====== VALIDADORES PERSONALIZADOS ======
def validate_document_size(value):
    """Valida que el archivo no supere los 5MB"""
    filesize = value.size
    max_size_mb = 5
    max_size_bytes = max_size_mb * 1024 * 1024  # 5MB en bytes

    if filesize > max_size_bytes:
        raise ValidationError(
            f"El tamaño máximo del archivo es {max_size_mb}MB. "
            f"Tu archivo tiene {filesize / (1024 * 1024):.2f}MB"
        )


def validate_iso_6346(value):
    """
    Valida el código de contenedor según la norma ISO 6346.

    Formato: AAAA NNNNNN C
    - 4 letras: Código del propietario (3 letras) + categoría (U, J, Z)
    - 6 números: Número de serie
    - 1 número: Dígito verificador (check digit)

    El dígito verificador se calcula usando el algoritmo ISO 6346:
    1. Cada carácter tiene un valor equivalente
    2. Se multiplica por 2^posición
    3. Se suma todo, se divide entre 11, y el residuo es el check digit
    4. Si el residuo es 10, el check digit es 0

    Ejemplos válidos: MSKU9070323, HLXU8142385, CSQU3054383
    """
    value = value.upper().strip()

    # Validar formato básico: 4 letras + 7 números (incluyendo check digit)
    pattern = r"^[A-Z]{4}\d{7}$"
    if not re.match(pattern, value):
        raise ValidationError(
            f"El código '{value}' no tiene el formato ISO 6346 válido. "
            "Debe ser 4 letras seguidas de 7 números (ej: MSKU9070323)"
        )

    # Validar que la 4ta letra sea U, J o Z (categoría de equipo)
    categoria = value[3]
    if categoria not in ["U", "J", "Z"]:
        raise ValidationError(
            f"La 4ta letra debe ser U (contenedor de carga), J (equipo auxiliar) "
            f"o Z (trailer/chasis). Recibido: '{categoria}'"
        )

    # Tabla de equivalencias ISO 6346 para letras
    # Las letras tienen valores específicos (saltando múltiplos de 11)
    letter_values = {
        "A": 10,
        "B": 12,
        "C": 13,
        "D": 14,
        "E": 15,
        "F": 16,
        "G": 17,
        "H": 18,
        "I": 19,
        "J": 20,
        "K": 21,
        "L": 23,
        "M": 24,
        "N": 25,
        "O": 26,
        "P": 27,
        "Q": 28,
        "R": 29,
        "S": 30,
        "T": 31,
        "U": 32,
        "V": 34,
        "W": 35,
        "X": 36,
        "Y": 37,
        "Z": 38,
    }

    # Calcular el check digit
    total = 0
    for i, char in enumerate(value[:10]):  # Solo los primeros 10 caracteres
        if char.isalpha():
            char_value = letter_values[char]
        else:
            char_value = int(char)

        # Multiplicar por 2^posición
        total += char_value * (2**i)

    # Calcular el dígito verificador
    remainder = total % 11
    check_digit = 0 if remainder == 10 else remainder

    # Validar contra el dígito proporcionado
    provided_check_digit = int(value[10])

    if check_digit != provided_check_digit:
        raise ValidationError(
            f"El código '{value}' tiene un dígito verificador inválido. "
            f"Esperado: {check_digit}, Proporcionado: {provided_check_digit}. "
            "Este código no cumple con la norma ISO 6346."
        )

    return value


def calculate_iso_6346_check_digit(owner_code, serial_number):
    """
    Calcula el dígito verificador ISO 6346 dado el código de propietario y número de serie.

    Args:
        owner_code: 4 letras (ej: 'MSKU')
        serial_number: 6 dígitos (ej: '907032')

    Returns:
        El dígito verificador (0-9)
    """
    letter_values = {
        "A": 10,
        "B": 12,
        "C": 13,
        "D": 14,
        "E": 15,
        "F": 16,
        "G": 17,
        "H": 18,
        "I": 19,
        "J": 20,
        "K": 21,
        "L": 23,
        "M": 24,
        "N": 25,
        "O": 26,
        "P": 27,
        "Q": 28,
        "R": 29,
        "S": 30,
        "T": 31,
        "U": 32,
        "V": 34,
        "W": 35,
        "X": 36,
        "Y": 37,
        "Z": 38,
    }

    code = (owner_code + serial_number).upper()
    total = 0

    for i, char in enumerate(code):
        if char.isalpha():
            char_value = letter_values[char]
        else:
            char_value = int(char)
        total += char_value * (2**i)

    remainder = total % 11
    return 0 if remainder == 10 else remainder


# ====== CUN02: BUQUES (Catálogo) ======
class Buque(models.Model):
    """Catálogo de buques que arriban al puerto"""

    nombre = models.CharField(max_length=200, verbose_name="Nombre del Buque")
    imo_number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="IMO Number",
        help_text="Número IMO único internacional",
    )
    pabellon_bandera = models.CharField(max_length=80, verbose_name="Pabellón/Bandera")
    naviera = models.CharField(max_length=120, verbose_name="Naviera")
    puerto_registro = models.CharField(
        max_length=120, verbose_name="Puerto de Registro"
    )
    callsign = models.CharField(max_length=20, verbose_name="Call Sign")
    eslora_metros = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Eslora (metros)"
    )
    manga_metros = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Manga (metros)"
    )
    teu_capacidad = models.PositiveIntegerField(verbose_name="Capacidad TEU")
    calado_metros = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Calado (metros)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buque"
        verbose_name_plural = "Buques"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["imo_number"]),
            models.Index(fields=["nombre"]),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.imo_number})"


# ====== CUN06: TRANSITARIOS (Catálogo empresas logísticas) ======
class Transitario(models.Model):
    """Empresas de logística y transporte que gestionan contenedores"""

    TIPO_SERVICIO_CHOICES = [
        ("NVOCC", "NVOCC"),
        ("FFWD", "Freight Forwarder"),
        ("TRUCKING", "Trucking"),
        ("INTEGRAL", "Servicio Integral"),
    ]

    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("SUSPENDIDO", "Suspendido"),
        ("BLOQUEADO", "Bloqueado"),
    ]

    ESPECIALIDAD_CHOICES = [
        ("IMPORT", "Importación"),
        ("EXPORT", "Exportación"),
        ("AMBOS", "Ambos"),
    ]

    razon_social = models.CharField(max_length=200, verbose_name="Razón Social")
    nombre_comercial = models.CharField(
        max_length=200, blank=True, verbose_name="Nombre Comercial"
    )
    identificador_tributario = models.CharField(
        max_length=20, unique=True, verbose_name="RUC/VAT/Tax ID"
    )
    codigo_scac = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="Código SCAC",
        help_text="Standard Carrier Alpha Code",
    )
    tipo_servicio = models.CharField(
        max_length=20,
        choices=TIPO_SERVICIO_CHOICES,
        verbose_name="Tipo de Servicio",
        help_text="NVOCC: Operador sin buque | FFWD: Agente de carga | TRUCKING: Transporte terrestre | INTEGRAL: Ofrece todos los servicios anteriores",
    )
    pais = models.CharField(max_length=60, verbose_name="País")
    ciudad = models.CharField(max_length=80, verbose_name="Ciudad")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    contacto_principal = models.CharField(
        max_length=120, verbose_name="Contacto Principal"
    )
    telefono_contacto = models.CharField(
        max_length=30, verbose_name="Teléfono de Contacto"
    )
    telefono_emergencia = models.CharField(
        max_length=30, blank=True, verbose_name="Teléfono de Emergencia"
    )
    email_contacto = models.EmailField(verbose_name="Email de Contacto")
    email_facturacion = models.EmailField(
        blank=True, verbose_name="Email de Facturación"
    )
    sitio_web = models.URLField(blank=True, verbose_name="Sitio Web")
    estado_operacion = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="ACTIVO",
        verbose_name="Estado de Operación",
    )
    especialidad = models.CharField(
        max_length=20, choices=ESPECIALIDAD_CHOICES, verbose_name="Especialidad"
    )
    licencia_operador = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Licencia de Operador",
        help_text="Ej: MTC-2024-00123",
    )
    fecha_vencimiento_licencia = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Vencimiento de Licencia"
    )
    zona_cobertura = models.TextField(blank=True, verbose_name="Zona de Cobertura")
    limite_credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Límite de Crédito ($)",
        help_text="Monto máximo de crédito en dólares americanos",
    )
    calificacion = models.IntegerField(
        default=5, verbose_name="Calificación", help_text="Calificación de 1 a 5"
    )
    es_activo = models.BooleanField(default=True, verbose_name="Activo")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transitario"
        verbose_name_plural = "Transitarios"
        ordering = ["razon_social"]
        indexes = [
            models.Index(fields=["identificador_tributario"]),
            models.Index(fields=["estado_operacion", "es_activo"]),
        ]

    def clean(self):
        if self.calificacion and (self.calificacion < 1 or self.calificacion > 5):
            raise ValidationError(
                {"calificacion": "La calificación debe estar entre 1 y 5"}
            )

    def __str__(self):
        return self.nombre_comercial or self.razon_social


# ====== CUN01: ARRIBO (Vessel Call) ======
class Arribo(models.Model):
    """Registro de arribo de buques al puerto - maneja DESCARGA (import) y CARGA (export)"""

    TIPO_OPERACION_CHOICES = [
        ("DESCARGA", "Descarga (Importación)"),
        ("CARGA", "Carga (Exportación)"),
        ("AMBOS", "Carga y Descarga"),
    ]

    ESTADO_CHOICES = [
        ("PROGRAMADO", "Programado"),
        ("EN_RUTA", "En Ruta"),
        ("ATRACADO", "Atracado"),
        ("OPERANDO", "Operando"),
        ("COMPLETADO", "Completado"),
        ("CANCELADO", "Cancelado"),
    ]

    buque = models.ForeignKey(
        Buque, on_delete=models.PROTECT, related_name="arribos", verbose_name="Buque"
    )
    fecha_eta = models.DateTimeField(verbose_name="ETA (Estimated Time of Arrival)")
    fecha_etd = models.DateTimeField(
        null=True, blank=True, verbose_name="ETD (Estimated Time of Departure)"
    )
    fecha_arribo_real = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de Arribo Real"
    )
    muelle_berth = models.CharField(max_length=50, verbose_name="Muelle/Berth")
    tipo_operacion = models.CharField(
        max_length=10, choices=TIPO_OPERACION_CHOICES, verbose_name="Tipo de Operación"
    )
    contenedores_descarga = models.PositiveIntegerField(
        verbose_name="Contenedores Descarga (Import)",
        help_text="Cantidad esperada de contenedores a descargar del buque (importación)",
        default=0,
    )
    contenedores_carga = models.PositiveIntegerField(
        verbose_name="Contenedores Carga (Export)",
        help_text="Cantidad esperada de contenedores a cargar al buque (exportación)",
        default=0,
    )
    servicios_contratados = models.CharField(
        max_length=120, verbose_name="Servicios Contratados"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="PROGRAMADO",
        verbose_name="Estado",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Arribo"
        verbose_name_plural = "Arribos"
        ordering = ["-fecha_eta"]
        indexes = [
            models.Index(fields=["estado", "fecha_eta"]),
            models.Index(fields=["buque", "fecha_eta"]),
        ]

    def clean(self):
        if self.fecha_etd and self.fecha_eta:
            if self.fecha_etd < self.fecha_eta:
                raise ValidationError(
                    {"fecha_etd": "La fecha ETD no puede ser anterior a la fecha ETA"}
                )

        # Validar que al menos un tipo de operación tenga contenedores
        if self.tipo_operacion == "DESCARGA" and self.contenedores_descarga == 0:
            raise ValidationError(
                {"contenedores_descarga": "Debe especificar contenedores para descarga"}
            )

        if self.tipo_operacion == "CARGA" and self.contenedores_carga == 0:
            raise ValidationError(
                {"contenedores_carga": "Debe especificar contenedores para carga"}
            )

        if self.tipo_operacion == "AMBOS":
            if self.contenedores_descarga == 0 and self.contenedores_carga == 0:
                raise ValidationError(
                    "Debe especificar contenedores para descarga y/o carga"
                )

    def __str__(self):
        return f"{self.buque.nombre} - {self.fecha_eta.strftime('%Y-%m-%d %H:%M')}"


# ====== CUN03: CONTENEDOR ======
class Contenedor(models.Model):
    """Contenedores individuales manejados en el puerto (import y export)"""

    DIRECCION_CHOICES = [
        ("IMPORT", "Importación (Descarga)"),
        ("EXPORT", "Exportación (Carga)"),
    ]

    arribo = models.ForeignKey(
        Arribo,
        on_delete=models.CASCADE,
        related_name="contenedores",
        verbose_name="Arribo",
    )
    transitario = models.ForeignKey(
        Transitario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contenedores",
        verbose_name="Transitario",
        help_text="Transitario encargado de gestionar este contenedor",
    )
    direccion = models.CharField(
        max_length=10,
        choices=DIRECCION_CHOICES,
        verbose_name="Dirección del Contenedor",
        help_text="Import: descarga del buque | Export: carga al buque",
    )
    codigo_iso = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="Código ISO 6346",
        help_text="Código único del contenedor según norma ISO 6346 (ej: MSKU9070323)",
        validators=[validate_iso_6346],
    )
    bic_propietario = models.CharField(
        max_length=4,
        verbose_name="BIC Propietario",
        help_text="Bureau International des Containers - Código del propietario",
    )
    tipo_tamaño = models.CharField(
        max_length=10, verbose_name="Tipo/Tamaño", help_text="Ej: 20GP, 40HC, 40RF"
    )
    peso_bruto_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Peso Bruto (kg)",
        help_text="VGM - Verified Gross Mass",
    )
    tara_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Tara (kg)",
        help_text="Peso del contenedor vacío",
    )
    numero_sello = models.CharField(max_length=30, verbose_name="Número de Sello")
    mercancia_declarada = models.CharField(
        max_length=255, verbose_name="Mercancía Declarada"
    )
    mercancia_peligrosa = models.BooleanField(
        default=False, verbose_name="Mercancía Peligrosa"
    )
    ubicacion_actual = models.CharField(
        max_length=50,
        verbose_name="Ubicación Actual",
        help_text="Ubicación física en el puerto",
    )
    bl_referencia = models.CharField(
        max_length=50, verbose_name="BL de Referencia", help_text="Bill of Lading"
    )
    fecha_retiro_transitario = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Retiro/Entrega (Cita)",
        help_text="Import: cita de retiro | Export: cita de entrega al puerto",
    )
    # === Información de Origen ===
    origen_pais = models.CharField(
        max_length=60, null=True, blank=True, verbose_name="País de Origen"
    )
    origen_puerto = models.CharField(
        max_length=120, null=True, blank=True, verbose_name="Puerto de Origen"
    )
    origen_ciudad = models.CharField(
        max_length=120, null=True, blank=True, verbose_name="Ciudad de Origen"
    )
    remitente = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Remitente/Shipper",
        help_text="Empresa o persona que envía la mercancía",
    )
    # === Información de Destino ===
    destino_pais = models.CharField(
        max_length=60, null=True, blank=True, verbose_name="País de Destino"
    )
    destino_puerto = models.CharField(
        max_length=120, null=True, blank=True, verbose_name="Puerto de Destino"
    )
    destino_ciudad = models.CharField(
        max_length=120, null=True, blank=True, verbose_name="Ciudad de Destino"
    )
    consignatario = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Consignatario/Receiver",
        help_text="Empresa o persona que recibe la mercancía",
    )
    # === Tracking ===
    carrier = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Carrier/Naviera",
        help_text="Naviera principal que transporta el contenedor",
    )
    fecha_eta_destino = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="ETA Destino Final",
        help_text="Fecha estimada de llegada al destino final",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contenedor"
        verbose_name_plural = "Contenedores"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["codigo_iso"]),
            models.Index(fields=["arribo", "transitario"]),
            models.Index(fields=["bl_referencia"]),
            models.Index(fields=["direccion", "arribo"]),
        ]

    def clean(self):
        if self.peso_bruto_kg and self.tara_kg:
            if self.peso_bruto_kg < self.tara_kg:
                raise ValidationError(
                    {"peso_bruto_kg": "El peso bruto no puede ser menor que la tara"}
                )

    @property
    def esta_liberado_aduana(self):
        """Verifica si el contenedor está liberado por aduana (calculado)"""
        return (
            hasattr(self, "aprobacion_aduanera")
            and self.aprobacion_aduanera.aprobado
            and self.aprobacion_aduanera.fecha_levante is not None
        )

    @property
    def esta_pagado(self):
        """Verifica si el cliente ha pagado por este contenedor (calculado)"""
        return (
            hasattr(self, "aprobacion_financiera")
            and self.aprobacion_financiera.fecha_pago is not None
        )

    @property
    def transitario_ha_pagado(self):
        """Verifica si el transitario ha pagado al puerto (calculado)"""
        return (
            hasattr(self, "aprobacion_pago_transitario")
            and self.aprobacion_pago_transitario.pago_realizado
        )

    @property
    def ultimo_evento(self):
        """Retorna el último evento registrado del contenedor"""
        return self.eventos.order_by("-fecha_hora").first()

    @property
    def ultimo_estado(self):
        """Retorna el tipo del último evento como estado actual"""
        evento = self.ultimo_evento
        return evento.get_tipo_evento_display() if evento else "Sin movimientos"

    def __str__(self):
        direccion_label = "IMP" if self.direccion == "IMPORT" else "EXP"
        return f"{self.codigo_iso} ({direccion_label}) - {self.bl_referencia}"


# ====== CUN07: EVENTOS/TRACKING DE CONTENEDOR ======
class EventoContenedor(models.Model):
    """Registro de eventos/movimientos del contenedor para tracking"""

    TIPO_EVENTO_CHOICES = [
        # Eventos en origen
        ("GATE_OUT_EMPTY", "Gate Out Empty - Salida vacío"),
        ("GATE_IN_FULL", "Gate In Full - Ingreso cargado"),
        ("LOADED", "Loaded - Cargado al buque"),
        # Eventos en tránsito
        ("DEPARTED", "Departed - Zarpe del buque"),
        ("IN_TRANSIT", "In Transit - En tránsito"),
        ("TRANSSHIPMENT", "Transshipment - Transbordo"),
        ("ARRIVED", "Arrived - Arribo del buque"),
        # Eventos en destino
        ("DISCHARGED", "Discharged - Descargado del buque"),
        ("GATE_OUT_FULL", "Gate Out Full - Salida cargado"),
        ("DELIVERED", "Delivered - Entregado"),
        ("GATE_IN_EMPTY", "Gate In Empty - Devolución vacío"),
        # Eventos especiales
        ("CUSTOMS_HOLD", "Customs Hold - Retención aduanera"),
        ("CUSTOMS_RELEASED", "Customs Released - Liberado aduana"),
        ("INSPECTION", "Inspection - En inspección"),
        ("DAMAGED", "Damaged - Daño reportado"),
    ]

    MEDIO_TRANSPORTE_CHOICES = [
        ("VESSEL", "Buque"),
        ("TRUCK", "Camión"),
        ("RAIL", "Ferrocarril"),
        ("BARGE", "Barcaza"),
    ]

    contenedor = models.ForeignKey(
        Contenedor,
        on_delete=models.CASCADE,
        related_name="eventos",
        verbose_name="Contenedor",
    )
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name="Tipo de Evento",
    )
    fecha_hora = models.DateTimeField(
        verbose_name="Fecha y Hora",
        help_text="Momento en que ocurrió el evento",
    )
    # Ubicación del evento
    ubicacion_puerto = models.CharField(
        max_length=120,
        verbose_name="Puerto",
        help_text="Puerto donde ocurrió el evento",
    )
    ubicacion_ciudad = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Ciudad",
    )
    ubicacion_pais = models.CharField(
        max_length=60,
        verbose_name="País",
    )
    # Transporte asociado
    buque = models.ForeignKey(
        Buque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_contenedores",
        verbose_name="Buque",
        help_text="Buque asociado al evento (si aplica)",
    )
    medio_transporte = models.CharField(
        max_length=10,
        choices=MEDIO_TRANSPORTE_CHOICES,
        default="VESSEL",
        verbose_name="Medio de Transporte",
    )
    # Información adicional
    referencia_viaje = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Referencia de Viaje",
        help_text="Número de viaje o voyage del buque",
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Observaciones adicionales del evento",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento de Contenedor"
        verbose_name_plural = "Eventos de Contenedores"
        ordering = ["-fecha_hora"]
        indexes = [
            models.Index(fields=["contenedor", "-fecha_hora"]),
            models.Index(fields=["tipo_evento"]),
            models.Index(fields=["fecha_hora"]),
        ]

    def __str__(self):
        return f"{self.contenedor.codigo_iso} - {self.get_tipo_evento_display()} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"


# ====== CUN04: PERMISOS ADUANEROS (1-1 opcional) ======
class AprobacionAduanera(models.Model):
    """Registro de aprobaciones aduaneras por contenedor"""

    contenedor = models.OneToOneField(
        Contenedor,
        on_delete=models.PROTECT,
        related_name="aprobacion_aduanera",
        verbose_name="Contenedor",
    )
    numero_despacho = models.CharField(max_length=30, verbose_name="Número de Despacho")
    fecha_revision = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de Revisión"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    aprobado = models.BooleanField(
        default=False,
        verbose_name="Aprobado",
        help_text="Indica si la aduana aprobó el despacho",
    )
    fecha_levante = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Levante",
        help_text="Fecha en que se autoriza el retiro del contenedor",
    )
    documento_adjunto = models.FileField(
        upload_to="documentos/aduaneros/%Y/%m/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"]),
            validate_document_size,
        ],
        null=True,
        blank=True,
        verbose_name="Documento Adjunto",
        help_text="Sube el documento aduanero en formato PDF, JPG o PNG (máx. 5MB)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aprobación Aduanera"
        verbose_name_plural = "Aprobaciones Aduaneras"
        ordering = ["-created_at"]

    def clean(self):
        if self.aprobado and not self.fecha_levante:
            raise ValidationError(
                {
                    "fecha_levante": "Si está aprobado, debe especificar la fecha de levante"
                }
            )

    def __str__(self):
        estado = "Aprobado" if self.aprobado else "Pendiente"
        return f"{self.contenedor.codigo_iso} - {estado}"


# ====== CUN05: REGISTRO FACTURAS AL CLIENTE (1-1 opcional) ======
class AprobacionFinanciera(models.Model):
    """Registro de facturas emitidas al cliente por contenedor"""

    contenedor = models.OneToOneField(
        Contenedor,
        on_delete=models.PROTECT,
        related_name="aprobacion_financiera",
        verbose_name="Contenedor",
    )
    numero_factura = models.CharField(
        max_length=30, unique=True, verbose_name="Número de Factura"
    )
    monto_usd = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Monto (USD)"
    )
    servicios_facturados = models.CharField(
        max_length=120, verbose_name="Servicios Facturados"
    )
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión")
    fecha_vencimiento = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Vencimiento"
    )
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    aprobado = models.BooleanField(
        default=False,
        verbose_name="Aprobado",
        help_text="Indica si la factura fue aprobada internamente",
    )
    documento_adjunto = models.FileField(
        upload_to="documentos/facturas/%Y/%m/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"]),
            validate_document_size,
        ],
        null=True,
        blank=True,
        verbose_name="Factura Adjunta",
        help_text="Sube la factura en formato PDF, JPG o PNG (máx. 5MB)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aprobación Financiera"
        verbose_name_plural = "Aprobaciones Financieras"
        ordering = ["-fecha_emision"]
        indexes = [
            models.Index(fields=["numero_factura"]),
            models.Index(fields=["fecha_pago"]),
        ]

    def clean(self):
        if self.fecha_vencimiento and self.fecha_emision:
            if self.fecha_vencimiento < self.fecha_emision:
                raise ValidationError(
                    {
                        "fecha_vencimiento": "La fecha de vencimiento no puede ser anterior a la fecha de emisión"
                    }
                )

    @property
    def esta_vencida(self):
        """Verifica si la factura está vencida"""
        from django.utils import timezone

        if not self.fecha_vencimiento or self.fecha_pago:
            return False
        return timezone.now().date() > self.fecha_vencimiento

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.contenedor.codigo_iso}"


# ====== APROBACIÓN PAGO TRANSITARIO (1-1 opcional) ======
class AprobacionPagoTransitario(models.Model):
    """Registro de pagos realizados por transitarios al puerto"""

    contenedor = models.OneToOneField(
        Contenedor,
        on_delete=models.PROTECT,
        related_name="aprobacion_pago_transitario",
        verbose_name="Contenedor",
    )
    transitario = models.ForeignKey(
        Transitario,
        on_delete=models.PROTECT,
        related_name="pagos",
        verbose_name="Transitario",
        help_text="Transitario que realiza el pago",
    )
    pago_realizado = models.BooleanField(default=False, verbose_name="Pago Realizado")
    monto_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Monto Pagado (USD)",
    )
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    documento_adjunto = models.FileField(
        upload_to="documentos/pagos_transitarios/%Y/%m/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"]),
            validate_document_size,
        ],
        null=True,
        blank=True,
        verbose_name="Comprobante de Pago",
        help_text="Sube el comprobante de pago en formato PDF, JPG o PNG (máx. 5MB)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aprobación Pago Transitario"
        verbose_name_plural = "Aprobaciones Pago Transitario"
        ordering = ["-created_at"]

    def clean(self):
        if self.pago_realizado and not self.fecha_pago:
            raise ValidationError(
                {
                    "fecha_pago": "Si el pago está realizado, debe especificar la fecha de pago"
                }
            )
        if self.pago_realizado and not self.monto_pagado:
            raise ValidationError(
                {
                    "monto_pagado": "Si el pago está realizado, debe especificar el monto pagado"
                }
            )

    def __str__(self):
        estado = "Pagado" if self.pago_realizado else "Pendiente"
        return f"{self.contenedor.codigo_iso} - {self.transitario} - {estado}"


# ====== CUN07: QUEJAS ======
def queja_imagen_path(instance, filename):
    """Genera la ruta para guardar imágenes de quejas"""
    import os
    from uuid import uuid4

    ext = filename.split(".")[-1]
    new_filename = f"{uuid4().hex[:8]}.{ext}"
    return os.path.join("quejas", new_filename)


class Queja(models.Model):
    """Registro de quejas de clientes"""

    CATEGORIA_CHOICES = [
        ("DEMORA", "Demora en Entrega"),
        ("DAÑO", "Daño en Mercancía"),
        ("DOCUMENTACION", "Problemas de Documentación"),
        ("ATENCION", "Atención al Cliente"),
        ("COBRO", "Problemas de Cobro"),
        ("OTRO", "Otro"),
    ]

    ESTADO_CHOICES = [
        ("SIN_ESTADO", "Sin Estado"),
        ("EN_PROCESO", "En Proceso"),
        ("SOLUCIONADA", "Solucionada"),
        ("ARCHIVADA", "Archivada"),
    ]

    email_cliente = models.EmailField(verbose_name="Email del Cliente")
    nombre_cliente = models.CharField(max_length=120, verbose_name="Nombre del Cliente")
    categoria = models.CharField(
        max_length=20, choices=CATEGORIA_CHOICES, verbose_name="Categoría"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="SIN_ESTADO",
        verbose_name="Estado",
    )
    descripcion = models.TextField(verbose_name="Descripción")
    # Hasta 3 imágenes adjuntas
    imagen1 = models.ImageField(
        upload_to=queja_imagen_path,
        blank=True,
        null=True,
        verbose_name="Imagen 1",
    )
    imagen2 = models.ImageField(
        upload_to=queja_imagen_path,
        blank=True,
        null=True,
        verbose_name="Imagen 2",
    )
    imagen3 = models.ImageField(
        upload_to=queja_imagen_path,
        blank=True,
        null=True,
        verbose_name="Imagen 3",
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Queja"
        verbose_name_plural = "Quejas"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["estado", "fecha_creacion"]),
            models.Index(fields=["categoria"]),
        ]

    @property
    def cantidad_contenedores(self):
        """Cantidad de contenedores afectados por esta queja (calculado)"""
        return self.contenedores_afectados.count()

    def __str__(self):
        return f"Queja #{self.id} - {self.get_categoria_display()} - {self.estado}"


# ====== TABLA INTERMEDIA: QUEJA-CONTENEDOR (M:N) ======
class QuejaContenedor(models.Model):
    """Relación entre quejas y contenedores afectados"""

    queja = models.ForeignKey(
        Queja,
        on_delete=models.CASCADE,
        related_name="contenedores_afectados",
        verbose_name="Queja",
    )
    contenedor = models.ForeignKey(
        Contenedor,
        on_delete=models.CASCADE,
        related_name="quejas_relacionadas",
        verbose_name="Contenedor",
    )
    observaciones_especificas = models.TextField(
        blank=True,
        verbose_name="Observaciones Específicas",
        help_text="Detalles específicos de este contenedor en relación a la queja",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contenedor Afectado por Queja"
        verbose_name_plural = "Contenedores Afectados por Quejas"
        unique_together = ["queja", "contenedor"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Queja #{self.queja.id} - {self.contenedor.codigo_iso}"
