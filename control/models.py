import re

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

# from django.utils.translation import gettext_lazy as _


# ====== CONSTANTES PARA TIPOS DE CONTENEDOR ======
# Códigos ISO 6346 Tipo/Tamaño con tara aproximada en kg
TIPOS_CONTENEDOR = {
    # 20 pies (6m)
    "22G1": {"nombre": "20' Dry Standard", "tara_kg": 2200, "capacidad_m3": 33},
    "22G0": {
        "nombre": "20' Dry Standard (ventilado)",
        "tara_kg": 2300,
        "capacidad_m3": 33,
    },
    "22R1": {"nombre": "20' Reefer", "tara_kg": 3100, "capacidad_m3": 28},
    "22U1": {"nombre": "20' Open Top", "tara_kg": 2300, "capacidad_m3": 32},
    "22P1": {"nombre": "20' Flat Rack", "tara_kg": 2500, "capacidad_m3": 0},
    "22T1": {"nombre": "20' Tank", "tara_kg": 3600, "capacidad_m3": 21},
    # 40 pies (12m)
    "42G1": {"nombre": "40' Dry Standard", "tara_kg": 3800, "capacidad_m3": 67},
    "42G0": {
        "nombre": "40' Dry Standard (ventilado)",
        "tara_kg": 3900,
        "capacidad_m3": 67,
    },
    "45G1": {"nombre": "40' High Cube (HC)", "tara_kg": 3900, "capacidad_m3": 76},
    "42R1": {"nombre": "40' Reefer", "tara_kg": 4500, "capacidad_m3": 60},
    "45R1": {"nombre": "40' Reefer High Cube", "tara_kg": 4800, "capacidad_m3": 67},
    "42U1": {"nombre": "40' Open Top", "tara_kg": 4000, "capacidad_m3": 65},
    "42P1": {"nombre": "40' Flat Rack", "tara_kg": 4200, "capacidad_m3": 0},
    # 45 pies
    "L5G1": {"nombre": "45' High Cube", "tara_kg": 4800, "capacidad_m3": 86},
}

TIPO_CONTENEDOR_CHOICES = [
    (codigo, f"{codigo} - {info['nombre']}")
    for codigo, info in TIPOS_CONTENEDOR.items()
]


# ====== CONSTANTES PARA SELLOS ======
TIPOS_SELLO = {
    "NAVIERA": "Sello de Naviera (Bolt Seal)",
    "ADUANAS": "Sello de Aduanas",
    "SENASA": "Sello Veterinario/SENASA",
    "EXPORTADOR": "Sello del Exportador",
    "OTRO": "Otro tipo de sello",
}


# ====== VALIDADORES PERSONALIZADOS ======
def validate_and_sanitize_sello(codigo):
    """
    Sanitiza y valida un código de sello individual.
    - Elimina espacios
    - Convierte a mayúsculas
    - Solo permite alfanuméricos y guiones

    Returns: código sanitizado
    Raises: ValidationError si el código es inválido
    """
    if not codigo:
        return ""

    # Trim y eliminar espacios internos
    codigo = codigo.strip().replace(" ", "")

    # Mayúsculas
    codigo = codigo.upper()

    # Solo alfanuméricos y guiones
    if not re.match(r"^[A-Z0-9\-]+$", codigo):
        raise ValidationError(
            f"El código de sello '{codigo}' contiene caracteres inválidos. "
            "Solo se permiten letras, números y guiones."
        )

    # Longitud mínima
    if len(codigo) < 4:
        raise ValidationError(
            f"El código de sello '{codigo}' es muy corto. Mínimo 4 caracteres."
        )

    return codigo


