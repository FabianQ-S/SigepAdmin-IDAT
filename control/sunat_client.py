"""
Cliente para consultar la API de SUNAT (RUC)

Configuración:
    En settings.py o como variables de entorno:
    - SUNAT_API_TOKEN: Token de autenticación
    - SUNAT_API_PROVIDER: Proveedor de API (apis.net.pe, apiperu.dev, decolecta)

Proveedores soportados:
    1. apis.net.pe - Regístrate en https://apis.net.pe/
    2. apiperu.dev - Regístrate en https://apiperu.dev/
    3. decolecta.com - Regístrate en https://decolecta.com/
"""

import logging
import os

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


# Datos de demostración para RUCs conocidos (cuando no hay token)
DEMO_DATA = {
    "20100070970": {
        "numeroDocumento": "20100070970",
        "nombre": "SUPERMERCADOS PERUANOS SOCIEDAD ANONIMA",
        "nombreComercial": "PLAZA VEA",
        "estado": "ACTIVO",
        "condicion": "HABIDO",
        "direccion": "AV. CENTENARIO NRO. 1642 URB. LAS LADERAS DE MELITON P LIMA - LIMA - LA MOLINA",
        "departamento": "LIMA",
        "provincia": "LIMA",
        "distrito": "LA MOLINA",
        "tipoContribuyente": "SOCIEDAD ANONIMA",
    },
    "20100190797": {
        "numeroDocumento": "20100190797",
        "nombre": "GLORIA S.A.",
        "nombreComercial": "GLORIA",
        "estado": "ACTIVO",
        "condicion": "HABIDO",
        "direccion": "AV. REPUBLICA DE PANAMA NRO. 2461 URB. SANTA CATALINA LIMA - LIMA - LA VICTORIA",
        "departamento": "LIMA",
        "provincia": "LIMA",
        "distrito": "LA VICTORIA",
        "tipoContribuyente": "SOCIEDAD ANONIMA",
    },
    "20131312955": {
        "numeroDocumento": "20131312955",
        "nombre": "TELEFONICA DEL PERU S.A.A.",
        "nombreComercial": "MOVISTAR",
        "estado": "ACTIVO",
        "condicion": "HABIDO",
        "direccion": "AV. AREQUIPA NRO. 1155 LIMA - LIMA - SANTA BEATRIZ",
        "departamento": "LIMA",
        "provincia": "LIMA",
        "distrito": "SANTA BEATRIZ",
        "tipoContribuyente": "SOCIEDAD ANONIMA ABIERTA",
    },
}


class SunatClient:
    """Cliente para consultar RUC en la API de SUNAT"""

    def __init__(self):
        # Intentar obtener configuración desde settings, luego desde variables de entorno
        self.token = getattr(settings, "SUNAT_API_TOKEN", None) or os.environ.get(
            "SUNAT_API_TOKEN"
        )
        self.provider = (
            getattr(settings, "SUNAT_API_PROVIDER", None)
            or os.environ.get("SUNAT_API_PROVIDER")
            or "apis.net.pe"
        )
        self.timeout = 10  # segundos

    def consultar(self, ruc: str) -> dict:
        """
        Consulta un RUC en la API de SUNAT.

        Args:
            ruc: Número de RUC (11 dígitos)

        Returns:
            dict con los datos del contribuyente o error
        """
        # Validar formato de RUC
        ruc = str(ruc).strip()
        if not ruc.isdigit() or len(ruc) != 11:
            return {"error": "RUC inválido. Debe tener 11 dígitos."}

        # Si no hay token, usar datos de demostración
        if not self.token:
            return self._demo_data(ruc)

        # Consultar según el proveedor configurado
        try:
            if self.provider == "apis.net.pe":
                return self._consultar_apis_net_pe(ruc)
            elif self.provider == "apiperu.dev":
                return self._consultar_apiperu_dev(ruc)
            elif self.provider == "decolecta":
                return self._consultar_decolecta(ruc)
            else:
                return self._consultar_apis_net_pe(ruc)
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al consultar RUC {ruc}")
            return {"error": "Tiempo de espera agotado. Intente nuevamente."}
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al consultar RUC {ruc}")
            return {"error": "Error de conexión con el servicio de SUNAT."}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar RUC {ruc}: {e}")
            return {"error": f"Error de conexión: {str(e)}"}

    def _demo_data(self, ruc: str) -> dict:
        """Retorna datos de demostración"""
        if ruc in DEMO_DATA:
            data = DEMO_DATA[ruc].copy()
            data["_modo"] = "DEMO - Para datos reales configure SUNAT_API_TOKEN"
            return data
        else:
            return {
                "error": "Modo DEMO: RUC no encontrado en datos de ejemplo",
                "message": f"Configure su token de API para consultar el RUC {ruc}",
                "instrucciones": [
                    "1. Regístrate en https://apis.net.pe/ o https://apiperu.dev/",
                    "2. Obtén tu token gratuito",
                    "3. En settings.py: SUNAT_API_TOKEN = 'tu-token'",
                    "4. O variable de entorno: export SUNAT_API_TOKEN='tu-token'",
                ],
            }

    def _consultar_apis_net_pe(self, ruc: str) -> dict:
        """Consulta usando apis.net.pe"""
        url = f"https://api.apis.net.pe/v2/sunat/ruc?numero={ruc}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Referer": "https://apis.net.pe/api-consulta-ruc",
        }

        response = requests.get(url, headers=headers, timeout=self.timeout)
        return self._handle_response(response)

    def _consultar_apiperu_dev(self, ruc: str) -> dict:
        """Consulta usando apiperu.dev"""
        url = "https://apiperu.dev/api/ruc"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {"ruc": ruc}

        response = requests.post(
            url, json=payload, headers=headers, timeout=self.timeout
        )
        result = self._handle_response(response)

        # apiperu.dev envuelve los datos en 'data'
        if "data" in result:
            return result["data"]
        return result

    def _consultar_decolecta(self, ruc: str) -> dict:
        """Consulta usando decolecta.com"""
        url = f"https://api.decolecta.com/v1/sunat/ruc?numero={ruc}"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers, timeout=self.timeout)
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> dict:
        """Procesa la respuesta de la API"""
        if response.ok:
            return response.json()
        else:
            logger.error(f"Error API SUNAT: {response.status_code} - {response.text}")
            return {
                "error": f"Error {response.status_code}",
                "message": response.text,
            }

    def normalizar_datos(self, data: dict) -> dict:
        """
        Normaliza los datos de diferentes proveedores a un formato común.

        Returns:
            dict con campos normalizados:
            - ruc
            - razon_social
            - nombre_comercial
            - estado
            - condicion
            - direccion
            - departamento
            - provincia
            - distrito
            - tipo_contribuyente
        """
        if "error" in data:
            return data

        return {
            "ruc": data.get("numeroDocumento")
            or data.get("numero_documento")
            or data.get("ruc")
            or "",
            "razon_social": data.get("nombre")
            or data.get("razonSocial")
            or data.get("razon_social")
            or "",
            "nombre_comercial": data.get("nombreComercial")
            or data.get("nombre_comercial")
            or "",
            "estado": data.get("estado") or "",
            "condicion": data.get("condicion") or "",
            "direccion": data.get("direccion") or data.get("direccionCompleta") or "",
            "departamento": data.get("departamento") or "",
            "provincia": data.get("provincia") or "",
            "distrito": data.get("distrito") or "",
            "tipo_contribuyente": data.get("tipoContribuyente")
            or data.get("tipo_contribuyente")
            or "",
            "_modo": data.get("_modo"),
        }


# Instancia global del cliente
sunat_client = SunatClient()
