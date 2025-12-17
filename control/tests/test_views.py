"""
Tests de Aceptación - Vistas Públicas
Casos de Prueba: CP-005, CP-006, CP-007
"""
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from control.models import (
    Buque,
    Arribo,
    Transitario,
    Contenedor,
    Queja,
)


class TestBusquedaContenedor(TestCase):
    """CP-005: Vista pública de búsqueda de contenedor"""
    
    def setUp(self):
        self.client = Client()
        
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
    def test_buscar_contenedor_existente(self):
        """Cliente busca contenedor existente"""
        response = self.client.get(
            reverse('control:buscar'),
            {'codigo': 'MSKU9070323'}
        )
        self.assertEqual(response.status_code, 200)
    
    # ===== ERROR PATH =====
    def test_buscar_contenedor_no_existente(self):
        """Cliente busca contenedor que no existe"""
        response = self.client.get(
            reverse('control:buscar'),
            {'codigo': 'XXXX0000000'}
        )
        self.assertEqual(response.status_code, 200)  # Retorna página con mensaje "no encontrado"


class TestQuejaRegistro(TestCase):
    """CP-006: Registro de Queja por Cliente"""
    
    def setUp(self):
        self.client = Client()
        
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
    def test_pagina_quejas_accesible(self):
        """Página de quejas es accesible públicamente"""
        response = self.client.get(reverse('control:quejas'))
        self.assertEqual(response.status_code, 200)
    
    # ===== ERROR PATH =====
    def test_queja_sin_datos_falla(self):
        """Formulario vacío no crea queja"""
        response = self.client.post(reverse('control:quejas'), {})
        self.assertEqual(Queja.objects.count(), 0)


class TestPDFGeneration(TestCase):
    """CP-007: Generación de PDF - Ficha de Contenedor"""
    
    def setUp(self):
        self.admin = User.objects.create_superuser(
            'admin', 'admin@test.com', 'admin123'
        )
        self.user_normal = User.objects.create_user(
            'user', 'user@test.com', 'user123'
        )
        
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
    def test_generar_pdf_ficha_contenedor(self):
        """Admin genera PDF de ficha de contenedor"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(
            reverse('control:pdf_ficha_contenedor', 
                    kwargs={'codigo_iso': 'CSQU3054383'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    # ===== ERROR PATH =====
    def test_pdf_contenedor_inexistente_404(self):
        """Error: Contenedor no existe retorna 404"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(
            reverse('control:pdf_ficha_contenedor', 
                    kwargs={'codigo_iso': 'XXXX0000000'})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_pdf_sin_autenticar_es_publico(self):
        """Vista PDF es pública (accesible sin autenticación)"""
        response = self.client.get(
            reverse('control:pdf_ficha_contenedor', 
                    kwargs={'codigo_iso': 'CSQU3054383'})
        )
        # La vista es pública, retorna el PDF directamente
        self.assertEqual(response.status_code, 200)
