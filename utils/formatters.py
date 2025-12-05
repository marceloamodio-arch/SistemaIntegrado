#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO DE FORMATEO Y UTILIDADES COMPARTIDAS
Sistema de Cálculos y Herramientas - Tribunal de Trabajo 2 de Quilmes

Este módulo centraliza todas las funciones de formateo y utilidades
que son compartidas entre múltiples aplicaciones del sistema.

Funciones disponibles:
- formato_moneda: Formatea números como moneda argentina
- safe_parse_date: Parser robusto de fechas
- numero_a_letras: Convierte números a texto en español
- days_in_month: Calcula días en un mes
- redondear_decimal: Redondeo con ROUND_HALF_UP (legal)
"""

import pandas as pd
import math
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


def formato_moneda(valor) -> str:
    """
    Formatea números como moneda argentina.
    
    Args:
        valor: Número a formatear (int, float, Decimal)
    
    Returns:
        String con formato: "$ 1.234.567,89"
    
    Ejemplos:
        >>> formato_moneda(1234567.89)
        '$ 1.234.567,89'
        >>> formato_moneda(0)
        '$ 0,00'
        >>> formato_moneda(None)
        '$ 0,00'
    """
    try:
        return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "$ 0,00"


def safe_parse_date(s) -> Optional[date]:
    """
    Parser robusto de fechas que maneja múltiples formatos.
    
    Formatos soportados:
    - ISO: 2024-12-31, 2024-12-31 00:00:00
    - Argentino: 31/12/2024, 31-12-2024
    - Mes/Año: 12/2024, 2024-12, Diciembre 2024
    - Objetos datetime/date
    - Timestamps de pandas
    
    Args:
        s: Fecha en cualquier formato (str, datetime, date, None)
    
    Returns:
        date object o None si no se puede parsear
    
    Ejemplos:
        >>> safe_parse_date("31/12/2024")
        date(2024, 12, 31)
        >>> safe_parse_date("2024-12-31")
        date(2024, 12, 31)
        >>> safe_parse_date("12/2024")
        date(2024, 12, 1)
        >>> safe_parse_date(None)
        None
    """
    # Manejar None y NaN
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return None
    
    # Si ya es date o datetime, convertir
    if isinstance(s, (datetime, date)):
        return s.date() if isinstance(s, datetime) else s
    
    # Convertir a string y limpiar
    s = str(s).strip()
    if not s:
        return None
    
    # Intentar formatos estándar
    fmts = [
        "%Y-%m-%d",           # ISO: 2024-12-31
        "%d/%m/%Y",           # AR: 31/12/2024
        "%d-%m-%Y",           # AR con guión: 31-12-2024
        "%m/%Y",              # Mes/Año: 12/2024
        "%Y/%m/%d",           # Año primero con /
        "%Y-%m",              # Año-Mes: 2024-12
        "%Y-%m-%d %H:%M:%S",  # ISO con hora
        "%d/%m/%Y %H:%M:%S",  # AR con hora
        "%B %Y",              # Diciembre 2024
        "%b %Y",              # Dic 2024
        "%Y/%m",              # 2024/12
        "%m-%Y",              # 12-2024
    ]
    
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            # Para formatos mes/año, retornar primer día del mes
            if f in ("%m/%Y", "%Y-%m", "%Y/%m", "%m-%Y", "%B %Y", "%b %Y"):
                return date(dt.year, dt.month, 1)
            return dt.date()
        except Exception:
            continue
    
    # Intentar parsear mes/año manualmente
    if "/" in s or "-" in s:
        parts = s.replace("/", "-").split("-")
        if len(parts) == 2:
            try:
                year, month = int(parts[0]), int(parts[1])
                if 1900 <= year <= 2100 and 1 <= month <= 12:
                    return date(year, month, 1)
            except ValueError:
                pass
    
    # Último intento con pandas
    try:
        dt = pd.to_datetime(s, dayfirst=True, errors="coerce")
        if pd.isna(dt):
            return None
        if isinstance(dt, pd.Timestamp):
            return dt.date()
        return None
    except Exception:
        return None


def numero_a_letras(numero: float) -> str:
    """
    Convierte un número a su representación en letras (pesos argentinos).
    
    Args:
        numero: Número a convertir (admite decimales)
    
    Returns:
        String con el número en letras, formato: "PESOS ... CON XX/100"
    
    Ejemplos:
        >>> numero_a_letras(1234.56)
        'PESOS UN MIL DOSCIENTOS TREINTA Y CUATRO CON 56/100'
        >>> numero_a_letras(0)
        'CERO PESOS'
        >>> numero_a_letras(1000000)
        'PESOS UN MILLÓN CON 00/100'
    """
    unidades = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
    decenas = ['', '', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
    especiales = ['DIEZ', 'ONCE', 'DOCE', 'TRECE', 'CATORCE', 'QUINCE', 'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO', 'DIECINUEVE']
    centenas = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS']
    
    def convertir_grupo(n):
        """Convierte un número de 0-999 a letras"""
        if n == 0:
            return ''
        elif n == 100:
            return 'CIEN'
        elif n < 10:
            return unidades[n]
        elif n < 20:
            return especiales[n - 10]
        elif n < 100:
            dec = n // 10
            uni = n % 10
            if uni == 0:
                return decenas[dec]
            else:
                return decenas[dec] + (' Y ' if dec > 2 else 'I') + unidades[uni]
        else:
            cen = n // 100
            resto = n % 100
            if resto == 0:
                return centenas[cen]
            else:
                return centenas[cen] + ' ' + convertir_grupo(resto)
    
    if numero == 0:
        return 'CERO PESOS'
    
    entero = int(numero)
    decimal = int(round((numero - entero) * 100))
    
    # Manejar miles de millones
    if entero >= 1000000000:
        miles_millon = entero // 1000000000
        resto = entero % 1000000000
        texto = convertir_grupo(miles_millon) + ' MIL'
        if resto >= 1000000:
            millones = resto // 1000000
            resto = resto % 1000000
            texto += ' ' + (convertir_grupo(millones) if millones > 1 else 'UN') + ' MILLÓN' + ('ES' if millones > 1 else '')
        if resto > 0:
            if resto >= 1000:
                miles = resto // 1000
                resto = resto % 1000
                texto += ' ' + convertir_grupo(miles) + ' MIL'
            if resto > 0:
                texto += ' ' + convertir_grupo(resto)
    # Manejar millones
    elif entero >= 1000000:
        millones = entero // 1000000
        resto = entero % 1000000
        texto = (convertir_grupo(millones) if millones > 1 else 'UN') + ' MILLÓN' + ('ES' if millones > 1 else '')
        if resto > 0:
            if resto >= 1000:
                miles = resto // 1000
                resto = resto % 1000
                texto += ' ' + convertir_grupo(miles) + ' MIL'
            if resto > 0:
                texto += ' ' + convertir_grupo(resto)
    # Manejar miles
    elif entero >= 1000:
        miles = entero // 1000
        resto = entero % 1000
        texto = convertir_grupo(miles) + ' MIL'
        if resto > 0:
            texto += ' ' + convertir_grupo(resto)
    # Menores a mil
    else:
        texto = convertir_grupo(entero)
    
    return f'PESOS {texto} CON {decimal:02d}/100'


def days_in_month(d: date) -> int:
    """
    Calcula la cantidad de días en un mes dado.
    
    Args:
        d: Fecha de la cual extraer el mes
    
    Returns:
        Cantidad de días en el mes (28-31)
    
    Ejemplos:
        >>> days_in_month(date(2024, 2, 15))
        29  # Año bisiesto
        >>> days_in_month(date(2023, 2, 15))
        28
        >>> days_in_month(date(2024, 12, 1))
        31
    """
    if d.month == 12:
        nxt = date(d.year + 1, 1, 1)
    else:
        nxt = date(d.year, d.month + 1, 1)
    return (nxt - date(d.year, d.month, 1)).days


def redondear_decimal(valor, decimales: int = 2) -> float:
    """
    Redondeo con ROUND_HALF_UP para cumplimiento legal.
    
    Este método de redondeo es requerido para cálculos contables
    y legales en Argentina, ya que garantiza reproducibilidad
    en peritajes judiciales.
    
    Args:
        valor: Número a redondear
        decimales: Cantidad de decimales (default: 2)
    
    Returns:
        Número redondeado como float
    
    Ejemplos:
        >>> redondear_decimal(1.235, 2)
        1.24
        >>> redondear_decimal(1.234, 2)
        1.23
        >>> redondear_decimal(1234.567, 0)
        1235.0
    
    Nota:
        ROUND_HALF_UP: 0.5 redondea hacia arriba (no hacia el par más cercano)
        Ejemplo: 2.5 → 3.0 (no 2.0)
    """
    d = Decimal(str(valor))
    return float(d.quantize(Decimal(10) ** -decimales, rounding=ROUND_HALF_UP))


# Funciones auxiliares adicionales

def limpiar_valor_monetario(valor_str: str) -> float:
    """
    Limpia un string monetario y lo convierte a float.
    
    Args:
        valor_str: String con formato monetario (ej: "$ 1.234,56" o "$1234.56")
    
    Returns:
        Valor como float
    
    Ejemplos:
        >>> limpiar_valor_monetario("$ 1.234,56")
        1234.56
        >>> limpiar_valor_monetario("$1234.56")
        1234.56
        >>> limpiar_valor_monetario("1.234,56")
        1234.56
    """
    try:
        # Quitar símbolos y espacios
        limpio = valor_str.replace('$', '').replace(' ', '').strip()
        
        # Detectar si usa coma como decimal (formato argentino)
        if ',' in limpio and '.' in limpio:
            # Formato argentino: 1.234,56
            limpio = limpio.replace('.', '').replace(',', '.')
        elif ',' in limpio:
            # Solo coma: 1234,56
            limpio = limpio.replace(',', '.')
        
        return float(limpio)
    except:
        return 0.0


def formato_porcentaje(valor: float, decimales: int = 2) -> str:
    """
    Formatea un número como porcentaje.
    
    Args:
        valor: Número a formatear (ej: 0.15 para 15%)
        decimales: Cantidad de decimales a mostrar
    
    Returns:
        String con formato de porcentaje
    
    Ejemplos:
        >>> formato_porcentaje(0.15)
        '15,00%'
        >>> formato_porcentaje(0.1567, 3)
        '15,670%'
    """
    try:
        porcentaje = valor * 100
        return f"{porcentaje:.{decimales}f}%".replace(".", ",")
    except:
        return "0,00%"


# Diccionario de meses en español
MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

MESES_ES_CORTO = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


def formato_fecha_argentina(fecha: date, formato: str = "largo") -> str:
    """
    Formatea una fecha en formato argentino.
    
    Args:
        fecha: Fecha a formatear
        formato: "largo" (31/12/2024), "corto" (31/12/24), "texto" (31 de Diciembre de 2024)
    
    Returns:
        String con fecha formateada
    
    Ejemplos:
        >>> formato_fecha_argentina(date(2024, 12, 31), "largo")
        '31/12/2024'
        >>> formato_fecha_argentina(date(2024, 12, 31), "texto")
        '31 de Diciembre de 2024'
    """
    if formato == "corto":
        return fecha.strftime("%d/%m/%y")
    elif formato == "texto":
        mes_nombre = MESES_ES[fecha.month]
        return f"{fecha.day} de {mes_nombre} de {fecha.year}"
    else:  # largo (default)
        return fecha.strftime("%d/%m/%Y")


if __name__ == "__main__":
    # Tests básicos
    print("=== Tests de formatters.py ===")
    print(f"formato_moneda(1234567.89): {formato_moneda(1234567.89)}")
    print(f"safe_parse_date('31/12/2024'): {safe_parse_date('31/12/2024')}")
    print(f"numero_a_letras(1234.56): {numero_a_letras(1234.56)}")
    print(f"days_in_month(date(2024, 2, 1)): {days_in_month(date(2024, 2, 1))}")
    print(f"redondear_decimal(1.235, 2): {redondear_decimal(1.235, 2)}")
    print(f"formato_porcentaje(0.1567): {formato_porcentaje(0.1567)}")
    print(f"formato_fecha_argentina(date(2024, 12, 31)): {formato_fecha_argentina(date(2024, 12, 31))}")
