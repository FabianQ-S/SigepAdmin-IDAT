# 📋 FICHA DE DISEÑO DE TESTING - SigepAdmin

Sistema de Gestión Portuaria desarrollado con Django 5.2.7

---

## 1. INTRODUCCIÓN AL TESTING CON `django.test`

### ¿Qué es `django.test`?

`django.test` es el framework nativo de Django para pruebas unitarias y de integración. Está construido sobre `unittest` de Python y añade funcionalidades específicas:

```python
from django.test import TestCase, Client

class MiTest(TestCase):
    def setUp(self):
        # Preparación antes de cada test
        pass

    def test_ejemplo(self):
        # Lógica del test
        self.assertEqual(1, 1)
```

### Clases principales disponibles

| Clase | Descripción | Uso recomendado |
|-------|-------------|-----------------|
| `TestCase` | Base transaccional con rollback automático | Tests de modelos y vistas |
| `TransactionTestCase` | Permite commit real | Tests con transacciones complejas |
| `SimpleTestCase` | Sin soporte de base de datos | Tests de utilidades/validaciones puras |
| `LiveServerTestCase` | Servidor de pruebas real | Tests end-to-end con Selenium |
| `Client` | Cliente HTTP simulado | Tests de vistas y APIs |

### Comando de ejecución

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una app específica
python manage.py test control

# Ejecutar un test específico
python manage.py test control.tests.TestBuqueModel

# Con verbosidad
python manage.py test --verbosity=2
```

---

## 2. LISTA DE REQUERIMIENTOS FUNCIONALES

| NUM REQ FUNC | DESCRIPCIÓN | MÓDULO RELACIONADO |
|:---:|:---|:---|
| RF01 | Gestión de roles y permisos: Deberá permitir tener diferentes tipos de Usuarios para la app como administradores, encargados del almacén, Transportista, logística, entre otros relacionados. | Django Auth / Groups |
| RF02 | Gestionar Usuarios: Permitir la gestión de los trabajadores de forma compleja permitiendo la eliminación, desactivación y asignación de roles para cada uno, de forma explícita. | Django Auth / Admin |
| RF03 | Generación de reportes: El sistema debe poder generar reportes personalizados según el tipo de dato que se quiera demostrar, sea en formato PDF. | `views.py` (WeasyPrint) |
| RF04 | Gestionar fechas de atraques: El sistema debe permitir la gestión de las fechas de arribo. | `Arribo` model |
| RF05 | Gestionar Contenedores: El sistema debe permitir la gestión, ubicación y su evento actual. | `Contenedor`, `EventoContenedor` |
| RF06 | Gestionar cargueros: Sistema que permita la gestión completa de las naves que distribuyen el puerto. | `Buque` model |
| RF07 | Generación de Facturas: Permitiendo la emisión manual y anulación de facturas. | `AprobacionFinanciera` |
| RF08 | Administración de pagos: Permitiendo actualizar el estado del pago por cada contenedor. | `AprobacionFinanciera` |
| RF09 | Vista de datos pública: Permite a los clientes revisar el estado de su contenedor a través de una página pública. | `views.index`, `views.detalle_contenedor` |
| RF10 | Permitirá a los clientes realizar quejas a través del portal del cliente de forma eficiente por correo. | `Queja`, `views.quejas_sugerencias` |
| RF11 | Gestión y administración de transitarios del puerto. | `Transitario` model |
| RF12 | Registro y administración de pagos de los transitarios del puerto. | `AprobacionPagoTransitario` |
| RF13 | Transitario: El área logística se encarga del registro y administración de los transitarios asignados a cada lote de contenedores. | `Transitario`, `Contenedor` |
| RF14 | Pago transitario: El área financiera se encarga del registro de los pagos de parte de los transitarios al puerto. | `AprobacionPagoTransitario` |

---

## 3. LISTA DE CASOS DE USO

| NUM CASO USO | DESCRIPCIÓN | MODELO/VISTA ASOCIADO |
|:---:|:---|:---|
| CU01 | Gestionar Arribo | `Arribo`, `ArriboAdmin` |
| CU02 | Gestionar Buques | `Buque`, `BuqueAdmin` |
| CU03 | Gestionar Contenedores | `Contenedor`, `ContenedorAdmin` |
| CU04 | Gestionar Permisos Aduaneros | `AprobacionAduanera`, `AprobacionAduaneraAdmin` |
| CU05 | Gestionar Registro Facturas | `AprobacionFinanciera`, `AprobacionFinancieraAdmin` |
| CU06 | Consultar Contenedor (Cliente) | `views.buscar_contenedor`, `views.detalle_contenedor` |
| CU07 | Registrar Queja (Cliente) | `views.quejas_sugerencias` |
| CU08 | Gestionar Quejas (Admin) | `Queja`, `QuejaAdmin` |
| CU09 | Gestionar Empleados | Django Auth `User` |
| CU10 | Gestionar Permisos y Roles | Django Auth `Group`, `Permission` |
| CU11 | Gestionar Transitarios | `Transitario`, `TransitarioAdmin` |
| CU12 | Gestionar Pagos Transitarios | `AprobacionPagoTransitario` |
| CU13 | Gestionar Evento Contenedor | `EventoContenedor`, `EventoContenedorAdmin` |

---

## 4. MATRIZ DE TRAZABILIDAD: Requerimientos vs Casos de Uso

|  | RF01 | RF02 | RF03 | RF04 | RF05 | RF06 | RF07 | RF08 | RF09 | RF10 | RF11 | RF12 | RF13 | RF14 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CU01** |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |
| **CU02** |  |  |  |  |  | ✓ |  |  |  |  |  |  |  |  |
| **CU03** |  |  |  |  | ✓ |  |  |  |  |  |  |  | ✓ |  |
| **CU04** |  |  |  |  | ✓ |  |  |  |  |  |  |  |  |  |
| **CU05** |  |  | ✓ |  |  |  | ✓ | ✓ |  |  |  |  |  |  |
| **CU06** |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |  |
| **CU07** |  |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |
| **CU08** | ✓ |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |
| **CU09** | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |  |  |
| **CU10** | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |  |  |
| **CU11** |  |  |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  |
| **CU12** |  |  |  |  |  |  |  |  |  |  |  | ✓ |  | ✓ |
| **CU13** |  |  |  |  | ✓ |  |  |  |  |  |  |  |  |  |

---

## 5. FICHAS DE CASOS DE PRUEBA DETALLADAS

---

### 📋 CP-001: Validación ISO 6346 en Código de Contenedor

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Validar formato ISO 6346 en código de contenedor |
| **CASO DE USO RELACIONADO** | CU03 - Gestionar Contenedores |
| **REQUERIMIENTO FUNCIONAL** | RF05 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar que los códigos de contenedor cumplan con el estándar ISO 6346 incluyendo dígito verificador correcto. |
| **PRERREQUISITOS** | Ninguno (test unitario puro) |
| **DATOS DE ENTRADA** | `MSKU9070323` (válido), `XXXX1234567` (inválido), `MSKU9070322` (dígito incorrecto) |
| **PASOS** | 1. Invocar `validate_iso_6346(codigo)`<br>2. Verificar si lanza `ValidationError` |
| **RESULTADO ESPERADO** | Códigos válidos no lanzan excepción. Códigos inválidos lanzan `ValidationError` |
| **MÉTODO DJANGO** | `assertRaises(ValidationError, validate_iso_6346, codigo_invalido)` |

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from control.models import validate_iso_6346

class TestValidacionISO6346(TestCase):
    def test_codigo_valido(self):
        # No debe lanzar excepción
        validate_iso_6346("MSKU9070323")
    
    def test_codigo_digito_incorrecto(self):
        with self.assertRaises(ValidationError):
            validate_iso_6346("MSKU9070322")
    
    def test_codigo_formato_invalido(self):
        with self.assertRaises(ValidationError):
            validate_iso_6346("INVAL1D")
```

