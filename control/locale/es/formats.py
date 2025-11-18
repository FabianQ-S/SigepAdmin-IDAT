# -*- coding: utf-8 -*-
"""
Formato de fecha personalizado para admin en español
"""

# Django usa estos formatos cuando LANGUAGE_CODE = 'es'
# Automáticamente muestra fechas como: 17/11/2025

DATE_FORMAT = 'd/m/Y'                # 17/11/2025
DATETIME_FORMAT = 'd/m/Y H:i'        # 17/11/2025 14:30
SHORT_DATE_FORMAT = 'd/m/Y'          # 17/11/2025
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'  # 17/11/2025 14:30

# Formatos de entrada para formularios
DATE_INPUT_FORMATS = [
    '%d/%m/%Y',    # 17/11/2025
    '%d/%m/%y',    # 17/11/25
    '%Y-%m-%d',    # 2025-11-17
]

DATETIME_INPUT_FORMATS = [
    '%d/%m/%Y %H:%M:%S',
    '%d/%m/%Y %H:%M',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
]

