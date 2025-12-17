"""
Tests Unitarios - Validadores
Casos de Prueba: CP-001, CP-004, CP-008
"""
from django.test import TestCase
from django.core.exceptions import ValidationError

from control.models import (
    validate_iso_6346,
    validate_sellos_format,
)


class TestValidacionISO6346(TestCase):
    """CP-001: Validación ISO 6346 en Código de Contenedor"""
    
    # ===== HAPPY PATH =====
    def test_codigo_valido_msku(self):
        """Código ISO válido con dígito verificador correcto"""
        # No debe lanzar excepción
        try:
            validate_iso_6346("MSKU9070323")
        except ValidationError:
            self.fail("validate_iso_6346 lanzó ValidationError para código válido")
    
    # ===== ERROR PATH =====
    def test_codigo_digito_incorrecto(self):
        """Error: Dígito verificador incorrecto"""
        with self.assertRaises(ValidationError):
            validate_iso_6346("MSKU9070322")  # Dígito correcto es 3, no 2
    
    def test_codigo_formato_invalido_corto(self):
        """Error: Código muy corto"""
        with self.assertRaises(ValidationError):
            validate_iso_6346("MSK907")
    
    def test_codigo_formato_invalido_letras(self):
        """Error: Formato completamente inválido"""
        with self.assertRaises(ValidationError):
            validate_iso_6346("INVALIDO")
    
    def test_codigo_vacio(self):
        """Error: Código vacío"""
        with self.assertRaises(ValidationError):
            validate_iso_6346("")


class TestSellosFormat(TestCase):
    """CP-004: Formato de sellos de contenedor"""
    
    # ===== HAPPY PATH =====
    def test_sello_simple_valido(self):
        """Sello simple con marcador principal"""
        try:
            validate_sellos_format("NAVIERA:HL123456*")
        except ValidationError:
            self.fail("validate_sellos_format lanzó ValidationError para formato válido")
    
    def test_sellos_multiples_validos(self):
        """Múltiples sellos separados por pipe"""
        try:
            validate_sellos_format("NAVIERA:HL123*|ADUANAS:AD456")
        except ValidationError:
            self.fail("validate_sellos_format lanzó ValidationError para formato válido")
    
    # ===== ERROR PATH =====
    def test_sello_formato_invalido(self):
        """Error: Formato sin tipo:codigo"""
        with self.assertRaises(ValidationError):
            validate_sellos_format("FORMATO_INCORRECTO")
    
    def test_sello_tipo_vacio(self):
        """Error: Tipo de sello vacío"""
        with self.assertRaises(ValidationError):
            validate_sellos_format(":CODIGO123*")
