"""
Utilidades compartidas del Sistema de Cálculos y Herramientas
Tribunal de Trabajo 2 de Quilmes
"""

from .data_loader import (
    DataLoader,
    cargar_dataset_jus,
    cargar_dataset_ipc,
    cargar_dataset_pisos,
    cargar_dataset_ripte,
    cargar_dataset_tasa,
    get_ultimo_dato
)

from .auth import AuthSystem
from .simple_session import SimpleSessionManager
from .navegacion import mostrar_sidebar_navegacion

from .formatters import (
    formato_moneda,
    safe_parse_date,
    numero_a_letras,
    days_in_month,
    redondear_decimal,
    limpiar_valor_monetario,
    formato_porcentaje,
    formato_fecha_argentina,
    MESES_ES,
    MESES_ES_CORTO
)

__all__ = [
    'DataLoader',
    'cargar_dataset_jus',
    'cargar_dataset_ipc',
    'cargar_dataset_pisos',
    'cargar_dataset_ripte',
    'cargar_dataset_tasa',
    'get_ultimo_dato',
    'AuthSystem',
    'SimpleSessionManager',
    'mostrar_sidebar_navegacion',
    'formato_moneda',
    'safe_parse_date',
    'numero_a_letras',
    'days_in_month',
    'redondear_decimal',
    'limpiar_valor_monetario',
    'formato_porcentaje',
    'formato_fecha_argentina',
    'MESES_ES',
    'MESES_ES_CORTO'
]