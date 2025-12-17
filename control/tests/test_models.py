"""
Tests Unitarios - Modelos
Casos de Prueba: CP-002, CP-003, CP-010, CP-011, CP-012
"""
from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from control.models import (
    Buque,
    Arribo,
    Transitario,
    Contenedor,
    AprobacionFinanciera,
    AprobacionPagoTransitario,
)


class TestBuqueModel(TestCase):
    """CP-002: Creación de Buque con IMO válido"""
    
    # ===== HAPPY PATH =====
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
    
    # ===== ERROR PATH =====
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


class TestArriboValidations(TestCase):
    """CP-003: Validación de fechas en Arribo"""
    
    def setUp(self):
        self.buque = Buque.objects.create(
            nombre="Test Ship",
            imo_number="1234567",
            naviera="Test Line",
            pabellon_bandera="PA",
            puerto_registro="Lima",
            callsign="TESTC",
            eslora_metros=Decimal("200.00"),
            manga_metros=Decimal("30.00"),
            calado_metros=Decimal("10.00"),
            teu_capacidad=5000
        )
    
    # ===== HAPPY PATH =====
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
    
    # ===== ERROR PATH =====
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


class TestTransitarioModel(TestCase):
    """CP-010: Gestión de Transitario"""
    
    # ===== HAPPY PATH =====
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
    
    # ===== ERROR PATH =====
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


class TestAprobacionFinanciera(TestCase):
    """CP-011: Facturación y Estados de Pago"""
    
    def setUp(self):
        self.buque = Buque.objects.create(
            nombre="Test Ship",
            imo_number="1234567",
            naviera="Test",
            pabellon_bandera="PA",
            puerto_registro="Lima",
            callsign="TESTC",
            eslora_metros=Decimal("200"),
            manga_metros=Decimal("30"),
            calado_metros=Decimal("10"),
            teu_capacidad=5000
        )
        self.transitario = Transitario.objects.create(
            razon_social="Test Transit",
            identificador_tributario="20512345678",
            direccion="Test Address",
            tipo_servicio="NVOCC"
        )
        self.arribo = Arribo.objects.create(
            buque=self.buque,
            tipo_operacion="DESCARGA",
            fecha_eta=timezone.now(),
            muelle_berth="MUELLE-A",
            servicios_contratados="Descarga",
            contenedores_descarga=10
        )
        self.contenedor = Contenedor.objects.create(
            arribo=self.arribo,
            transitario=self.transitario,
            codigo_iso="MSKU9070323",
            direccion="IMPORT",
            tipo_tamaño="22G1",
            peso_bruto_kg=25000,
            numero_sello="NAVIERA:HL123456*",
            mercancia_declarada="Test cargo",
            ubicacion_actual="PATIO-A",
            bl_referencia="TEST-BL-001"
        )
    
    # ===== HAPPY PATH =====
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


class TestPagoTransitario(TestCase):
    """CP-012: Pago Transitario al Puerto - Validación de campo transitario"""
    
    def setUp(self):
        self.buque = Buque.objects.create(
            nombre="Test Ship",
            imo_number="1234567",
            naviera="Test",
            pabellon_bandera="PA",
            puerto_registro="Lima",
            callsign="TESTC",
            eslora_metros=Decimal("200"),
            manga_metros=Decimal("30"),
            calado_metros=Decimal("10"),
            teu_capacidad=5000
        )
        self.transitario = Transitario.objects.create(
            razon_social="Test Transit",
            identificador_tributario="20512345678",
            direccion="Test Address",
            tipo_servicio="NVOCC"
        )
        self.arribo = Arribo.objects.create(
            buque=self.buque,
            tipo_operacion="DESCARGA",
            fecha_eta=timezone.now(),
            muelle_berth="MUELLE-A",
            servicios_contratados="Descarga",
            contenedores_descarga=10
        )
        self.contenedor = Contenedor.objects.create(
            arribo=self.arribo,
            transitario=self.transitario,
            codigo_iso="HLXU8142385",
            direccion="IMPORT",
            tipo_tamaño="22G1",
            peso_bruto_kg=25000,
            numero_sello="NAVIERA:HL234567*",
            mercancia_declarada="Test cargo",
            ubicacion_actual="PATIO-A",
            bl_referencia="TEST-BL-002"
        )
    
    # ===== HAPPY PATH =====
    def test_transitario_ha_pagado_sin_registro(self):
        """Contenedor sin registro de pago retorna False"""
        # transitario_ha_pagado es propiedad, no método
        self.assertFalse(self.contenedor.transitario_ha_pagado)
    
    # ===== ERROR PATH =====
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