def validate_sellos_format(value):
    """
    Valida el formato de múltiples sellos.
    Formato: TIPO:CODIGO*|TIPO:CODIGO|...
    El * indica el sello principal.

    Ejemplo: NAVIERA:HL123456*|ADUANAS:AD789012
    """
    if not value:
        raise ValidationError("Debe ingresar al menos un sello.")

    value = value.strip()
    sellos = value.split("|")
    codigos_vistos = set()
    tiene_principal = False

    for sello in sellos:
        sello = sello.strip()
        if not sello:
            continue

        # Verificar formato TIPO:CODIGO
        if ":" not in sello:
            raise ValidationError(
                f"Formato inválido en '{sello}'. Use TIPO:CODIGO (ej: NAVIERA:HL123456)"
            )

        partes = sello.split(":", 1)
        if len(partes) != 2:
            raise ValidationError(f"Formato inválido en '{sello}'.")

        tipo, codigo = partes
        tipo = tipo.upper().strip()

        # Verificar tipo válido
        if tipo not in TIPOS_SELLO:
            tipos_validos = ", ".join(TIPOS_SELLO.keys())
            raise ValidationError(
                f"Tipo de sello '{tipo}' no válido. Tipos permitidos: {tipos_validos}"
            )

        # Verificar si es principal (tiene *)
        es_principal = codigo.endswith("*")
        if es_principal:
            codigo = codigo[:-1]  # Quitar el *
            if tiene_principal:
                raise ValidationError(
                    "Solo puede haber un sello principal (marcado con ⭐)."
                )
            tiene_principal = True

        # Sanitizar código
        codigo = validate_and_sanitize_sello(codigo)

        # Verificar duplicados en este contenedor
        if codigo in codigos_vistos:
            raise ValidationError(f"El código de sello '{codigo}' está duplicado.")
        codigos_vistos.add(codigo)

    if not tiene_principal:
        raise ValidationError(
            "Debe marcar un sello como principal (sello de la Naviera)."
        )


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
        from django.utils import timezone

        # Validar ETD >= ETA
        if self.fecha_etd and self.fecha_eta:
            if self.fecha_etd < self.fecha_eta:
                raise ValidationError(
                    {"fecha_etd": "La fecha ETD no puede ser anterior a la fecha ETA"}
                )

        # Validar fecha_arribo_real no puede estar en el futuro
        if self.fecha_arribo_real:
            now = timezone.now()
            if self.fecha_arribo_real > now:
                raise ValidationError(
                    {
                        "fecha_arribo_real": "La fecha de arribo real no puede estar en el futuro"
                    }
                )

        # Validar fecha_arribo_real solo permitida si estado no es PROGRAMADO ni EN_RUTA
        if self.fecha_arribo_real and self.estado in ["PROGRAMADO", "EN_RUTA"]:
            raise ValidationError(
                {
                    "fecha_arribo_real": "No se puede establecer fecha de arribo real cuando el estado es PROGRAMADO o EN RUTA"
                }
            )

        # Validar contenedores según tipo_operacion
        # Solo se requiere que el campo correspondiente tenga valor > 0
        if self.tipo_operacion == "DESCARGA":
            if self.contenedores_descarga == 0:
                raise ValidationError(
                    {
                        "contenedores_descarga": "Debe especificar contenedores para descarga"
                    }
                )
            # Limpiar campo de carga (no aplica)
            self.contenedores_carga = 0

        elif self.tipo_operacion == "CARGA":
            if self.contenedores_carga == 0:
                raise ValidationError(
                    {"contenedores_carga": "Debe especificar contenedores para carga"}
                )
            # Limpiar campo de descarga (no aplica)
            self.contenedores_descarga = 0

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
        help_text="Se extrae automáticamente del Código ISO (primeras 3 letras)",
        blank=True,
    )
    tipo_tamaño = models.CharField(
        max_length=10,
        choices=TIPO_CONTENEDOR_CHOICES,
        verbose_name="Tipo/Tamaño",
        help_text="Código ISO del tipo de contenedor",
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
    # Campo de sellos con formato: TIPO:CODIGO*|TIPO:CODIGO
    # El * indica sello principal. Tipos: NAVIERA, ADUANAS, SENASA, EXPORTADOR, OTRO
    numero_sello = models.CharField(
        max_length=500,
        verbose_name="Sellos del Contenedor",
        help_text="Ingrese los sellos del contenedor. El sello de Naviera es obligatorio.",
        validators=[validate_sellos_format],
    )
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
    # === Campo de bloqueo por eventos ===
    bloqueado_por_evento = models.BooleanField(
        default=False,
        verbose_name="Bloqueado por Evento",
        help_text="Se activa automáticamente por eventos como Customs Hold, Damaged o Inspection",
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
        from django.core.exceptions import ValidationError

        # Validación de campos obligatorios primero
        errors = {}
        if not self.arribo_id:
            errors["arribo"] = "Debe seleccionar un arribo"
        if not self.direccion:
            errors["direccion"] = "Debe seleccionar la dirección (Import/Export)"

        if errors:
            raise ValidationError(errors)

        # Auto-llenar BIC propietario desde el código ISO
        if self.codigo_iso and len(self.codigo_iso) >= 3:
            self.bic_propietario = self.codigo_iso[:3].upper()

        # ====== VALIDACIÓN DE CAPACIDAD DEL ARRIBO ======
        # No permitir registrar más contenedores de los declarados en el Arribo
        if self.arribo and self.direccion:
            # Contar contenedores ya registrados (excluyendo el actual si es edición)
            contenedores_existentes = Contenedor.objects.filter(
                arribo=self.arribo, direccion=self.direccion
            )
            if self.pk:  # Si es edición, excluir el registro actual
                contenedores_existentes = contenedores_existentes.exclude(pk=self.pk)

            cantidad_registrada = contenedores_existentes.count()

            if self.direccion == "IMPORT":
                capacidad_declarada = self.arribo.contenedores_descarga
                tipo_texto = "importación (descarga)"
            else:  # EXPORT
                capacidad_declarada = self.arribo.contenedores_carga
                tipo_texto = "exportación (carga)"

            # Validar que no se exceda la capacidad
            if cantidad_registrada >= capacidad_declarada:
                raise ValidationError(
                    {
                        "direccion": f"El arribo '{self.arribo}' ya tiene {cantidad_registrada} de {capacidad_declarada} "
                        f"contenedores de {tipo_texto} registrados. No se pueden agregar más."
                    }
                )

        # Validación de peso bruto > tara
        if self.peso_bruto_kg and self.tara_kg:
            if self.peso_bruto_kg < self.tara_kg:
                raise ValidationError(
                    {"peso_bruto_kg": "El peso bruto no puede ser menor que la tara"}
                )

        # Validación de fecha_retiro_transitario según dirección
        if self.fecha_retiro_transitario and self.arribo:
            if self.direccion == "IMPORT":
                # Import: fecha de retiro no puede ser anterior al ETA
                if (
                    self.arribo.fecha_eta
                    and self.fecha_retiro_transitario < self.arribo.fecha_eta
                ):
                    raise ValidationError(
                        {
                            "fecha_retiro_transitario": f"La fecha de retiro no puede ser anterior a la llegada del buque (ETA: {self.arribo.fecha_eta.strftime('%d/%m/%Y %H:%M')})"
                        }
                    )
            elif self.direccion == "EXPORT":
                # Export: fecha de entrega no puede ser posterior al ETD (cut-off)
                if (
                    self.arribo.fecha_etd
                    and self.fecha_retiro_transitario > self.arribo.fecha_etd
                ):
                    raise ValidationError(
                        {
                            "fecha_retiro_transitario": f"La fecha de entrega no puede ser posterior a la salida del buque (ETD: {self.arribo.fecha_etd.strftime('%d/%m/%Y %H:%M')})"
                        }
                    )

        # Validar duplicidad de sellos con otros contenedores activos
        if self.numero_sello:
            mis_codigos = self.get_codigos_sello()
            # Buscar contenedores con sellos duplicados (excluyendo este)
            contenedores = Contenedor.objects.exclude(pk=self.pk)
            for contenedor in contenedores:
                otros_codigos = contenedor.get_codigos_sello()
                duplicados = mis_codigos.intersection(otros_codigos)
                if duplicados:
                    raise ValidationError(
                        {
                            "numero_sello": f"🚨 ALERTA: El sello '{', '.join(duplicados)}' ya está registrado "
                            f"en el contenedor {contenedor.codigo_iso}. "
                            "Esto podría indicar un error de tipeo o un intento de fraude."
                        }
                    )

    def get_codigos_sello(self):
        """Extrae todos los códigos de sello como un set (sin tipo ni marcador principal)"""
        if not self.numero_sello:
            return set()

        codigos = set()
        for sello in self.numero_sello.split("|"):
            if ":" in sello:
                _, codigo = sello.split(":", 1)
                codigo = codigo.replace("*", "").strip().upper()
                if codigo:
                    codigos.add(codigo)
        return codigos

    def get_sello_principal(self):
        """Retorna el código del sello principal (marcado con *)"""
        if not self.numero_sello:
            return None

        for sello in self.numero_sello.split("|"):
            if "*" in sello and ":" in sello:
                _, codigo = sello.split(":", 1)
                return codigo.replace("*", "").strip().upper()
        return None

    def get_sellos_lista(self):
        """
        Retorna lista de diccionarios con info de cada sello.
        Útil para templates y APIs.
        """
        if not self.numero_sello:
            return []

        sellos = []
        for sello in self.numero_sello.split("|"):
            sello = sello.strip()
            if ":" not in sello:
                continue
            tipo, codigo = sello.split(":", 1)
            es_principal = codigo.endswith("*")
            codigo = codigo.replace("*", "").strip().upper()
            sellos.append(
                {
                    "tipo": tipo.strip().upper(),
                    "tipo_display": TIPOS_SELLO.get(tipo.strip().upper(), tipo),
                    "codigo": codigo,
                    "es_principal": es_principal,
                }
            )
        return sellos

    @property
    def sello_principal_display(self):
        """Para mostrar en listados: solo el sello principal"""
        principal = self.get_sello_principal()
        return principal if principal else "Sin sello principal"

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
        # ══════ INICIO: Preparación y carga ══════
        ("GATE_OUT_EMPTY", "1. Gate Out Empty - Salida vacío (retiro)"),
        ("GATE_IN_FULL", "2. Gate In Full - Ingreso cargado"),
        ("LOADED", "3. Loaded - Cargado al buque"),
        # ══════ INTERMEDIO: Tránsito marítimo ══════
        ("DEPARTED", "4. Departed - Zarpe del buque"),
        ("IN_TRANSIT", "5. In Transit - En tránsito"),
        ("TRANSSHIPMENT", "6. Transshipment - Transbordo"),
        ("ARRIVED", "7. Arrived - Arribo del buque"),
        # ══════ FINAL: Descarga y entrega ══════
        ("DISCHARGED", "8. Discharged - Descargado del buque"),
        ("GATE_OUT_FULL", "9. Gate Out Full - Salida cargado"),
        ("DELIVERED", "10. Delivered - Entregado al cliente"),
        ("GATE_IN_EMPTY", "11. Gate In Empty - Devolución vacío"),
        # ══════ EXCEPCIONES: Eventos especiales ══════
        ("CUSTOMS_HOLD", "⚠️ Customs Hold - Retención aduanera"),
        ("CUSTOMS_RELEASED", "✅ Customs Released - Liberado aduana"),
        ("INSPECTION", "🔍 Inspection - En inspección"),
        ("DAMAGED", "❌ Damaged - Daño reportado"),
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
        verbose_name="Lugar",
        help_text="Puerto, terminal, almacén o dirección del evento",
    )
    ubicacion_ciudad = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Ciudad",
        help_text="Ciudad (no aplica para eventos en tránsito marítimo)",
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

    # Eventos que son locales (auto-llenan ubicación del puerto local)
    EVENTOS_LOCALES = [
        "GATE_IN_FULL",
        "GATE_IN_EMPTY",
        "GATE_OUT_FULL",
        "GATE_OUT_EMPTY",
        "DISCHARGED",
        "LOADED",
        "INSPECTION",
        "CUSTOMS_HOLD",
        "CUSTOMS_RELEASED",
        "DELIVERED",
    ]

    # Eventos marítimos (requieren buque)
    EVENTOS_MARITIMOS = [
        "LOADED",
        "DEPARTED",
        "IN_TRANSIT",
        "TRANSSHIPMENT",
        "ARRIVED",
        "DISCHARGED",
    ]

    # Eventos terrestres (camión/ferrocarril)
    EVENTOS_TERRESTRES = [
        "GATE_IN_FULL",
        "GATE_IN_EMPTY",
        "GATE_OUT_FULL",
        "GATE_OUT_EMPTY",
        "DELIVERED",
    ]

    # Eventos para Importación
    EVENTOS_IMPORTACION = [
        "ARRIVED",
        "DISCHARGED",
        "CUSTOMS_HOLD",
        "CUSTOMS_RELEASED",
        "INSPECTION",
        "GATE_OUT_FULL",
        "DELIVERED",
        "GATE_IN_EMPTY",
        "DAMAGED",
    ]

    # Eventos para Exportación
    EVENTOS_EXPORTACION = [
        "GATE_OUT_EMPTY",
        "GATE_IN_FULL",
        "CUSTOMS_HOLD",
        "CUSTOMS_RELEASED",
        "INSPECTION",
        "LOADED",
        "DEPARTED",
        "IN_TRANSIT",
        "DAMAGED",
    ]

    # Eventos de alerta (bloquean Gate Pass)
    EVENTOS_BLOQUEO = ["CUSTOMS_HOLD", "DAMAGED", "INSPECTION"]

    # Eventos que liberan bloqueo
    EVENTOS_LIBERACION = ["CUSTOMS_RELEASED"]

    # ══════ SECUENCIA LÓGICA DE EVENTOS ══════
    # Define el orden numérico de cada evento en el flujo normal
    # Los eventos especiales (CUSTOMS_HOLD, etc.) no tienen número - pueden ocurrir en cualquier momento
    SECUENCIA_EVENTOS = {
        "GATE_OUT_EMPTY": 1,
        "GATE_IN_FULL": 2,
        "LOADED": 3,
        "DEPARTED": 4,
        "IN_TRANSIT": 5,
        "TRANSSHIPMENT": 6,
        "ARRIVED": 7,
        "DISCHARGED": 8,
        "GATE_OUT_FULL": 9,
        "DELIVERED": 10,
        "GATE_IN_EMPTY": 11,
        # Eventos especiales - sin número, pueden ocurrir en cualquier momento
        "CUSTOMS_HOLD": None,
        "CUSTOMS_RELEASED": None,
        "INSPECTION": None,
        "DAMAGED": None,
    }

    # Prerrequisitos: qué eventos deben existir antes de poder registrar otro
    PRERREQUISITOS_EVENTOS = {
        # Para cargar al buque, debe haber ingresado al puerto
        "LOADED": ["GATE_IN_FULL"],
        # Para zarpar, debe estar cargado
        "DEPARTED": ["LOADED"],
        # Para estar en tránsito, debe haber zarpado
        "IN_TRANSIT": ["DEPARTED"],
        # Para transbordo, debe estar en tránsito o haber llegado
        "TRANSSHIPMENT": ["IN_TRANSIT", "ARRIVED"],
        # Para arribar, debe haber zarpado o estar en tránsito
        "ARRIVED": ["DEPARTED", "IN_TRANSIT", "TRANSSHIPMENT"],
        # Para descargar, debe haber arribado
        "DISCHARGED": ["ARRIVED"],
        # Para salir cargado, debe estar descargado y liberado
        "GATE_OUT_FULL": ["DISCHARGED"],
        # Para entregar, debe haber salido del puerto
        "DELIVERED": ["GATE_OUT_FULL"],
        # Para devolver vacío, debe haberse entregado
        "GATE_IN_EMPTY": ["DELIVERED"],
        # Liberación aduanera requiere retención previa
        "CUSTOMS_RELEASED": ["CUSTOMS_HOLD"],
    }

    class Meta:
        verbose_name = "Evento de Contenedor"
        verbose_name_plural = "Eventos de Contenedores"
        ordering = ["-fecha_hora"]
        indexes = [
            models.Index(fields=["contenedor", "-fecha_hora"]),
            models.Index(fields=["tipo_evento"]),
            models.Index(fields=["fecha_hora"]),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}

        # Validación cronológica: el evento no puede ser anterior al último evento
        if self.contenedor_id and self.fecha_hora:
            ultimo_evento = (
                EventoContenedor.objects.filter(contenedor_id=self.contenedor_id)
                .exclude(pk=self.pk)
                .order_by("-fecha_hora")
                .first()
            )
            if ultimo_evento and self.fecha_hora < ultimo_evento.fecha_hora:
                errors["fecha_hora"] = (
                    f"Cronología incoherente: Este evento no puede ser anterior al último evento "
                    f"({ultimo_evento.get_tipo_evento_display()} - {ultimo_evento.fecha_hora.strftime('%d/%m/%Y %H:%M')})"
                )

        # ══════ VALIDACIÓN DE SECUENCIA LÓGICA ══════
        if self.contenedor_id and self.tipo_evento:
            eventos_existentes = set(
                EventoContenedor.objects.filter(contenedor_id=self.contenedor_id)
                .exclude(pk=self.pk)
                .values_list("tipo_evento", flat=True)
            )

            # 1. Verificar prerrequisitos
            if self.tipo_evento in self.PRERREQUISITOS_EVENTOS:
                prerrequisitos = self.PRERREQUISITOS_EVENTOS[self.tipo_evento]
                # Al menos uno de los prerrequisitos debe existir
                if not any(prereq in eventos_existentes for prereq in prerrequisitos):
                    prereq_nombres = [
                        dict(self.TIPO_EVENTO_CHOICES).get(p, p) for p in prerrequisitos
                    ]
                    errors["tipo_evento"] = (
                        f"Secuencia inválida: Para registrar '{self.get_tipo_evento_display()}' "
                        f"primero debe existir alguno de estos eventos: {', '.join(prereq_nombres)}"
                    )

            # 2. Verificar que no se salten eventos en la secuencia numérica
            num_evento_nuevo = self.SECUENCIA_EVENTOS.get(self.tipo_evento)
            if num_evento_nuevo:  # Solo para eventos numerados
                for evento_existente in eventos_existentes:
                    num_existente = self.SECUENCIA_EVENTOS.get(evento_existente)
                    if num_existente and num_existente > num_evento_nuevo:
                        # Hay un evento posterior ya registrado
                        nombre_existente = dict(self.TIPO_EVENTO_CHOICES).get(
                            evento_existente, evento_existente
                        )
                        errors["tipo_evento"] = (
                            f"Secuencia inválida: No puede registrar '{self.get_tipo_evento_display()}' "
                            f"porque ya existe un evento posterior: '{nombre_existente}'"
                        )
                        break

            # 3. Evitar eventos duplicados (excepto los especiales que pueden repetirse)
            eventos_no_repetibles = [
                "GATE_OUT_EMPTY",
                "GATE_IN_FULL",
                "LOADED",
                "DEPARTED",
                "ARRIVED",
                "DISCHARGED",
                "GATE_OUT_FULL",
                "DELIVERED",
                "GATE_IN_EMPTY",
            ]
            if (
                self.tipo_evento in eventos_no_repetibles
                and self.tipo_evento in eventos_existentes
            ):
                errors["tipo_evento"] = (
                    f"Este evento ya fue registrado para este contenedor. "
                    f"'{self.get_tipo_evento_display()}' solo puede ocurrir una vez."
                )

        # Validar que eventos marítimos tengan buque
        if self.tipo_evento in self.EVENTOS_MARITIMOS and not self.buque_id:
            errors["buque"] = "Los eventos marítimos requieren seleccionar un buque"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # ══════ AUTO-ASIGNACIÓN DE CAMPOS SEGÚN TIPO DE EVENTO ══════
        # Esto soluciona el problema de campos deshabilitados por JS que no se envían

        # Mapeo de eventos a medio de transporte requerido
        MEDIO_POR_EVENTO = {
            # Eventos marítimos → VESSEL
            "LOADED": "VESSEL",
            "DEPARTED": "VESSEL",
            "IN_TRANSIT": "VESSEL",
            "TRANSSHIPMENT": "VESSEL",
            "ARRIVED": "VESSEL",
            "DISCHARGED": "VESSEL",
            # Eventos terrestres → TRUCK
            "GATE_OUT_EMPTY": "TRUCK",
            "GATE_IN_FULL": "TRUCK",
            "GATE_OUT_FULL": "TRUCK",
            "GATE_IN_EMPTY": "TRUCK",
            "DELIVERED": "TRUCK",
            # Eventos especiales → mantener el valor actual o TRUCK por defecto
        }

        # Asignar medio de transporte automáticamente según tipo de evento
        if self.tipo_evento in MEDIO_POR_EVENTO:
            self.medio_transporte = MEDIO_POR_EVENTO[self.tipo_evento]
        elif not self.medio_transporte:
            # Para eventos especiales sin medio asignado, usar TRUCK por defecto
            self.medio_transporte = "TRUCK"

        # Limpiar campos que no aplican para eventos terrestres
        if self.tipo_evento in self.EVENTOS_TERRESTRES:
            self.buque = None
            self.referencia_viaje = ""

        # Limpiar ciudad para eventos en tránsito (aguas internacionales)
        if self.tipo_evento == "IN_TRANSIT":
            self.ubicacion_ciudad = ""

        super().save(*args, **kwargs)
        # Actualizar estado de bloqueo del contenedor después de guardar
        self._actualizar_bloqueo_contenedor()

    def _actualizar_bloqueo_contenedor(self):
        """Actualiza el estado de bloqueo del contenedor según eventos"""
        if not self.contenedor_id:
            return

        # Verificar si hay eventos de bloqueo activos sin liberación posterior
        eventos = EventoContenedor.objects.filter(
            contenedor_id=self.contenedor_id
        ).order_by("fecha_hora")

        bloqueado = False
        for evento in eventos:
            if evento.tipo_evento in self.EVENTOS_BLOQUEO:
                bloqueado = True
            elif evento.tipo_evento in self.EVENTOS_LIBERACION:
                bloqueado = False

        # Actualizar el contenedor
        Contenedor.objects.filter(pk=self.contenedor_id).update(
            bloqueado_por_evento=bloqueado
        )

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
    numero_despacho = models.CharField(
        max_length=30,
        verbose_name="Número de Despacho (DAM/DUA)",
        help_text="Formato: AAA-AAAA-RR-NNNNNN o AAA-AAAA-RR-NNNNNN-SS. Ejemplo: 118-2025-10-012345",
    )
    fecha_revision = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Revisión",
        help_text="Fecha en que se realizó la revisión aduanera. No puede ser futura.",
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
        help_text="Obligatorio si NO está aprobado (indique el motivo del rechazo)",
    )
    aprobado = models.BooleanField(
        default=False,
        verbose_name="Aprobado",
        help_text="Indica si la aduana aprobó el despacho",
    )
    fecha_levante = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Levante",
        help_text="Fecha en que se autoriza el retiro del contenedor. Obligatorio si está aprobado.",
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
        help_text="Documento legal de aprobación. Obligatorio si está aprobado.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aprobación Aduanera"
        verbose_name_plural = "Aprobaciones Aduaneras"
        ordering = ["-created_at"]

    def clean(self):
        import re

        from django.utils import timezone

        errors = {}

        # === Validación del Número de Despacho DAM/DUA ===
        if self.numero_despacho:
            # Limpiar espacios al inicio y final
            numero_limpio = self.numero_despacho.strip()

            # Verificar que no haya espacios internos
            if " " in numero_limpio:
                errors["numero_despacho"] = (
                    "El número de despacho no puede contener espacios. "
                    "Formato correcto: 118-2025-10-012345"
                )
            else:
                # Patrón: AAA-AAAA-RR-NNNNNN o AAA-AAAA-RR-NNNNNN-SS
                patron_dam = r"^\d{3}-\d{4}-\d{2}-\d{6}(-\d{2})?$"
                if not re.match(patron_dam, numero_limpio):
                    errors["numero_despacho"] = (
                        "Formato inválido. Debe ser AAA-AAAA-RR-NNNNNN o AAA-AAAA-RR-NNNNNN-SS. "
                        "Ejemplo: 118-2025-10-012345 o 118-2025-10-012345-00"
                    )
                else:
                    # Guardar el número limpio
                    self.numero_despacho = numero_limpio

        # === Validación de Fecha de Revisión (obligatoria) ===
        if not self.fecha_revision:
            errors["fecha_revision"] = "La fecha de revisión es obligatoria"
        else:
            now = timezone.now()
            if self.fecha_revision > now:
                errors["fecha_revision"] = "La fecha de revisión no puede ser futura"

        # === Validaciones condicionales según Aprobado ===
        if self.aprobado:
            # Escenario A: Aprobado - requiere fecha_levante y documento
            if not self.fecha_levante:
                errors["fecha_levante"] = (
                    "Si está aprobado, debe especificar la fecha de levante"
                )
            if not self.documento_adjunto:
                errors["documento_adjunto"] = (
                    "Si está aprobado, debe adjuntar el documento legal de aprobación"
                )
        else:
            # Escenario B: No aprobado - requiere observaciones, limpia fecha_levante
            if not self.observaciones:
                errors["observaciones"] = (
                    "Si no está aprobado, debe especificar el motivo en las observaciones"
                )
            # Limpiar fecha de levante si no está aprobado
            self.fecha_levante = None

        # === Validaciones de Fecha de Levante ===
        if self.fecha_levante:
            now = timezone.now()

            # No puede ser futura
            if self.fecha_levante > now:
                errors["fecha_levante"] = "La fecha de levante no puede ser futura"

            # No puede ser anterior a la fecha de revisión
            if self.fecha_revision and self.fecha_levante < self.fecha_revision:
                errors["fecha_levante"] = (
                    "La fecha de levante no puede ser anterior a la fecha de revisión"
                )

            # No puede ser anterior a la fecha de llegada del buque (ETA o arribo real)
            if self.contenedor_id:
                try:
                    contenedor = Contenedor.objects.select_related("arribo__buque").get(
                        pk=self.contenedor_id
                    )
                    if contenedor.arribo:
                        # Usar fecha_arribo_real si existe, sino fecha_eta
                        fecha_llegada_buque = (
                            contenedor.arribo.fecha_arribo_real
                            or contenedor.arribo.fecha_eta
                        )
                        if (
                            fecha_llegada_buque
                            and self.fecha_levante < fecha_llegada_buque
                        ):
                            errors["fecha_levante"] = (
                                f"La fecha de levante no puede ser anterior a la "
                                f"llegada del buque ({fecha_llegada_buque.strftime('%d/%m/%Y %H:%M')})"
                            )
                except Contenedor.DoesNotExist:
                    pass

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        estado = "Aprobado" if self.aprobado else "Pendiente"
        return f"{self.contenedor.codigo_iso} - {estado}"


