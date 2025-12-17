"""
Tests Unitarios - Eventos de Contenedor
Casos de Prueba: CP-009
"""
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from control.models import (
    Buque,
    Arribo,
    Transitario,
    Contenedor,
    EventoContenedor,
)


class TestEventosContenedor(TestCase):
    """CP-009: Flujo de eventos de contenedor (Importación)"""
    
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
            codigo_iso="CSQU3054383",
            direccion="IMPORT",
            tipo_tamaño="22G1",
            peso_bruto_kg=25000,
            numero_sello="NAVIERA:HL345678*",
            mercancia_declarada="Test cargo",
            ubicacion_actual="PATIO-A",
            bl_referencia="TEST-BL-003"
        )
    
    # ===== HAPPY PATH =====
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
        # ultimo_estado retorna el display del tipo_evento, no el código
        self.assertIn("Gate Out", self.contenedor.ultimo_estado)
    
    # ===== ERROR PATH =====
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