---

### 📋 CP-002: Creación de Buque con IMO válido

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Crear y persistir un buque correctamente |
| **CASO DE USO RELACIONADO** | CU02 - Gestionar Buques |
| **REQUERIMIENTO FUNCIONAL** | RF06 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar que se pueda crear un buque con todos sus campos obligatorios de forma correcta. |
| **PRERREQUISITOS** | Base de datos limpia de pruebas |
| **DATOS DE ENTRADA** | Nombre: "MSC Gülsün", IMO: "9839430", Naviera: "MSC", Eslora: 400.00, Manga: 61.00, Calado: 16.50, TEU: 23756 |
| **PASOS** | 1. Crear instancia de `Buque` con datos válidos<br>2. Ejecutar `full_clean()`<br>3. Guardar con `save()` |
| **RESULTADO ESPERADO** | Buque creado y persistido con pk asignado |
| **MÉTODO DJANGO** | `assertEqual`, `assertIsNotNone` |

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from control.models import Buque

class TestBuqueModel(TestCase):
    # ===== HAPPY PATH =====
    def test_crear_buque_valido(self):
        buque = Buque(
            nombre="MSC Gülsün",
            imo_number="9839430",
            naviera="MSC",
            pabellon_bandera="PA",
            eslora_metros=400.00,
            manga_metros=61.00,
            calado_metros=16.50,
            teu_capacidad=23756
        )
        buque.full_clean()
        buque.save()
        
        self.assertIsNotNone(buque.pk)
        self.assertEqual(Buque.objects.count(), 1)
    
    # ===== ERROR PATH =====
    def test_buque_sin_nombre_falla(self):
        """Error: Campo obligatorio faltante"""
        buque = Buque(
            nombre="",  # Campo vacío
            imo_number="9839431",
            naviera="MSC",
            pabellon_bandera="PA",
            eslora_metros=400.00,
            manga_metros=61.00,
            calado_metros=16.50,
            teu_capacidad=23756
        )
        with self.assertRaises(ValidationError):
            buque.full_clean()
    
    def test_buque_imo_duplicado_falla(self):
        """Error: IMO debe ser único"""
        Buque.objects.create(
            nombre="Buque 1",
            imo_number="9839430",
            naviera="MSC",
            pabellon_bandera="PA",
            eslora_metros=400.00,
            manga_metros=61.00,
            calado_metros=16.50,
            teu_capacidad=23756
        )
        with self.assertRaises(IntegrityError):
            Buque.objects.create(
                nombre="Buque 2",
                imo_number="9839430",  # IMO duplicado
                naviera="MSC",
                pabellon_bandera="PA",
                eslora_metros=400.00,
                manga_metros=61.00,
                calado_metros=16.50,
                teu_capacidad=23756
            )
