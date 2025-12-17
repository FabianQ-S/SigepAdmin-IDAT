# SigepAdmin - Sistema de Gestión Portuaria
## Plan de Pruebas Unitarias

> **Nota:** Este documento contiene los casos de prueba unitarias implementados para el proyecto SigepAdmin.
> Las pruebas se ejecutan con el framework nativo de Django (`django.test`).
> - **Comando de ejecución:** `python manage.py test control.tests`
> - **Total de tests:** 37 | **Exitosos:** 37 | **Fallidos:** 0

---

## Índice de Casos de Prueba

| Número del Caso de Prueba | Componente | Descripción de lo que se Probará | Prerrequisitos |
| :--- | :--- | :--- | :--- |
| CP-001 | `validate_iso_6346` | Validación de código ISO 6346 de contenedor | Ninguno |
| CP-002 | `Buque` | Creación y validación de modelo Buque | Base de datos limpia |
| CP-003 | `Arribo` | Validación de fechas ETA/ETD en arribos | Buque existente |
| CP-004 | `validate_sellos_format` | Validación de formato de sellos | Ninguno |
| CP-009 | `EventoContenedor` | Flujo de eventos y tracking de contenedor | Contenedor existente |
| CP-010 | `Transitario` | CRUD de transitarios | Ninguno |
| CP-011 | `AprobacionFinanciera` | Ciclo de vida de facturas | Contenedor existente |
| CP-012 | `AprobacionPagoTransitario` | Validación de pagos de transitario | Contenedor con transitario |

---

## CP-001: Validación ISO 6346 en Código de Contenedor

**Archivo:** `control/tests/test_validators.py`

### Prueba 1: Código válido MSKU

**Código de la prueba:**
```python
def test_codigo_valido_msku(self):
    """Código ISO válido con dígito verificador correcto"""
    try:
        validate_iso_6346("MSKU9070323")
    except ValidationError:
        self.fail("validate_iso_6346 lanzó ValidationError para código válido")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Código válido MSKU | `test_codigo_valido_msku` | `MSKU9070323` | Sin excepción | ✅ | Happy Path |

---

### Prueba 2: Dígito verificador incorrecto

**Código de la prueba:**
```python
def test_codigo_digito_incorrecto(self):
    """Error: Dígito verificador incorrecto"""
    with self.assertRaises(ValidationError):
        validate_iso_6346("MSKU9070322")  # Dígito correcto es 3, no 2
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | Dígito verificador incorrecto | `test_codigo_digito_incorrecto` | `MSKU9070322` | `ValidationError` | ✅ | Error Path |

---

### Prueba 3: Código muy corto

**Código de la prueba:**
```python
def test_codigo_formato_invalido_corto(self):
    """Error: Código muy corto"""
    with self.assertRaises(ValidationError):
        validate_iso_6346("MSK907")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **3** | Código muy corto | `test_codigo_formato_invalido_corto` | `MSK907` | `ValidationError` | ✅ | Error Path |

---

### Prueba 4: Formato completamente inválido

**Código de la prueba:**
```python
def test_codigo_formato_invalido_letras(self):
    """Error: Formato completamente inválido"""
    with self.assertRaises(ValidationError):
        validate_iso_6346("INVALIDO")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **4** | Formato completamente inválido | `test_codigo_formato_invalido_letras` | `INVALIDO` | `ValidationError` | ✅ | Error Path |

---

### Prueba 5: Código vacío

**Código de la prueba:**
```python
def test_codigo_vacio(self):
    """Error: Código vacío"""
    with self.assertRaises(ValidationError):
        validate_iso_6346("")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **5** | Código vacío | `test_codigo_vacio` | `""` | `ValidationError` | ✅ | Error Path |

---

## CP-004: Formato de sellos de contenedor

**Archivo:** `control/tests/test_validators.py`

### Prueba 1: Sello simple válido

**Código de la prueba:**
```python
def test_sello_simple_valido(self):
    """Sello simple con marcador principal"""
    try:
        validate_sellos_format("NAVIERA:HL123456*")
    except ValidationError:
        self.fail("validate_sellos_format lanzó ValidationError para formato válido")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Sello simple válido | `test_sello_simple_valido` | `NAVIERA:HL123456*` | Sin excepción | ✅ | Happy Path |

---

### Prueba 2: Sellos múltiples válidos

