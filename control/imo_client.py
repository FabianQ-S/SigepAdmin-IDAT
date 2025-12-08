"""
Cliente para consultar información de buques por IMO Number.
Integra scraping de VesselFinder directamente sin dependencias externas.

Basado en la lógica de api_barcos.rb (Sinatra) pero implementado en Python.
"""

import json
import re

import requests
from bs4 import BeautifulSoup


class ImoClient:
    """Cliente para consultar datos de buques por IMO mediante scraping."""

    # Datos de demostración para IMOs conocidos (fallback)
    DEMO_SHIPS = {
        "9839133": {
            "imo": "9839133",
            "name": "MSC GULSUN",
            "type": "Container Ship",
            "flag": "Panama",
            "gross_tonnage": 232618,
            "length": 400,
            "beam": 61,
            "year_built": 2019,
            "status": "Active",
            "current_port": "Singapore",
            "destination": "Rotterdam",
            "speed": 18.5,
            "course": 285,
            "lat": 1.2655,
            "lon": 103.8263,
            "draught": 14.5,
            "call_sign": "3FZB9",
            "teu": 23756,
        },
        "9778791": {
            "imo": "9778791",
            "name": "EVER GIVEN",
            "type": "Container Ship",
            "flag": "Panama",
            "gross_tonnage": 220940,
            "length": 400,
            "beam": 59,
            "year_built": 2018,
            "status": "Active",
            "current_port": "Ningbo",
            "destination": "Felixstowe",
            "speed": 14.2,
            "course": 95,
            "lat": 29.8683,
            "lon": 121.9494,
            "draught": 14.5,
            "call_sign": "3FQU8",
            "teu": 20124,
        },
        "9461867": {
            "imo": "9461867",
            "name": "MAERSK MC-KINNEY MOLLER",
            "type": "Container Ship",
            "flag": "Denmark",
            "gross_tonnage": 194849,
            "length": 399,
            "beam": 59,
            "year_built": 2013,
            "status": "Active",
            "current_port": "Tanjung Pelepas",
            "destination": "Algeciras",
            "speed": 16.8,
            "course": 270,
            "lat": 1.3622,
            "lon": 103.5478,
            "draught": 15.5,
            "call_sign": "OXOS2",
            "teu": 18270,
        },
    }

    def __init__(self):
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.timeout = 15
        self.base_url = "https://www.vesselfinder.com"

    def consultar_imo(self, imo: str) -> dict:
        """
        Consulta información de un buque por su número IMO.

        Args:
            imo: Número IMO del buque (7 dígitos)

        Returns:
            dict con los datos del buque o error
        """
        # Validar formato IMO
        imo = str(imo).strip()
        if not imo.isdigit() or len(imo) != 7:
            return {"error": "El número IMO debe tener exactamente 7 dígitos"}

        # Primero intentar con datos demo (fallback rápido)
        if imo in self.DEMO_SHIPS:
            data = self.DEMO_SHIPS[imo].copy()
            data["_source"] = "DEMO - Para datos reales ingrese un IMO válido"
            return self.normalizar_datos(data)

        # Intentar scraping de VesselFinder
        result = self._scrape_vessel_info(imo)

        if "error" in result:
            return result

        return self.normalizar_datos(result)

    def _scrape_vessel_info(self, imo: str) -> dict:
        """
        Realiza scraping de VesselFinder para obtener datos del buque.

        Args:
            imo: Número IMO del buque

        Returns:
            dict con datos crudos o error
        """
        try:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }

            response = requests.get(
                f"{self.base_url}/vessels/details/{imo}",
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                return self._parse_vesselfinder_html(response.text, imo)
            elif response.status_code == 404:
                return {
                    "error": "Buque no encontrado",
                    "message": f"No se encontró un buque con IMO {imo}",
                    "sugerencias": [
                        "Verifica que el IMO sea correcto (7 dígitos)",
                        "Prueba con IMOs de demo: 9839133, 9778791, 9461867",
                    ],
                }
            else:
                return {"error": f"Error del servidor: HTTP {response.status_code}"}

        except requests.exceptions.Timeout:
            return {"error": "Tiempo de espera agotado. Intente nuevamente."}
        except requests.exceptions.ConnectionError:
            return {
                "error": "No se pudo conectar con VesselFinder. Verifique su conexión."
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión: {str(e)}"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}

    def _parse_vesselfinder_html(self, html: str, imo: str) -> dict:
        """
        Parsea el HTML de VesselFinder para extraer datos del buque.

        Args:
            html: Contenido HTML de la página
            imo: Número IMO del buque

        Returns:
            dict con datos parseados
        """
        soup = BeautifulSoup(html, "lxml")

        # Extraer nombre del barco
        name_el = soup.select_one("h1.title")
        name = name_el.text.strip() if name_el else "Unknown"

        # Si no encontramos datos válidos
        if name == "Unknown" or not name:
            return {"error": "No se pudo parsear la información del barco"}

        data = {
            "imo": imo,
            "name": name,
            "_source": "VesselFinder (scraped)",
        }

        # Extraer datos de las tablas de detalles
        for row in soup.select(".tpt1 tr, .aparams tr"):
            cells = row.select("td")
            if len(cells) >= 2:
                key = cells[0].text.strip().lower()
                value = cells[1].text.strip()

                if "ship type" in key:
                    data["type"] = value
                elif "flag" in key:
                    data["flag"] = value
                elif "gross tonnage" in key:
                    data["gross_tonnage"] = self._parse_int(value)
                elif "length overall" in key:
                    data["length"] = self._parse_float(value)
                elif "beam" in key:
                    data["beam"] = self._parse_float(value)
                elif "year of build" in key:
                    data["year_built"] = self._parse_int(value)
                elif key in ("status", "navigation status"):
                    data["status"] = value
                elif "current draught" in key:
                    # Remover 'm' y parsear
                    data["draught"] = self._parse_float(value.replace("m", ""))
                elif "callsign" in key:
                    data["call_sign"] = value
                elif "teu" in key:
                    data["teu"] = self._parse_int(value)
                elif "destination" in key:
                    data["destination"] = value
                elif "speed" in key or "course / speed" in key:
                    # Puede venir como "229.8° / 8.9 kn"
                    if "/" in value:
                        parts = value.split("/")
                        data["course"] = self._parse_float(parts[0].replace("°", ""))
                        data["speed"] = self._parse_float(
                            parts[1].replace("kn", "").strip()
                        )
                    else:
                        data["speed"] = self._parse_float(value.replace("kn", ""))

        # Intentar extraer posición del JSON incrustado
        json_div = soup.select_one("#djson")
        if json_div and json_div.get("data-json"):
            try:
                # Decodificar entidades HTML
                json_str = json_div["data-json"].replace("&quot;", '"')
                json_data = json.loads(json_str)
                data["lat"] = json_data.get("ship_lat")
                data["lon"] = json_data.get("ship_lon")
                if "course" not in data:
                    data["course"] = json_data.get("ship_cog")
                if data.get("speed", 0) == 0:
                    data["speed"] = json_data.get("ship_sog", 0)
            except (json.JSONDecodeError, TypeError):
                pass  # Ignorar errores de parseo JSON

        # Valores por defecto si faltan
        data.setdefault("type", "N/A")
        data.setdefault("flag", "N/A")
        data.setdefault("gross_tonnage", 0)
        data.setdefault("length", 0)
        data.setdefault("beam", 0)
        data.setdefault("year_built", 0)
        data.setdefault("status", "Unknown")
        data.setdefault("draught", 0)
        data.setdefault("call_sign", "")
        data.setdefault("teu", 0)
        data.setdefault("speed", 0)
        data.setdefault("course", 0)
        data.setdefault("lat", 0)
        data.setdefault("lon", 0)

        return data

    def _parse_int(self, value: str) -> int:
        """Parsea un string a entero, removiendo caracteres no numéricos."""
        try:
            # Remover comas, espacios y otros caracteres
            cleaned = re.sub(r"[^\d]", "", str(value))
            return int(cleaned) if cleaned else 0
        except (ValueError, TypeError):
            return 0

    def _parse_float(self, value: str) -> float:
        """Parsea un string a float."""
        try:
            # Remover caracteres excepto dígitos, punto y coma
            cleaned = re.sub(r"[^\d.,]", "", str(value))
            # Reemplazar coma por punto (formato europeo)
            cleaned = cleaned.replace(",", ".")
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0

    def normalizar_datos(self, data: dict) -> dict:
        """
        Normaliza los datos recibidos al formato esperado por el formulario.

        Args:
            data: Datos crudos del scraping o demo

        Returns:
            dict con datos normalizados
        """
        return {
            # Datos principales
            "imo": data.get("imo", ""),
            "nombre": data.get("name", ""),
            "tipo": data.get("type", ""),
            "bandera": data.get("flag", ""),
            # Dimensiones
            "eslora": data.get("length", 0),
            "manga": data.get("beam", 0),
            "calado": data.get("draught", 0),
            "tonelaje_bruto": data.get("gross_tonnage", 0),
            "teu": data.get("teu", 0),
            # Identificación
            "call_sign": data.get("call_sign", ""),
            "year_built": data.get("year_built", 0),
            # Navegación (informativo)
            "status": data.get("status", ""),
            "velocidad": data.get("speed", 0),
            "rumbo": data.get("course", 0),
            "destino": data.get("destination", ""),
            "puerto_actual": data.get("current_port", ""),
            # Coordenadas
            "latitud": data.get("lat", 0),
            "longitud": data.get("lon", 0),
            # Metadata
            "_source": data.get("_source", ""),
        }


# Instancia global del cliente
imo_client = ImoClient()