```

---

### 📋 CP-003: Validación de fechas en Arribo

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | ETA debe ser anterior a ETD |
| **CASO DE USO RELACIONADO** | CU01 - Gestionar Arribo |
| **REQUERIMIENTO FUNCIONAL** | RF04 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar que el sistema rechace un arribo donde la fecha ETA sea posterior a la fecha ETD. |
| **PRERREQUISITOS** | Buque existente en la base de datos |
| **DATOS DE ENTRADA** | ETA: 2025-12-15, ETD: 2025-12-10 (inválido) |
| **PASOS** | 1. Crear buque válido<br>2. Crear arribo con ETA > ETD<br>3. Ejecutar `full_clean()` |
| **RESULTADO ESPERADO** | Se lanza `ValidationError` indicando inconsistencia de fechas |
| **MÉTODO DJANGO** | `assertRaises(ValidationError)` |

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from control.models import Buque, Arribo

class TestArriboValidations(TestCase):
    def setUp(self):
        self.buque = Buque.objects.create(
            nombre="Test Ship",
            imo_number="1234567",
            naviera="Test Line",
            pabellon_bandera="PA",
            eslora_metros=200.00,
            manga_metros=30.00,
            calado_metros=10.00,
            teu_capacidad=5000
        )
    
    def test_eta_posterior_a_etd_invalido(self):
        ahora = timezone.now()
        arribo = Arribo(
            buque=self.buque,
            tipo_operacion="DESCARGA",
            fecha_eta=ahora + timedelta(days=10),
            fecha_etd=ahora + timedelta(days=5),  # ETD antes de ETA
            muelle="MUELLE-A"
        )
        with self.assertRaises(ValidationError):
            arribo.full_clean()
```

---

### 📋 CP-004: Formato de sellos de contenedor

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Validar formato de múltiples sellos |
| **CASO DE USO RELACIONADO** | CU03 - Gestionar Contenedores |
| **REQUERIMIENTO FUNCIONAL** | RF05 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar que el formato de sellos múltiples `TIPO:CODIGO*|TIPO:CODIGO` se valide correctamente. |
| **PRERREQUISITOS** | Ninguno |
| **DATOS DE ENTRADA** | Válido: `NAVIERA:HL123456*`, `NAVIERA:HL123*|ADUANAS:AD456`<br>Inválido: `INVALIDO`, `NAVIERA:` |
| **PASOS** | 1. Invocar `validate_sellos_format(value)` |
| **RESULTADO ESPERADO** | Formato válido no lanza excepción. Formato inválido lanza `ValidationError` |
| **MÉTODO DJANGO** | `assertRaises(ValidationError)` |

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from control.models import validate_sellos_format

class TestSellosFormat(TestCase):
    def test_sello_simple_valido(self):
        validate_sellos_format("NAVIERA:HL123456*")
    
    def test_sellos_multiples_validos(self):
        validate_sellos_format("NAVIERA:HL123*|ADUANAS:AD456")
    
    def test_sello_formato_invalido(self):
        with self.assertRaises(ValidationError):
            validate_sellos_format("FORMATO_INCORRECTO")
```

---

### 📋 CP-005: Vista pública de búsqueda de contenedor

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Buscar contenedor desde interfaz pública |
| **CASO DE USO RELACIONADO** | CU06 - Consultar Contenedor |
| **REQUERIMIENTO FUNCIONAL** | RF09 |
| **TIPO DE PRUEBA** | Aceptación |
| **DESCRIPCIÓN** | Verificar que un cliente pueda buscar un contenedor por código ISO desde la página principal. |
| **PRERREQUISITOS** | Contenedor `MSKU9070323` existente en la base de datos |
| **DATOS DE ENTRADA** | Query: `codigo=MSKU9070323` |
| **PASOS** | 1. Crear contenedor de prueba<br>2. GET a `/buscar/?codigo=MSKU9070323`<br>3. Verificar respuesta |
| **RESULTADO ESPERADO** | Respuesta 200, contenido incluye información del contenedor |
| **MÉTODO DJANGO** | `self.client.get()`, `assertContains()` |

```python
from django.test import TestCase, Client
from django.urls import reverse
from control.models import Buque, Arribo, Contenedor, Transitario