**Código de la prueba:**
```python
def test_sellos_multiples_validos(self):
    """Múltiples sellos separados por pipe"""
    try:
        validate_sellos_format("NAVIERA:HL123*|ADUANAS:AD456")
    except ValidationError:
        self.fail("validate_sellos_format lanzó ValidationError para formato válido")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | Sellos múltiples válidos | `test_sellos_multiples_validos` | `NAVIERA:HL123*\|ADUANAS:AD456` | Sin excepción | ✅ | Happy Path |

---

### Prueba 3: Formato sin tipo:codigo

**Código de la prueba:**
```python
def test_sello_formato_invalido(self):
    """Error: Formato sin tipo:codigo"""
    with self.assertRaises(ValidationError):
        validate_sellos_format("FORMATO_INCORRECTO")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **3** | Formato sin tipo:codigo | `test_sello_formato_invalido` | `FORMATO_INCORRECTO` | `ValidationError` | ✅ | Error Path |

---

### Prueba 4: Tipo de sello vacío

**Código de la prueba:**
```python
def test_sello_tipo_vacio(self):
    """Error: Tipo de sello vacío"""
    with self.assertRaises(ValidationError):
        validate_sellos_format(":CODIGO123*")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **4** | Tipo de sello vacío | `test_sello_tipo_vacio` | `:CODIGO123*` | `ValidationError` | ✅ | Error Path |

---

## CP-002: Creación de Buque con IMO válido

**Archivo:** `control/tests/test_models.py`

### Prueba 1: Crear buque válido

**Código de la prueba:**
```python
def test_crear_buque_valido(self):
    """Crear buque con todos los campos válidos"""
    buque = Buque(
        nombre="MSC Gülsün",
        imo_number="9839430",
        naviera="MSC",
        pabellon_bandera="PA",
        puerto_registro="Panama City",
        callsign="3FZV9",
        eslora_metros=Decimal("400.00"),
        manga_metros=Decimal("61.00"),
        calado_metros=Decimal("16.50"),
        teu_capacidad=23756
    )
    buque.full_clean()
    buque.save()
    
    self.assertIsNotNone(buque.pk)
    self.assertEqual(Buque.objects.count(), 1)
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Crear buque válido | `test_crear_buque_valido` | Datos completos (nombre, IMO, naviera...) | Buque con `pk` asignado | ✅ | Happy Path |

---

### Prueba 2: Buque sin nombre falla

**Código de la prueba:**
```python
def test_buque_sin_nombre_falla(self):
    """Error: Campo nombre obligatorio vacío"""
    buque = Buque(
        nombre="",
        imo_number="9839431",
        naviera="MSC",
        pabellon_bandera="PA",
        puerto_registro="Panama City",
        callsign="3FZV8",
        eslora_metros=Decimal("400.00"),
        manga_metros=Decimal("61.00"),
        calado_metros=Decimal("16.50"),
        teu_capacidad=23756
    )
    with self.assertRaises(ValidationError):
        buque.full_clean()
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | Buque sin nombre falla | `test_buque_sin_nombre_falla` | `nombre=""` | `ValidationError` | ✅ | Error Path |

---

### Prueba 3: IMO duplicado falla

**Código de la prueba:**
```python
def test_buque_imo_duplicado_falla(self):
    """Error: IMO debe ser único"""
    Buque.objects.create(
        nombre="Buque 1",
        imo_number="9839430",
        naviera="MSC",
        pabellon_bandera="PA",
        puerto_registro="Panama City",
        callsign="3FZV9",
        eslora_metros=Decimal("400.00"),
        manga_metros=Decimal("61.00"),
        calado_metros=Decimal("16.50"),
        teu_capacidad=23756
    )
    with self.assertRaises(IntegrityError):
        Buque.objects.create(
            nombre="Buque 2",
            imo_number="9839430",  # IMO duplicado
            naviera="MSC",
            pabellon_bandera="PA",
            puerto_registro="Panama City",
            callsign="3FZV7",
            eslora_metros=Decimal("400.00"),
            manga_metros=Decimal("61.00"),
            calado_metros=Decimal("16.50"),
            teu_capacidad=23756
        )
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **3** | IMO duplicado falla | `test_buque_imo_duplicado_falla` | IMO existente | `IntegrityError` | ✅ | Error Path |

---

## CP-003: Validación de fechas en Arribo

**Archivo:** `control/tests/test_models.py`

### Prueba 1: Fechas válidas (ETA < ETD)

