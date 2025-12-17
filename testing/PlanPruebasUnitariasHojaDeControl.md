| | | | |
| :--- | :--- | :--- | :--- |
| **Organismo** | Instituto de Educación Superior Tecnológico IDAT | | |
| **Proyecto** | SigepAdmin - Sistema de Gestión Portuaria | | |
| **Entregable** | Plan de Pruebas Unitarias | | |
| **Autor** | Equipo de Desarrollo SigepAdmin | | |
| **Versión / Edición** | 0100 | **Fecha Versión** | 13/12/2024 |
| **Aprobado Por** | | **Fecha Aprobación** | DD/MM/AAAA |
| | | **Nº Total de Páginas** | 4 |

<br>

### REGISTRO DE CAMBIOS

| Versión | Causa del cambio | Responsable del cambio | Fecha del cambio |
| :---: | :--- | :--- | :---: |
| 0100 | Versión Inicial - Suite de pruebas unitarias implementada | Equipo de Desarrollo | 13/12/2024 |
| | | | |

<br>

### CONTROL DE DISTRIBUCIÓN

| Nombre y Apellidos |
| :--- |
| Profesor del curso Pruebas de Calidad de Software |
| Equipo de Desarrollo IDAT |
| <br> |

<br>

---

## RESUMEN DE EJECUCIÓN DE PRUEBAS

| Métrica | Valor |
| :--- | :---: |
| **Total de Casos de Prueba** | 37 |
| **Pruebas Exitosas (OK)** | 37 |
| **Pruebas Fallidas (FAIL)** | 0 |
| **Porcentaje de Éxito** | 100% |
| **Fecha de Ejecución** | 13/12/2024 |
| **Framework Utilizado** | django.test (unittest) |

<br>

### Comando de Ejecución

```bash
python manage.py test control.tests
```

### Resultado de Ejecución

```
Found 37 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....................................
----------------------------------------------------------------------
Ran 37 tests in 10.889s

OK
Destroying test database for alias 'default'...
```

<br>

---

## ARCHIVOS DE PRUEBAS CREADOS

| Archivo | Tipo | Tests | Casos de Prueba |
| :--- | :--- | :---: | :--- |
| `control/tests/test_validators.py` | Unitaria | 9 | CP-001, CP-004 |
| `control/tests/test_models.py` | Unitaria | 14 | CP-002, CP-003, CP-010, CP-011, CP-012 |
| `control/tests/test_events.py` | Unitaria | 3 | CP-009 |
| `control/tests/test_views.py` | Aceptación | 6 | CP-005, CP-006, CP-007 |
| `control/tests/test_permissions.py` | Aceptación | 5 | CP-013 |