class TestBusquedaContenedor(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear datos de prueba
        self.buque = Buque.objects.create(
            nombre="Test Ship",
            imo_number="1234567",
            naviera="Test",
            pabellon_bandera="PA",
            eslora_metros=200, manga_metros=30, calado_metros=10,
            teu_capacidad=5000
        )
        self.transitario = Transitario.objects.create(
            razon_social="Test Transit",
            identificador_tributario="12345678901",
            direccion="Test Address",
            tipo_servicio="NVOCC"
        )
        from django.utils import timezone
        self.arribo = Arribo.objects.create(
            buque=self.buque,
            tipo_operacion="DESCARGA",
            fecha_eta=timezone.now(),
            muelle="MUELLE-A"
        )
        self.contenedor = Contenedor.objects.create(
            arribo=self.arribo,
            transitario=self.transitario,
            codigo_iso="MSKU9070323",
            direccion="IMPORT",
            tipo="22G1",
            peso_bruto_kg=25000,
            bl_referencia="TEST-BL-001",
            puerto_origen="Shanghai",
            descripcion_mercancia="Test cargo"
        )
    
    def test_buscar_contenedor_existente(self):
        response = self.client.get(
            reverse('control:buscar'),
            {'codigo': 'MSKU9070323'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MSKU9070323')
    
    def test_buscar_contenedor_no_existente(self):
        response = self.client.get(
            reverse('control:buscar'),
            {'codigo': 'XXXX0000000'}
        )
        self.assertEqual(response.status_code, 200)
        # Debe indicar que no se encontró
```

---

### 📋 CP-006: Registro de Queja por Cliente

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Cliente registra queja con contenedor asociado |
| **CASO DE USO RELACIONADO** | CU07 - Registrar Queja |
| **REQUERIMIENTO FUNCIONAL** | RF10 |
| **TIPO DE PRUEBA** | Aceptación |
| **DESCRIPCIÓN** | Verificar que un cliente pueda registrar una queja asociada a un contenedor existente. |
| **PRERREQUISITOS** | Contenedor existente en la BD |
| **DATOS DE ENTRADA** | nombre_cliente, email, categoria="DEMORA", descripcion, codigo_contenedor |
| **PASOS** | 1. POST a `/quejas/` con datos válidos<br>2. Verificar creación de `Queja`<br>3. Verificar `QuejaContenedor` asociado |
| **RESULTADO ESPERADO** | Queja creada con estado "PENDIENTE", relación con contenedor establecida |
| **MÉTODO DJANGO** | `self.client.post()`, `assertEqual` |

```python
from django.test import TestCase, Client
from django.urls import reverse
from control.models import Queja, QuejaContenedor, Contenedor

class TestQuejaRegistro(TestCase):
    # setUp similar al anterior para crear contenedor
    
    # ===== HAPPY PATH =====
    def test_registrar_queja_valida(self):
        data = {
            'nombre_cliente': 'Juan Pérez',
            'email_cliente': 'juan@test.com',
            'telefono_cliente': '999888777',
            'categoria': 'DEMORA',
            'descripcion': 'El contenedor lleva 5 días de retraso',
            'contenedores[]': ['MSKU9070323']
        }
        response = self.client.post(reverse('control:quejas'), data)
        
        self.assertEqual(Queja.objects.count(), 1)
        queja = Queja.objects.first()
        self.assertEqual(queja.estado, 'PENDIENTE')
        self.assertEqual(queja.cantidad_contenedores, 1)
    
    # ===== ERROR PATH =====
    def test_queja_email_invalido_falla(self):
        """Error: Email con formato incorrecto"""
        data = {
            'nombre_cliente': 'Juan Pérez',
            'email_cliente': 'email-sin-arroba',  # Email inválido
            'telefono_cliente': '999888777',
            'categoria': 'DEMORA',
            'descripcion': 'Descripción válida',
            'contenedores[]': ['MSKU9070323']
        }
        response = self.client.post(reverse('control:quejas'), data)
        self.assertEqual(Queja.objects.count(), 0)  # No se creó
    
    def test_queja_sin_descripcion_falla(self):
        """Error: Campo descripción obligatorio vacío"""
        data = {
            'nombre_cliente': 'Juan Pérez',
            'email_cliente': 'juan@test.com',
            'telefono_cliente': '999888777',
            'categoria': 'DEMORA',
            'descripcion': '',  # Vacío
            'contenedores[]': ['MSKU9070323']
        }
        response = self.client.post(reverse('control:quejas'), data)
        self.assertEqual(Queja.objects.count(), 0)  # No se creó
    
    def test_queja_contenedor_inexistente_falla(self):
        """Error: Contenedor referenciado no existe"""
        data = {
            'nombre_cliente': 'Juan Pérez',
            'email_cliente': 'juan@test.com',
            'telefono_cliente': '999888777',
            'categoria': 'DEMORA',
            'descripcion': 'Descripción válida',
            'contenedores[]': ['XXXX0000000']  # No existe
        }
        response = self.client.post(reverse('control:quejas'), data)
        self.assertEqual(Queja.objects.count(), 0)  # No se creó
```

---

### 📋 CP-007: Generación de PDF - Ficha de Contenedor

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Generar PDF de ficha completa de contenedor |
| **CASO DE USO RELACIONADO** | CU03 - Gestionar Contenedores |
| **REQUERIMIENTO FUNCIONAL** | RF03 |
| **TIPO DE PRUEBA** | Aceptación |
| **DESCRIPCIÓN** | Verificar que un usuario admin pueda generar un PDF con la ficha completa del contenedor. |
| **PRERREQUISITOS** | Usuario staff autenticado, contenedor existente |
| **DATOS DE ENTRADA** | codigo_iso del contenedor |
| **PASOS** | 1. Autenticar como staff<br>2. GET a `/pdf/ficha/{codigo_iso}/`<br>3. Verificar respuesta PDF |
| **RESULTADO ESPERADO** | Response 200 con Content-Type `application/pdf` |
| **MÉTODO DJANGO** | `assertEqual(response['Content-Type'], 'application/pdf')` |

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class TestPDFGeneration(TestCase):
    def setUp(self):
        # Crear superusuario
        self.admin = User.objects.create_superuser(
            'admin', 'admin@test.com', 'admin123'
        )
        self.user_normal = User.objects.create_user(
            'user', 'user@test.com', 'user123'
        )
        self.client.login(username='admin', password='admin123')
        # Crear contenedor de prueba...
    
    # ===== HAPPY PATH =====
    def test_generar_pdf_ficha_contenedor(self):
        response = self.client.get(
            reverse('control:pdf_ficha_contenedor', 
                    kwargs={'codigo_iso': 'MSKU9070323'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    # ===== ERROR PATH =====
    def test_pdf_contenedor_inexistente_404(self):
        """Error: Contenedor no existe"""
        response = self.client.get(
            reverse('control:pdf_ficha_contenedor', 
                    kwargs={'codigo_iso': 'XXXX0000000'})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_pdf_sin_autenticar_redirige(self):
        """Error: Usuario no autenticado es redirigido"""
        self.client.logout()
        response = self.client.get(
            reverse('control:pdf_ficha_contenedor', 
                    kwargs={'codigo_iso': 'MSKU9070323'})
        )
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_pdf_usuario_normal_denegado(self):
        """Error: Usuario sin permisos staff no puede acceder"""
        self.client.login(username='user', password='user123')
        response = self.client.get(
            reverse('control:pdf_ficha_contenedor', 
                    kwargs={'codigo_iso': 'MSKU9070323'})
        )
        self.assertEqual(response.status_code, 403)
```

---

### 📋 CP-008: Validación de Aprobación Aduanera

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Número de despacho aduanero con formato correcto |
| **CASO DE USO RELACIONADO** | CU04 - Gestionar Permisos Aduaneros |
| **REQUERIMIENTO FUNCIONAL** | RF05 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar que el número de despacho aduanero cumpla el formato `XXX-YYYY-MM-NNNNNN`. |
| **PRERREQUISITOS** | Contenedor existente sin aprobación aduanera previa |
| **DATOS DE ENTRADA** | Válido: `118-2025-10-012345`, Inválido: `123456` |
| **PASOS** | 1. Crear `AprobacionAduanera` con numero_despacho<br>2. Ejecutar `full_clean()` |
| **RESULTADO ESPERADO** | Formato válido pasa, formato inválido lanza `ValidationError` |
| **MÉTODO DJANGO** | `assertRaises(ValidationError)` |

```python
from django.test import TestCase
from control.models import AprobacionAduanera, Contenedor

class TestAprobacionAduanera(TestCase):
    def test_numero_despacho_formato_valido(self):
        aprobacion = AprobacionAduanera(
            contenedor=self.contenedor,
            numero_despacho="118-2025-10-012345",
            estado="APROBADO"
        )
        aprobacion.full_clean()  # No debe lanzar error
    
    def test_numero_despacho_formato_invalido(self):
        aprobacion = AprobacionAduanera(
            contenedor=self.contenedor,
            numero_despacho="INVALIDO-123",
            estado="APROBADO"
        )
        with self.assertRaises(ValidationError):
            aprobacion.full_clean()
```

---

### 📋 CP-009: Flujo de eventos de contenedor (Importación)

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Secuencia válida de eventos para importación |
| **CASO DE USO RELACIONADO** | CU13 - Gestionar Evento Contenedor |
| **REQUERIMIENTO FUNCIONAL** | RF05 |
| **TIPO DE PRUEBA** | Unitaria (2 tests atómicos) |
| **DESCRIPCIÓN** | Verificar que los eventos de contenedor sigan la secuencia correcta según las reglas de negocio del workflow de importación. |
| **PRERREQUISITOS** | Contenedor de importación existente |
| **DATOS DE ENTRADA** | Eventos en orden: DISCHARGED → GATE_OUT_FULL → DELIVERED |
| **PASOS** | 1. Crear evento DISCHARGED<br>2. Crear evento GATE_OUT_FULL<br>3. Crear evento DELIVERED<br>4. Intentar crear GATE_IN_FULL (fuera de secuencia) |
| **RESULTADO ESPERADO** | Secuencia válida se guarda, evento fuera de orden lanza `ValidationError` |
| **MÉTODO DJANGO** | `assertRaises(ValidationError)` |

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from control.models import EventoContenedor, Contenedor

class TestEventosContenedor(TestCase):
    # ===== HAPPY PATH =====
    def test_secuencia_importacion_valida(self):
        """Secuencia correcta: DISCHARGED → GATE_OUT_FULL"""
        evento1 = EventoContenedor.objects.create(
            contenedor=self.contenedor,
            tipo_evento="DISCHARGED",
            descripcion="Descargado del buque"
        )
        self.assertIsNotNone(evento1.pk)
        
        evento2 = EventoContenedor.objects.create(
            contenedor=self.contenedor,
            tipo_evento="GATE_OUT_FULL",
            descripcion="Salida del puerto"
        )
        self.assertIsNotNone(evento2.pk)
    
    def test_ultimo_evento_contenedor(self):
        """RF05: Verificar que el contenedor muestre su evento actual"""
        EventoContenedor.objects.create(
            contenedor=self.contenedor,
            tipo_evento="DISCHARGED",
            descripcion="Descargado del buque"
        )
        EventoContenedor.objects.create(
            contenedor=self.contenedor,
            tipo_evento="GATE_OUT_FULL",
            descripcion="Salida del puerto"
        )
        
        ultimo = self.contenedor.ultimo_evento
        self.assertEqual(ultimo.tipo_evento, "GATE_OUT_FULL")
        self.assertEqual(self.contenedor.ultimo_estado, "GATE_OUT_FULL")
    
    # ===== ERROR PATH =====
    def test_evento_fuera_secuencia_falla(self):
        """Error: No se puede crear GATE_IN_FULL sin prerequisitos"""
        # Intentar crear evento que requiere prerequisitos sin tenerlos
        evento = EventoContenedor(
            contenedor=self.contenedor,
            tipo_evento="GATE_IN_FULL",  # Requiere eventos previos
            descripcion="Intento de ingreso sin descarga previa"
        )
        with self.assertRaises(ValidationError):
            evento.full_clean()
    
    def test_evento_tipo_invalido_falla(self):
        """Error: Tipo de evento no válido"""
        evento = EventoContenedor(
            contenedor=self.contenedor,
            tipo_evento="TIPO_INEXISTENTE",
            descripcion="Evento inválido"
        )
        with self.assertRaises(ValidationError):
            evento.full_clean()
```

---

### 📋 CP-010: Gestión de Transitario

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | CRUD completo de transitario |
| **CASO DE USO RELACIONADO** | CU11 - Gestionar Transitarios |
| **REQUERIMIENTO FUNCIONAL** | RF11, RF13 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar creación, lectura, actualización y eliminación de transitarios. |
| **PRERREQUISITOS** | Ninguno |
| **DATOS DE ENTRADA** | Datos completos de transitario (razón social, RUC, etc.) |
| **PASOS** | 1. Crear transitario<br>2. Leer y verificar<br>3. Actualizar campo<br>4. Verificar actualización |
| **RESULTADO ESPERADO** | Todas las operaciones CRUD funcionan correctamente |
| **MÉTODO DJANGO** | `assertEqual`, `assertIsNotNone` |

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from control.models import Transitario

class TestTransitarioModel(TestCase):
    # ===== HAPPY PATH =====
    def test_crear_transitario(self):
        transitario = Transitario.objects.create(
            razon_social="Logistics Peru SAC",
            identificador_tributario="20512345678",
            direccion="Av. Argentina 3458, Lima",
            tipo_servicio="NVOCC",
            email_contacto="contacto@logistics.pe"
        )
        self.assertIsNotNone(transitario.pk)
        self.assertEqual(transitario.estado_operacion, "ACTIVO")
    
    def test_actualizar_transitario(self):
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
    
    # ===== ERROR PATH =====
    def test_transitario_ruc_invalido_falla(self):
        """Error: RUC con formato incorrecto (no 11 dígitos)"""
        transitario = Transitario(
            razon_social="Test SAC",
            identificador_tributario="123",  # Muy corto
            direccion="Test Address",
            tipo_servicio="NVOCC"
        )
        with self.assertRaises(ValidationError):
            transitario.full_clean()
    
    def test_transitario_sin_razon_social_falla(self):
        """Error: Campo obligatorio faltante"""
        transitario = Transitario(
            razon_social="",  # Vacío
            identificador_tributario="20512345680",
            direccion="Test Address",
            tipo_servicio="NVOCC"
        )
        with self.assertRaises(ValidationError):
            transitario.full_clean()
```

---

### 📋 CP-011: Facturación y Estados de Pago

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Ciclo de vida de factura (emisión → pago) |
| **CASO DE USO RELACIONADO** | CU05 - Gestionar Registro Facturas |
| **REQUERIMIENTO FUNCIONAL** | RF07, RF08 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar el flujo de estados de una factura desde emisión hasta pago. |
| **PRERREQUISITOS** | Contenedor existente |
| **DATOS DE ENTRADA** | Factura con monto USD, servicios facturados |
| **PASOS** | 1. Crear factura en estado PENDIENTE<br>2. Actualizar estado a PAGADA con fecha_pago<br>3. Verificar método `permite_gate_pass()` |
| **RESULTADO ESPERADO** | Factura pagada retorna `True` en `permite_gate_pass()` |
| **MÉTODO DJANGO** | `assertTrue`, `assertEqual` |

```python
from django.test import TestCase
from django.utils import timezone
from control.models import AprobacionFinanciera, Contenedor

class TestAprobacionFinanciera(TestCase):
    def test_factura_pendiente_no_permite_gate_pass(self):
        factura = AprobacionFinanciera.objects.create(
            contenedor=self.contenedor,
            numero_factura="F001-0001234",
            fecha_emision=timezone.now().date(),
            monto_usd=1500.00,
            estado_financiero="PENDIENTE"
        )
        self.assertFalse(factura.permite_gate_pass())
    
    def test_factura_pagada_permite_gate_pass(self):
        factura = AprobacionFinanciera.objects.create(
            contenedor=self.contenedor,
            numero_factura="F001-0001235",
            fecha_emision=timezone.now().date(),
            monto_usd=1500.00,
            estado_financiero="PAGADA",
            fecha_pago=timezone.now().date()
        )
        self.assertTrue(factura.permite_gate_pass())
```

---

### 📋 CP-012: Pago Transitario al Puerto

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Registro de pago de transitario |
| **CASO DE USO RELACIONADO** | CU12 - Gestionar Pagos Transitarios |
| **REQUERIMIENTO FUNCIONAL** | RF12, RF14 |
| **TIPO DE PRUEBA** | Unitaria |
| **DESCRIPCIÓN** | Verificar que se pueda registrar un pago de transitario con validaciones de monto y comprobante. |
| **PRERREQUISITOS** | Contenedor con transitario asignado |
| **DATOS DE ENTRADA** | Monto USD, número de comprobante, fecha de pago |
| **PASOS** | 1. Crear `AprobacionPagoTransitario`<br>2. Verificar que el método `transitario_ha_pagado()` del contenedor retorne True |
| **RESULTADO ESPERADO** | Contenedor refleja el estado de pago del transitario |
| **MÉTODO DJANGO** | `assertTrue` |

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from control.models import AprobacionPagoTransitario, Contenedor

class TestPagoTransitario(TestCase):
    # ===== HAPPY PATH =====
    def test_pago_transitario_actualiza_estado(self):
        pago = AprobacionPagoTransitario.objects.create(
            contenedor=self.contenedor,
            transitario=self.contenedor.transitario,
            monto_usd=500.00,
            numero_comprobante="OP-2025-001234",
            fecha_pago=timezone.now().date()
        )
        
        self.contenedor.refresh_from_db()
        self.assertTrue(self.contenedor.transitario_ha_pagado())
    
    # ===== ERROR PATH =====
    def test_pago_monto_negativo_falla(self):
        """Error: Monto no puede ser negativo"""
        pago = AprobacionPagoTransitario(
            contenedor=self.contenedor,
            transitario=self.contenedor.transitario,
            monto_usd=-100.00,  # Negativo
            numero_comprobante="OP-2025-001235",
            fecha_pago=timezone.now().date()
        )
        with self.assertRaises(ValidationError):
            pago.full_clean()
    
    def test_pago_sin_comprobante_falla(self):
        """Error: Número de comprobante obligatorio"""
        pago = AprobacionPagoTransitario(
            contenedor=self.contenedor,
            transitario=self.contenedor.transitario,
            monto_usd=500.00,
            numero_comprobante="",  # Vacío
            fecha_pago=timezone.now().date()
        )
        with self.assertRaises(ValidationError):
            pago.full_clean()
    
    def test_pago_monto_cero_falla(self):
        """Error: Monto debe ser mayor que cero"""
        pago = AprobacionPagoTransitario(
            contenedor=self.contenedor,
            transitario=self.contenedor.transitario,
            monto_usd=0.00,  # Cero
            numero_comprobante="OP-2025-001236",
            fecha_pago=timezone.now().date()
        )
        with self.assertRaises(ValidationError):
            pago.full_clean()
```

---

### 📋 CP-013: Permisos de Usuario Admin

| Campo | Detalle |
|:---|:---|
| **NOMBRE DEL CASO DE PRUEBA** | Solo staff puede acceder a APIs internas |
| **CASO DE USO RELACIONADO** | CU09, CU10 - Gestionar Empleados y Permisos |
| **REQUERIMIENTO FUNCIONAL** | RF01, RF02 |
| **TIPO DE PRUEBA** | Aceptación |
| **DESCRIPCIÓN** | Verificar que las APIs internas (SUNAT, IMO) solo sean accesibles para usuarios staff. |
| **PRERREQUISITOS** | Usuario normal y usuario staff |
| **DATOS DE ENTRADA** | RUC o IMO para consulta |
| **PASOS** | 1. GET a API sin autenticación → 403<br>2. GET autenticado como staff → 200 |
| **RESULTADO ESPERADO** | Usuarios no autorizados reciben 403 Forbidden |
| **MÉTODO DJANGO** | `assertEqual(response.status_code, 403)` |

```python
from django.test import TestCase
from django.contrib.auth.models import User

class TestAPIPermissions(TestCase):
    def setUp(self):
        self.user_normal = User.objects.create_user('user', 'user@test.com', 'user123')
        self.user_staff = User.objects.create_user('staff', 'staff@test.com', 'staff123', is_staff=True)
    
    def test_api_sunat_sin_autenticar(self):
        response = self.client.get(
            reverse('control:consultar_ruc_sunat', kwargs={'ruc': '20100055237'})
        )
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_api_sunat_usuario_normal(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(
            reverse('control:consultar_ruc_sunat', kwargs={'ruc': '20100055237'})
        )
        self.assertEqual(response.status_code, 403)
    
    def test_api_sunat_usuario_staff(self):
        self.client.login(username='staff', password='staff123')
        response = self.client.get(
            reverse('control:consultar_ruc_sunat', kwargs={'ruc': '20100055237'})
        )
        self.assertEqual(response.status_code, 200)
```

---

## 6. MATRIZ DE TRAZABILIDAD: Casos de Prueba vs Casos de Uso

| Caso de Prueba | CU01 | CU02 | CU03 | CU04 | CU05 | CU06 | CU07 | CU08 | CU09 | CU10 | CU11 | CU12 | CU13 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CP-001** |  |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| **CP-002** |  | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| **CP-003** | ✓ |  |  |  |  |  |  |  |  |  |  |  |  |
| **CP-004** |  |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| **CP-005** |  |  |  |  |  | ✓ |  |  |  |  |  |  |  |
| **CP-006** |  |  |  |  |  |  | ✓ |  |  |  |  |  |  |
| **CP-007** |  |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| **CP-008** |  |  |  | ✓ |  |  |  |  |  |  |  |  |  |
| **CP-009** |  |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| **CP-010** |  |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| **CP-011** |  |  |  |  | ✓ |  |  |  |  |  |  |  |  |
| **CP-012** |  |  |  |  |  |  |  |  |  |  |  | ✓ |  |
| **CP-013** |  |  |  |  |  |  |  |  | ✓ | ✓ |  |  |  |

---

## 7. RESUMEN DE COBERTURA

### Por tipo de prueba

| Tipo | Casos de Prueba | Cantidad |
|:---|:---|:---:|
| **Unitaria** | CP-001, CP-002, CP-003, CP-004, CP-008, CP-009, CP-010, CP-011, CP-012 | 9 |
| **Aceptación** | CP-005, CP-006, CP-007, CP-013 | 4 |
| **Total** | | **13** |

> [!NOTE]
> **Pruebas Unitarias**: Verifican el comportamiento de métodos/funciones de forma aislada e independiente.
> **Pruebas de Aceptación**: Simulan la interacción del usuario final para validar que el sistema cumple los requisitos funcionales esperados.

### Por Requerimiento Funcional

| RF | Casos de Prueba |
|:---|:---|
| RF01 | CP-013 |
| RF02 | CP-013 |
| RF03 | CP-007 |
| RF04 | CP-003 |
| RF05 | CP-001, CP-004, CP-008, CP-009 |
| RF06 | CP-002 |
| RF07 | CP-011 |
| RF08 | CP-011 |
| RF09 | CP-005 |
| RF10 | CP-006 |
| RF11 | CP-010 |
| RF12 | CP-012 |
| RF13 | CP-010 |
| RF14 | CP-012 |

---

## 8. NOTAS DE IMPLEMENTACIÓN

### Configuración recomendada en `settings.py`

```python
# settings.py para testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # BD en memoria para tests rápidos
    }
}
```

### Estructura de archivos de test sugerida

```
control/
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # CP-002, CP-003, CP-010, CP-011, CP-012
│   ├── test_validators.py      # CP-001, CP-004, CP-008
│   ├── test_views.py           # CP-005, CP-006, CP-007
│   ├── test_events.py          # CP-009
│   └── test_permissions.py     # CP-013
└── tests.py  # Puede eliminarse o mantener imports
```

### Fixtures recomendados

Crear un archivo `control/fixtures/test_data.json` con datos de prueba consistentes para todos los tests.

---

*Documento generado para SigepAdmin - IDAT 2025*
*Versión: 1.0*
*Fecha: 2025-12-12*
