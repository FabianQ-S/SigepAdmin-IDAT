# 📘 Guía de Frontend - SigepAdmin IDAT

## 🗂️ Estructura del Proyecto

```
SigepAdmin-IDAT/
├── manage.py
├── requirements.txt
├── README.md
├── FRONTEND_GUIDE.md
├── .venv/                          # Entorno virtual de Python
├── .gitignore
│
├── config/                         # ⚙️ Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings.py                 # Configuración principal
│   ├── urls.py                     # URLs principales del proyecto
│   ├── wsgi.py                     # Servidor WSGI
│   └── asgi.py                     # Servidor ASGI
│
├── control/                        # 📦 App Django - Control
│   ├── __init__.py
│   ├── admin.py                    # Configuración del admin
│   ├── apps.py                     # Configuración de la app
│   ├── models.py                   # Modelos de base de datos
│   ├── views.py                    # Vistas/controladores
│   ├── tests.py                    # Tests unitarios
│   ├── urls.py                     # URLs de la app (crear si no existe)
│   ├── forms.py                    # Formularios Django (crear si necesitas)
│   ├── locale/                     # Traducciones/localización
│   │   └── es/
│   │       └── formats.py
│   └── migrations/                 # Migraciones de base de datos
│       ├── __init__.py
│       ├── 0001_initial.py
│       ├── 0002_remove...py
│       └── 0003_aprobacion...py
│
├── static/                         # 🎨 ARCHIVOS ESTÁTICOS (CSS, JS, Imágenes)
│   ├── css/
│   │   ├── styles.css              # Estilos personalizados globales
│   │   ├── control.css             # Estilos específicos de la app control
│   │   └── forms.css               # Estilos para formularios
│   ├── js/
│   │   ├── main.js                 # JavaScript principal
│   │   ├── htmx-config.js          # Configuración y eventos de HTMX
│   │   ├── forms.js                # Validaciones y manejo de formularios
│   │   └── utils.js                # Funciones auxiliares reutilizables
│   └── images/
│       ├── logo.png                # Logo de la aplicación
│       ├── favicon.ico             # Icono del navegador
│       └── backgrounds/            # Imágenes de fondo (opcional)
│
├── media/                          # 📁 ARCHIVOS SUBIDOS POR USUARIOS
│   ├── .gitignore                  # Ignora archivos subidos en Git
│   ├── documents/                  # Documentos PDF, Word, etc.
│   ├── images/                     # Imágenes subidas por usuarios
│   └── uploads/                    # Otros archivos subidos
│
└── templates/                      # 📄 PLANTILLAS HTML
    ├── base.html                   # Template base (hereda todas las páginas)
    ├── index.html                  # Página principal/home
    │
    ├── components/                 # 🧩 COMPONENTES REUTILIZABLES
    │   ├── navbar.html             # Barra de navegación
    │   ├── footer.html             # Pie de página
    │   ├── sidebar.html            # Menú lateral (opcional)
    │   ├── breadcrumbs.html        # Migas de pan
    │   └── pagination.html         # Paginación de listas
    │
    ├── partials/                   # ⚡ FRAGMENTOS HTML PARA HTMX
    │   ├── loading.html            # Spinner de carga
    │   ├── form_errors.html        # Mensajes de error
    │   ├── success_message.html    # Mensajes de éxito
    │   ├── table_row.html          # Fila de tabla individual
    │   └── modal_content.html      # Contenido de modales
    │
    └── control/                    # 📋 TEMPLATES DE LA APP CONTROL
        ├── list.html               # Lista/tabla de registros
        ├── detail.html             # Vista detalle de un registro
        ├── form.html               # Formulario crear/editar
        ├── confirm_delete.html     # Confirmación de eliminación
        └── dashboard.html          # Dashboard de control (opcional)
```

---

## 🚀 Stack Tecnológico del Frontend

### Dependencias Instaladas (requirements.txt)

```python
Django==5.2.7                    # Framework web principal
django-bootstrap5==25.3          # ✅ Bootstrap 5 oficial para Django
django-htmx==1.26.0             # ✅ HTMX oficial para Django
django-cleanup==9.0.0           # Limpieza automática de archivos media
python-decouple==3.8            # Manejo de variables de entorno
```

---

## 📚 Guía de Desarrollo Frontend

