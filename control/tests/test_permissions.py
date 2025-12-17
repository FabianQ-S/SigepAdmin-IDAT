"""
Tests de Aceptación - Permisos
Casos de Prueba: CP-013
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestAPIPermissions(TestCase):
    """CP-013: Permisos de Usuario Admin"""
    
    def setUp(self):
        self.client = Client()
        self.user_normal = User.objects.create_user(
            'user', 'user@test.com', 'user123'
        )
        self.user_staff = User.objects.create_user(
            'staff', 'staff@test.com', 'staff123', is_staff=True
        )
    
    # ===== HAPPY PATH =====
    def test_api_sunat_usuario_staff_accede(self):
        """Staff puede acceder a API SUNAT"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(
            reverse('control:consultar_ruc_sunat', kwargs={'ruc': '20100055237'})
        )
        # Puede ser 200 o error de API externa, pero no 403
        self.assertNotEqual(response.status_code, 403)
    
    # ===== ERROR PATH =====
    def test_api_sunat_sin_autenticar_redirige(self):
        """Usuario no autenticado es redirigido a login"""
        response = self.client.get(
            reverse('control:consultar_ruc_sunat', kwargs={'ruc': '20100055237'})
        )
        self.assertIn(response.status_code, [302, 403])
    
    def test_api_sunat_usuario_normal_denegado(self):
        """Usuario normal no puede acceder a API SUNAT"""
        self.client.login(username='user', password='user123')
        response = self.client.get(
            reverse('control:consultar_ruc_sunat', kwargs={'ruc': '20100055237'})
        )
        self.assertIn(response.status_code, [302, 403])
    
    def test_api_imo_usuario_staff_accede(self):
        """Staff puede acceder a API IMO"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(
            reverse('control:consultar_imo_buque', kwargs={'imo': '9839430'})
        )
        self.assertNotEqual(response.status_code, 403)
    
    def test_api_imo_usuario_normal_denegado(self):
        """Usuario normal no puede acceder a API IMO"""
        self.client.login(username='user', password='user123')
        response = self.client.get(
            reverse('control:consultar_imo_buque', kwargs={'imo': '9839430'})
        )
        self.assertIn(response.status_code, [302, 403])