# ====== CUN05: REGISTRO FACTURAS AL CLIENTE (1-1 opcional) ======
class AprobacionFinanciera(models.Model):
    """Registro de facturas emitidas al cliente por contenedor"""

    ESTADO_FINANCIERO_CHOICES = [
        ("PENDIENTE", "🟡 Emitida / Pendiente"),
        ("PAGADA", "🟢 Pagada"),
        ("CREDITO", "🔵 Crédito Aprobado"),
        ("ANULADA", "🔴 Anulada"),
    ]

    # Servicios tarifados predefinidos
    SERVICIOS_DISPONIBLES = [
        ("USO_MUELLE", "Uso de Muelle"),
        ("ENERGIA_REEFER", "Energía Reefer"),
        ("ALMACENAJE", "Almacenaje"),
        ("PESAJE", "Pesaje"),
        ("TRACCION", "Tracción"),
        ("MANIPULEO", "Manipuleo"),
        ("CONSOLIDACION", "Consolidación/Desconsolidación"),
        ("INSPECCION", "Inspección"),
        ("DOCUMENTACION", "Documentación"),
        ("SEGURO", "Seguro de Carga"),
        ("CUSTODIA", "Custodia"),
        ("LAVADO", "Lavado de Contenedor"),
        ("REPARACION", "Reparación"),
        ("FUMIGACION", "Fumigación"),
        ("OTROS", "Otros Servicios"),
    ]

    contenedor = models.OneToOneField(
        Contenedor,
        on_delete=models.PROTECT,
        related_name="aprobacion_financiera",
        verbose_name="Contenedor",
    )
    numero_factura = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Número de Factura",
        help_text="Formato factura electrónica: F001-12345678 o B001-12345678",
    )
    monto_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto (USD)",
        help_text="Monto total en dólares americanos (mínimo 0)",
    )
    servicios_facturados = models.JSONField(
        default=list,
        verbose_name="Servicios Facturados",
        help_text="Seleccione los servicios incluidos en la factura",
    )
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión")
    fecha_vencimiento = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Vencimiento"
    )
    fecha_pago = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Pago",
        help_text="Solo disponible cuando el estado es 'Pagada'",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    estado_financiero = models.CharField(
        max_length=20,
        choices=ESTADO_FINANCIERO_CHOICES,
        default="PENDIENTE",
        verbose_name="Estado Financiero",
        help_text="🟡 Pendiente bloquea Gate Pass | 🟢 Pagada y 🔵 Crédito liberan Gate Pass",
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
        import re

        errors = {}

        # === Validación del Número de Factura (formato electrónico) ===
        if self.numero_factura:
            numero_limpio = self.numero_factura.strip().upper()
            # Patrón: F001-12345678 o B001-12345678 (Factura o Boleta)
            patron_factura = r"^[FB]\d{3}-\d{8}$"
            if not re.match(patron_factura, numero_limpio):
                errors["numero_factura"] = (
                    "Formato inválido. Debe ser F001-12345678 o B001-12345678. "
                    "F=Factura, B=Boleta, seguido de serie (3 dígitos) y correlativo (8 dígitos)"
                )
            else:
                self.numero_factura = numero_limpio

        # === Validación del Monto (>= 0) ===
        if self.monto_usd is not None and self.monto_usd < 0:
            errors["monto_usd"] = "El monto no puede ser negativo"

        # === Validación Fecha Vencimiento >= Fecha Emisión ===
        if self.fecha_vencimiento and self.fecha_emision:
            if self.fecha_vencimiento < self.fecha_emision:
                errors["fecha_vencimiento"] = (
                    "La fecha de vencimiento no puede ser anterior a la fecha de emisión"
                )

        # === Validación condicional de Fecha de Pago ===
        if self.estado_financiero == "PAGADA":
            if not self.fecha_pago:
                errors["fecha_pago"] = (
                    "Debe especificar la fecha de pago cuando el estado es 'Pagada'"
                )
            # Documento adjunto obligatorio cuando está pagada
            if not self.documento_adjunto:
                errors["documento_adjunto"] = (
                    "Debe adjuntar la factura como comprobante de pago"
                )
        else:
            # Limpiar fecha de pago si no está pagada
            self.fecha_pago = None

        # === Validar que servicios_facturados sea una lista ===
        if self.servicios_facturados:
            if not isinstance(self.servicios_facturados, list):
                errors["servicios_facturados"] = "Debe seleccionar al menos un servicio"
            elif len(self.servicios_facturados) == 0:
                errors["servicios_facturados"] = "Debe seleccionar al menos un servicio"

        if errors:
            raise ValidationError(errors)

    @property
    def esta_vencida(self):
        """Verifica si la factura está vencida"""
        from django.utils import timezone

        if not self.fecha_vencimiento or self.fecha_pago:
            return False
        return timezone.now().date() > self.fecha_vencimiento

    @property
    def permite_gate_pass(self):
        """Indica si el estado financiero permite liberar el Gate Pass"""
        return self.estado_financiero in ["PAGADA", "CREDITO"]

    def get_servicios_display(self):
        """Retorna los servicios facturados como texto legible"""
        if not self.servicios_facturados:
            return "-"
        servicios_dict = dict(self.SERVICIOS_DISPONIBLES)
        nombres = [servicios_dict.get(s, s) for s in self.servicios_facturados]
        return ", ".join(nombres)

    def __str__(self):
        estado_dict = dict(self.ESTADO_FINANCIERO_CHOICES)
        estado = estado_dict.get(self.estado_financiero, self.estado_financiero)
        return f"Factura {self.numero_factura} - {estado}"


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
        help_text="Se auto-completa desde el contenedor seleccionado",
    )
    # Siempre True - si se registra un pago, es porque se realizó
    pago_realizado = models.BooleanField(
        default=True, verbose_name="Pago Realizado", editable=False
    )
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
        # Auto-asignar transitario desde el contenedor si no está asignado
        if self.contenedor_id and not self.transitario_id:
            try:
                contenedor = Contenedor.objects.select_related("transitario").get(
                    pk=self.contenedor_id
                )
                if contenedor.transitario_id:
                    self.transitario_id = contenedor.transitario_id
            except Contenedor.DoesNotExist:
                pass

        # Validar que el transitario coincida con el del contenedor (usando _id para evitar query)
        if self.contenedor_id and self.transitario_id:
            try:
                contenedor = Contenedor.objects.get(pk=self.contenedor_id)
                if (
                    contenedor.transitario_id
                    and contenedor.transitario_id != self.transitario_id
                ):
                    raise ValidationError(
                        {
                            "transitario": "El transitario debe ser el asignado al contenedor"
                        }
                    )
            except Contenedor.DoesNotExist:
                pass

        # Validaciones de pago (siempre requeridos ya que siempre es pago realizado)
        if not self.fecha_pago:
            raise ValidationError({"fecha_pago": "Debe especificar la fecha de pago"})
        if not self.monto_pagado:
            raise ValidationError({"monto_pagado": "Debe especificar el monto pagado"})
        # Documento adjunto obligatorio como comprobante de pago
        if not self.documento_adjunto:
            raise ValidationError(
                {"documento_adjunto": "Debe adjuntar el comprobante de pago"}
            )

    def __str__(self):
        estado = "Pagado" if self.pago_realizado else "Pendiente"
        codigo = self.contenedor.codigo_iso if self.contenedor_id else "Sin contenedor"
        transitario_nombre = (
            self.transitario.razon_social if self.transitario_id else "Sin transitario"
        )
        return f"{codigo} - {transitario_nombre} - {estado}"


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