### 1️⃣ **Configuración Inicial en `settings.py`**

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Paquetes de terceros
    'django_bootstrap5',      # ✅ Bootstrap 5
    'django_htmx',            # ✅ HTMX
    'django_cleanup',         # Limpieza de archivos media

    # Apps del proyecto
    'control',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',  # ✅ Middleware de HTMX
]

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuración de archivos media (subidos por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ Directorio de templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### 2️⃣ **Configuración de URLs para Media**

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('control/', include('control.urls')),  # URLs de la app control
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

---

## 🎨 **Uso de Bootstrap 5 con django-bootstrap5**

### Template Base (`templates/base.html`)

```html
{% load static %} {% load django_bootstrap5 %}
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}SigepAdmin IDAT{% endblock %}</title>

    {# Bootstrap CSS - Cargado por django-bootstrap5 #} {% bootstrap_css %} {#
    HTMX - Desde CDN #}
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    {# CSS Personalizado #}
    <link rel="stylesheet" href="{% static 'css/styles.css' %}" />

    {% block extra_css %}{% endblock %}
  </head>
  <body>
    {# Navbar #} {% include 'components/navbar.html' %} {# Mensajes de Django
    con Bootstrap #} {% if messages %}
    <div class="container mt-3">{% bootstrap_messages messages=messages %}</div>
    {% endif %} {# Contenido principal #}
    <main class="container my-4">{% block content %}{% endblock %}</main>

    {# Footer #} {% include 'components/footer.html' %} {# Bootstrap JavaScript
    Bundle #} {% bootstrap_javascript %} {# JavaScript Personalizado #}
    <script src="{% static 'js/main.js' %}"></script>

    {% block extra_js %}{% endblock %}
  </body>
</html>
```

### Renderizar Formularios con Bootstrap

```html
{# templates/control/form.html #} {% extends 'base.html' %} {% load
django_bootstrap5 %} {% block content %}
<div class="row justify-content-center">
  <div class="col-md-8">
    <div class="card">
      <div class="card-header">
        <h3>
          {% if form.instance.pk %}Editar{% else %}Crear{% endif %} Registro
        </h3>
      </div>
      <div class="card-body">
        <form method="post" enctype="multipart/form-data">
          {% csrf_token %} {# Renderiza el formulario completo con Bootstrap #}
          {% bootstrap_form form %} {# Botones con Bootstrap #} {%
          bootstrap_button button_type="submit" content="Guardar"
          button_class="btn-primary" %}
          <a href="{% url 'control:list' %}" class="btn btn-secondary"
            >Cancelar</a
          >
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## ⚡ **Uso de HTMX con django-htmx**

### En las Vistas (views.py)

```python
# control/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_htmx.http import HttpResponseClientRefresh
from .models import MiModelo

def lista_registros(request):
    """Vista principal con tabla completa"""
    registros = MiModelo.objects.all()

    # Si es una petición HTMX, solo devuelve el partial
    if request.htmx:
        return render(request, 'partials/table_rows.html', {'registros': registros})

    # Si es una petición normal, devuelve la página completa
    return render(request, 'control/list.html', {'registros': registros})

def eliminar_registro(request, pk):
    """Eliminar con HTMX sin recargar la página"""
    registro = get_object_or_404(MiModelo, pk=pk)

    if request.method == 'DELETE' or request.method == 'POST':
        registro.delete()

        # Si es HTMX, devuelve contenido vacío (la fila se eliminará del DOM)
        if request.htmx:
            return HttpResponse('')

        # Si no es HTMX, redirige
        return redirect('control:list')

    return render(request, 'control/confirm_delete.html', {'registro': registro})
```

### Templates con HTMX

```html
{# templates/control/list.html #} {% extends 'base.html' %} {% block content %}
<div class="card">
  <div class="card-header d-flex justify-content-between align-items-center">
    <h3>Lista de Registros</h3>
    <a href="{% url 'control:create' %}" class="btn btn-primary">Nuevo</a>
  </div>
  <div class="card-body">
    {# Buscador con HTMX #}
    <input
      type="search"
      name="search"
      placeholder="Buscar..."
      class="form-control mb-3"
      hx-get="{% url 'control:list' %}"
      hx-trigger="keyup changed delay:500ms"
      hx-target="#tabla-registros"
      hx-indicator="#loading"
    />

    {# Indicador de carga #}
    <div id="loading" class="htmx-indicator">
      {% include 'partials/loading.html' %}
    </div>

    {# Tabla que se actualiza con HTMX #}
    <div id="tabla-registros">{% include 'partials/table_rows.html' %}</div>
  </div>
</div>
{% endblock %}
```

```html
{# templates/partials/table_rows.html #}
<table class="table table-striped">
  <thead>
    <tr>
      <th>ID</th>
      <th>Nombre</th>
      <th>Fecha</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody>
    {% for registro in registros %}
    <tr id="row-{{ registro.id }}">
      <td>{{ registro.id }}</td>
      <td>{{ registro.nombre }}</td>
      <td>{{ registro.fecha }}</td>
      <td>
        <a
          href="{% url 'control:detail' registro.id %}"
          class="btn btn-sm btn-info"
          >Ver</a
        >
        <a
          href="{% url 'control:edit' registro.id %}"
          class="btn btn-sm btn-warning"
          >Editar</a
        >

        {# Eliminar con HTMX #}
        <button
          class="btn btn-sm btn-danger"
          hx-delete="{% url 'control:delete' registro.id %}"
          hx-target="#row-{{ registro.id }}"
          hx-swap="outerHTML"
          hx-confirm="¿Estás seguro de eliminar este registro?"
        >
          Eliminar
        </button>
      </td>
    </tr>
    {% empty %}
    <tr>
      <td colspan="4" class="text-center">No hay registros</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
```

### Eventos de HTMX en JavaScript

```javascript
// static/js/htmx-config.js

// Evento después de cargar contenido con HTMX
document.body.addEventListener("htmx:afterSwap", function (event) {
  console.log("Contenido actualizado con HTMX");

  // Reinicializar tooltips de Bootstrap si es necesario
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Evento antes de enviar una petición
document.body.addEventListener("htmx:beforeRequest", function (event) {
  console.log("Enviando petición HTMX...");
});

// Manejo de errores
document.body.addEventListener("htmx:responseError", function (event) {
  console.error("Error en petición HTMX:", event.detail);
  alert("Ocurrió un error. Por favor, intenta de nuevo.");
});
```

---

## 📂 **Manejo de Archivos Media**

### Modelo con Archivo (models.py)

```python
# control/models.py
from django.db import models

class Documento(models.Model):
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documents/%Y/%m/')  # Se guarda en media/documents/2025/11/
    imagen = models.ImageField(upload_to='images/', blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
```

### Mostrar Archivos en Templates

```html
{# templates/control/detail.html #} {% extends 'base.html' %} {% block content
%}
<div class="card">
  <div class="card-body">
    <h3>{{ documento.nombre }}</h3>

    {# Mostrar imagen si existe #} {% if documento.imagen %}
    <img
      src="{{ documento.imagen.url }}"
      alt="{{ documento.nombre }}"
      class="img-fluid mb-3"
    />
    {% endif %} {# Descargar archivo #} {% if documento.archivo %}
    <a href="{{ documento.archivo.url }}" class="btn btn-primary" download>
      Descargar Documento
    </a>
    {% endif %}
  </div>
</div>
{% endblock %}
```

---

## 🎯 **Flujo de Trabajo Completo**

### 1. **Página Normal (Sin HTMX)**

- Usuario accede → Django renderiza `base.html` + `control/list.html`
- Bootstrap da los estilos
- Página completa se carga

### 2. **Interacción con HTMX**

- Usuario busca/filtra → HTMX envía petición AJAX
- Django detecta `request.htmx` → devuelve solo `partials/table_rows.html`
- HTMX reemplaza solo la tabla (sin recargar página)
- Bootstrap mantiene los estilos

### 3. **Formularios**

- Django Forms + `django-bootstrap5` → formularios con estilos automáticos
- Validación en servidor → Django maneja errores
- Mostrar errores con `{% bootstrap_form %}`

### 4. **Archivos Media**

- Usuario sube archivo → Django guarda en `media/`
- `django-cleanup` elimina archivos antiguos automáticamente
- Templates acceden con `{{ object.archivo.url }}`

---

## ✅ **Checklist de Implementación**

- [ ] Configurar `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS` en settings.py
- [ ] Configurar `MEDIA_URL`, `MEDIA_ROOT` en settings.py
- [ ] Agregar `django_bootstrap5` y `django_htmx` a `INSTALLED_APPS`
- [ ] Agregar `HtmxMiddleware` a `MIDDLEWARE`
- [ ] Configurar URLs para servir archivos media en desarrollo
- [ ] Crear `base.html` con `{% bootstrap_css %}` y `{% bootstrap_javascript %}`
- [ ] Usar `{% bootstrap_form form %}` para renderizar formularios
- [ ] Detectar peticiones HTMX con `request.htmx` en las vistas
- [ ] Crear partials en `templates/partials/` para respuestas HTMX
- [ ] Usar atributos `hx-get`, `hx-post`, `hx-delete` en HTML
- [ ] Crear archivos CSS/JS personalizados en `static/`
- [ ] Configurar estructura de carpetas en `media/` para archivos subidos

---

## 🔗 **Recursos Útiles**

- [Documentación django-bootstrap5](https://django-bootstrap5.readthedocs.io/)
- [Documentación django-htmx](https://django-htmx.readthedocs.io/)
- [HTMX Official Docs](https://htmx.org/docs/)
- [Bootstrap 5 Docs](https://getbootstrap.com/docs/5.3/)

---

**¡Listo para desarrollar! 🚀**