**Código de la prueba:**
```python
def test_arribo_fechas_validas(self):
    """ETA antes de ETD es válido"""
    ahora = timezone.now()
    arribo = Arribo(
        buque=self.buque,
        tipo_operacion="DESCARGA",
        fecha_eta=ahora + timedelta(days=5),
        fecha_etd=ahora + timedelta(days=10),
        muelle_berth="MUELLE-A",
        servicios_contratados="Descarga",
        contenedores_descarga=10
    )
    arribo.full_clean()
    arribo.save()
    self.assertIsNotNone(arribo.pk)
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Fechas válidas (ETA < ETD) | `test_arribo_fechas_validas` | ETA: +5 días, ETD: +10 días | Arribo guardado | ✅ | Happy Path |

---

### Prueba 2: ETA posterior a ETD

**Código de la prueba:**
```python
def test_eta_posterior_a_etd_invalido(self):
    """Error: ETA no puede ser posterior a ETD"""
    ahora = timezone.now()
    arribo = Arribo(
        buque=self.buque,
        tipo_operacion="DESCARGA",
        fecha_eta=ahora + timedelta(days=10),
        fecha_etd=ahora + timedelta(days=5),  # ETD antes de ETA
        muelle_berth="MUELLE-A",
        servicios_contratados="Descarga",
        contenedores_descarga=10
    )
    with self.assertRaises(ValidationError):
        arribo.full_clean()
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | ETA posterior a ETD | `test_eta_posterior_a_etd_invalido` | ETA: +10 días, ETD: +5 días | `ValidationError` | ✅ | Error Path |

---

## CP-009: Flujo de eventos de contenedor (Importación)

**Archivo:** `control/tests/test_events.py`

### Prueba 1: Secuencia válida

**Código de la prueba:**
```python
def test_secuencia_importacion_valida(self):
    """Secuencia correcta: DISCHARGED → GATE_OUT_FULL"""
    evento1 = EventoContenedor.objects.create(
        contenedor=self.contenedor,
        tipo_evento="DISCHARGED",
        fecha_hora=timezone.now(),
        ubicacion_puerto="Terminal DP World Callao",
        ubicacion_pais="PE"
    )
    self.assertIsNotNone(evento1.pk)
    
    evento2 = EventoContenedor.objects.create(
        contenedor=self.contenedor,
        tipo_evento="GATE_OUT_FULL",
        fecha_hora=timezone.now(),
        ubicacion_puerto="Gate 3",
        ubicacion_pais="PE"
    )
    self.assertIsNotNone(evento2.pk)
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Secuencia válida | `test_secuencia_importacion_valida` | DISCHARGED → GATE_OUT_FULL | Eventos creados | ✅ | Happy Path |

---

### Prueba 2: Último evento correcto (RF05)

**Código de la prueba:**
```python
def test_ultimo_evento_contenedor(self):
    """RF05: Contenedor muestra su evento actual"""
    EventoContenedor.objects.create(
        contenedor=self.contenedor,
        tipo_evento="DISCHARGED",
        fecha_hora=timezone.now(),
        ubicacion_puerto="Terminal DP World Callao",
        ubicacion_pais="PE"
    )
    EventoContenedor.objects.create(
        contenedor=self.contenedor,
        tipo_evento="GATE_OUT_FULL",
        fecha_hora=timezone.now(),
        ubicacion_puerto="Gate 3",
        ubicacion_pais="PE"
    )
    
    ultimo = self.contenedor.ultimo_evento
    self.assertEqual(ultimo.tipo_evento, "GATE_OUT_FULL")
    self.assertIn("Gate Out", self.contenedor.ultimo_estado)
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | Último evento correcto | `test_ultimo_evento_contenedor` | 2 eventos creados | `ultimo_evento.tipo_evento == GATE_OUT_FULL` | ✅ | Happy Path - RF05 |

---

### Prueba 3: Tipo evento inválido

**Código de la prueba:**
```python
def test_evento_tipo_invalido_falla(self):
    """Error: Tipo de evento no válido"""
    evento = EventoContenedor(
        contenedor=self.contenedor,
        tipo_evento="TIPO_INEXISTENTE",
        fecha_hora=timezone.now(),
        ubicacion_puerto="Test",
        ubicacion_pais="PE"
    )
    with self.assertRaises(ValidationError):
        evento.full_clean()
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **3** | Tipo evento inválido | `test_evento_tipo_invalido_falla` | `tipo_evento="TIPO_INEXISTENTE"` | `ValidationError` | ✅ | Error Path |

---

## CP-010: Gestión de Transitario

**Archivo:** `control/tests/test_models.py`

### Prueba 1: Crear transitario válido

**Código de la prueba:**
```python
def test_crear_transitario(self):
    """Crear transitario con datos válidos"""
    transitario = Transitario.objects.create(
        razon_social="Logistics Peru SAC",
        identificador_tributario="20512345678",
        direccion="Av. Argentina 3458, Lima",
        tipo_servicio="NVOCC",
        email_contacto="contacto@logistics.pe"
    )
    self.assertIsNotNone(transitario.pk)
    self.assertEqual(transitario.estado_operacion, "ACTIVO")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Crear transitario válido | `test_crear_transitario` | Datos completos | Transitario con `estado_operacion="ACTIVO"` | ✅ | Happy Path |

---

### Prueba 2: Actualizar transitario

