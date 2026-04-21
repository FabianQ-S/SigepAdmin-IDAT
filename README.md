[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/FabianQ-S/SigepAdmin-IDAT)
# 🚢 SigepAdmin - Sistema de Gestión Portuaria

Sistema de administración portuaria desarrollado con Django para la gestión de buques, arribos y aprobaciones aduaneras.

---

## 📘 Desarrollado por

**Fabián Quintanilla**



**Fabrizio Jimenez**


### 🆔 Institución Educativa
- **IDAT** - Sede: Petit Thouars
- Proyecto académico sobre **Servicios**
- Fecha: **Noviembre 2025**

---

## 📄 Descripción del Proyecto

Este proyecto demuestra el uso, análisis e implementación de servicios web dentro de un entorno de gestión portuaria. El sistema permite administrar:

- 🚢 **Buques**: Registro de embarcaciones con información técnica
- ⚓ **Arribos**: Control de llegadas y operaciones portuarias
- 💰 **Aprobación Financiera**: Gestión de facturas y pagos
- 📋 **Aprobación Aduanera**: Documentos y trámites aduaneros
- 🚛 **Aprobación Pago Transitario**: Comprobantes de pagos a transitarios

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.14
- **Framework**: Django 5.2.7
- **Base de datos**: SQLite (desarrollo)
- **Control de versiones**: Git / GitHub
- **Librerías adicionales**:
  - django-cleanup 9.0.0 (Limpieza automática de archivos)
  - pytz 2025.2 (Manejo de zonas horarias)
  - django-tailwind 4.4.1 (Integración de Tailwind CSS)
  - django-htmx 1.26.0 (Integración HTMX)
  - weasyprint 66.0 (Generación de PDF)
  - pillow 12.0.0 (Procesamiento de imágenes)
  - arrow 1.4.0 (Manejo de fechas)
  - python-decouple 3.8 (Gestión de variables de entorno)

---

## 🌍 Regionalización

El sistema está configurado para Perú:
- 🇵🇪 Idioma: Español
- 🕐 Zona horaria: America/Lima (GMT-5)
- 📅 Formato de fecha: DD/MM/AAAA

---

## 📋 Requisitos

- Python 3.10 o superior
- pip
- virtualenv

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd SigepAdmin
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# O en Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

### 7. Acceder al sistema

Abre tu navegador en: **http://localhost:8000/admin/**

---

## 📁 Estructura del Proyecto

```
SigepAdmin/
├── config/          # Configuración del proyecto Django
│   ├── settings.py  # Configuración principal
│   └── urls.py      # Rutas del proyecto
├── control/         # App principal de gestión portuaria
│   ├── models.py    # Modelos de datos (Buque, Arribo, etc.)
│   ├── admin.py     # Configuración del panel administrativo
│   ├── views.py     # Vistas del sistema
│   ├── locale/      # Formatos de fecha personalizados
│   └── migrations/  # Migraciones de base de datos
├── templates/       # Plantillas HTML
├── media/           # Archivos subidos por usuarios
├── requirements.txt # Dependencias del proyecto
└── manage.py        # Comando de gestión de Django
```

---

## 📚 Modelos del Sistema

### Buque
Información técnica de embarcaciones:
- Nombre, IMO Number, Pabellón
- Dimensiones (eslora, manga, calado)
- Capacidad TEU

### Arribo
Registro de llegadas de buques:
- Fechas ETA/ETD/Arribo Real
- Muelle/Berth asignado
- Tipo de operación (carga/descarga)
- Estado del arribo

### Aprobaciones
Sistema de gestión documental con soporte para archivos PDF/JPG:
- **Financiera**: Facturas y comprobantes
- **Aduanera**: Documentos aduaneros
- **Pago Transitario**: Comprobantes de pago

---

## 🔧 Funcionalidades del Panel Admin

- ✅ Interfaz en español con formato de fecha DD/MM/AAAA
- ✅ Subida de archivos (PDF, JPG, PNG) con validación de tamaño
- ✅ Filtros y búsqueda avanzada
- ✅ Limpieza automática de archivos huérfanos
- ✅ Zona horaria de Perú configurada

---

## 🤝 Contribuir

1. Fork del proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

---

> _"El conocimiento se construye creando."_  
> — **Fabián Quintanilla**

---

## 📝 Licencia

Proyecto académico - IDAT 2025