**Código de la prueba:**
```python
def test_actualizar_transitario(self):
    """Actualizar estado de transitario"""
    transitario = Transitario.objects.create(
        razon_social="Test SAC",
        identificador_tributario="20512345679",
        direccion="Test Address",
        tipo_servicio="FFWD"
    )
    transitario.estado_operacion = "SUSPENDIDO"
    transitario.save()
    
    transitario.refresh_from_db()
    self.assertEqual(transitario.estado_operacion, "SUSPENDIDO")
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | Actualizar transitario | `test_actualizar_transitario` | `estado_operacion="SUSPENDIDO"` | Estado actualizado | ✅ | Happy Path |

---

### Prueba 3: Sin razón social falla

**Código de la prueba:**
```python
def test_transitario_sin_razon_social_falla(self):
    """Error: Razón social obligatoria"""
    transitario = Transitario(
        razon_social="",
        identificador_tributario="20512345680",
        direccion="Test Address",
        tipo_servicio="NVOCC"
    )
    with self.assertRaises(ValidationError):
        transitario.full_clean()
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **3** | Sin razón social falla | `test_transitario_sin_razon_social_falla` | `razon_social=""` | `ValidationError` | ✅ | Error Path |

---

## CP-011: Facturación y Estados de Pago

**Archivo:** `control/tests/test_models.py`

### Prueba 1: Factura pendiente no permite gate pass

**Código de la prueba:**
```python
def test_factura_pendiente_no_permite_gate_pass(self):
    """Factura pendiente no permite Gate Pass"""
    factura = AprobacionFinanciera.objects.create(
        contenedor=self.contenedor,
        numero_factura="F001-00001234",
        fecha_emision=timezone.now().date(),
        monto_usd=Decimal("1500.00"),
        estado_financiero="PENDIENTE"
    )
    # permite_gate_pass es propiedad, no método
    self.assertFalse(factura.permite_gate_pass)
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Factura pendiente no permite gate pass | `test_factura_pendiente_no_permite_gate_pass` | `estado_financiero="PENDIENTE"` | `permite_gate_pass == False` | ✅ | Happy Path |

---

### Prueba 2: Factura pagada permite gate pass

**Código de la prueba:**
```python
def test_factura_pagada_permite_gate_pass(self):
    """Factura pagada permite Gate Pass"""
    factura = AprobacionFinanciera.objects.create(
        contenedor=self.contenedor,
        numero_factura="F001-00001235",
        fecha_emision=timezone.now().date(),
        monto_usd=Decimal("1500.00"),
        estado_financiero="PAGADA",
        fecha_pago=timezone.now().date()
    )
    # permite_gate_pass es propiedad, no método
    self.assertTrue(factura.permite_gate_pass)
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | Factura pagada permite gate pass | `test_factura_pagada_permite_gate_pass` | `estado_financiero="PAGADA"` | `permite_gate_pass == True` | ✅ | Happy Path |

---

## CP-012: Pago Transitario al Puerto

**Archivo:** `control/tests/test_models.py`

### Prueba 1: Contenedor sin pago

**Código de la prueba:**
```python
def test_transitario_ha_pagado_sin_registro(self):
    """Contenedor sin registro de pago retorna False"""
    # transitario_ha_pagado es propiedad, no método
    self.assertFalse(self.contenedor.transitario_ha_pagado)
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | Contenedor sin pago | `test_transitario_ha_pagado_sin_registro` | Sin registro de pago | `transitario_ha_pagado == False` | ✅ | Happy Path |

---

### Prueba 2: Pago sin fecha falla

**Código de la prueba:**
```python
def test_pago_sin_fecha_falla(self):
    """Error: Fecha de pago obligatoria"""
    pago = AprobacionPagoTransitario(
        contenedor=self.contenedor,
        transitario=self.transitario,
        monto_pagado=Decimal("500.00"),
        fecha_pago=None  # Sin fecha
    )
    with self.assertRaises(ValidationError):
        pago.full_clean()
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **2** | Pago sin fecha falla | `test_pago_sin_fecha_falla` | `fecha_pago=None` | `ValidationError` | ✅ | Error Path |

---

### Prueba 3: Pago sin monto falla

**Código de la prueba:**
```python
def test_pago_sin_monto_falla(self):
    """Error: Monto pagado obligatorio"""
    pago = AprobacionPagoTransitario(
        contenedor=self.contenedor,
        transitario=self.transitario,
        monto_pagado=None,  # Sin monto
        fecha_pago=timezone.now().date()
    )
    with self.assertRaises(ValidationError):
        pago.full_clean()
```

| Nº | Descripción | Método | Datos Entrada | Salida Esperada | ¿OK? | Observaciones |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **3** | Pago sin monto falla | `test_pago_sin_monto_falla` | `monto_pagado=None` | `ValidationError` | ✅ | Error Path |

---

*Documento generado automáticamente desde la ejecución de pruebas del 13/12/2024*