#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para mostrar información de últimos datos de datasets
"""

import streamlit as st
import pandas as pd


def mostrar_ultimos_datos(data_manager):
    """
    Muestra una alerta informativa con los últimos datos disponibles de cada dataset.
    
    Args:
        data_manager: Instancia de DataManager con los datasets cargados
    
    Nota:
        Los datasets deben estar ordenados de más reciente a más antiguo (excepto pisos que tiene sort)
    """
    
    # Obtener último RIPTE (primer registro ya que CSV está invertido)
    ripte_info = "N/A"
    if hasattr(data_manager, 'ripte_data') and not data_manager.ripte_data.empty:
        ultimo_ripte = data_manager.ripte_data.iloc[0]
        fecha_ripte = ultimo_ripte['fecha']
        valor_ripte = ultimo_ripte['ripte']
        ripte_info = f"**RIPTE** {fecha_ripte.month}/{fecha_ripte.year}: {valor_ripte:,.2f}"
    
    # Obtener último IPC
    ipc_info = "N/A"
    if hasattr(data_manager, 'ipc_data') and not data_manager.ipc_data.empty:
        ultimo_ipc = data_manager.ipc_data.iloc[0]
        fecha_ipc = ultimo_ipc['fecha']
        valor_ipc = ultimo_ipc['ipc']
        ipc_info = f"**IPC** {fecha_ipc.month}/{fecha_ipc.year}: {valor_ipc:.2f}%"
    
    # Obtener última Tasa Activa
    tasa_info = "N/A"
    if hasattr(data_manager, 'tasa_data') and not data_manager.tasa_data.empty:
        ultima_tasa = data_manager.tasa_data.iloc[0]
        fecha_tasa = ultima_tasa['desde']
        valor_tasa = ultima_tasa['tasa']
        tasa_info = f"**TASA ACTIVA** {fecha_tasa.day}/{fecha_tasa.month}/{fecha_tasa.year}: {valor_tasa:.2f}%"
    
    # Obtener último Piso SRT
    piso_info = "N/A"
    if hasattr(data_manager, 'pisos_data') and not data_manager.pisos_data.empty:
        # Pisos tiene sort, así que el último es el más reciente
        ultimo_piso = data_manager.pisos_data.iloc[-1]
        norma = ultimo_piso['resol']
        desde = ultimo_piso['desde']
        hasta = ultimo_piso['hasta']
        monto = ultimo_piso['piso']
        
        if pd.isna(hasta):
            periodo = f"{desde.strftime('%d/%m/%Y')} - Vigente"
        else:
            periodo = f"{desde.strftime('%d/%m/%Y')} al {hasta.strftime('%d/%m/%Y')}"
        
        piso_info = f"**PISO SRT** {norma} ({periodo}): $ {monto:,.2f}"
    
    # Mostrar alerta informativa
    st.success(f"""
    📊 **Últimos Datos Disponibles:**  
    {ripte_info} | {ipc_info} | {tasa_info}  
    {piso_info}
    """)


def mostrar_ultimos_datos_jus(data_manager):
    """
    Muestra una alerta informativa con los últimos datos de JUS.
    
    Args:
        data_manager: Instancia de DataManager con el dataset JUS cargado
    """
    
    # Obtener último JUS (primer registro ya que CSV está invertido)
    jus_info = "N/A"
    if hasattr(data_manager, 'jus_data') and not data_manager.jus_data.empty:
        ultimo_jus = data_manager.jus_data.iloc[0]
        fecha_jus = ultimo_jus['fecha']
        valor_jus = ultimo_jus['valor']
        acuerdo = ultimo_jus.get('acuerdo', 'N/A')
        jus_info = f"**JUS** {fecha_jus.month}/{fecha_jus.year}: $ {valor_jus:,.2f} ({acuerdo})"
    
    # Mostrar alerta informativa
    st.success(f"""
    📊 **Últimos Datos Disponibles:**  
    {jus_info}
    """)


def mostrar_ultimos_datos_completo():
    """
    Muestra alerta con todos los últimos datos disponibles.
    Versión completa usada en main.py con colores y formato detallado.
    """
    try:
        from utils.data_loader import get_ultimo_dato
        
        # Cargar datasets
        df_ripte = pd.read_csv("data/dataset_ripte.csv", encoding='utf-8')
        
        df_ipc = pd.read_csv("data/dataset_ipc.csv", encoding='utf-8')
        df_ipc['periodo'] = pd.to_datetime(df_ipc['periodo'])
        
        df_tasa = pd.read_csv("data/dataset_tasa.csv", encoding='utf-8')
        df_tasa['Desde'] = pd.to_datetime(df_tasa['Desde'])
        df_tasa['Hasta'] = pd.to_datetime(df_tasa['Hasta'])
        
        df_jus = pd.read_csv("data/Dataset_JUS.csv", encoding='utf-8')
        
        df_pisos = pd.read_csv("data/dataset_pisos.csv", encoding='utf-8')
        
        # Obtener últimos datos con colores
        textos_datos = []
        
        # RIPTE - Color azul
        if not df_ripte.empty:
            ultimo_ripte = get_ultimo_dato(df_ripte)
            
            # Usar directamente año y mes del dataframe
            año_ripte = ultimo_ripte['año']
            mes_texto = ultimo_ripte['mes']
            
            # Mapear mes texto a número
            meses_map = {
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
                'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
                'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12,
                'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4,
                'May': 5, 'Jun': 6, 'Jul': 7, 'Ago': 8,
                'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
            }
            
            mes_ripte = meses_map.get(mes_texto[:3], mes_texto) if isinstance(mes_texto, str) else mes_texto
            
            # Intentar diferentes nombres de columna para el valor
            try:
                valor_ripte = ultimo_ripte['índice RIPTE']
            except:
                try:
                    valor_ripte = ultimo_ripte['indice_ripte']
                except:
                    valor_ripte = ultimo_ripte.iloc[2]  # Tercera columna
            
            textos_datos.append(f'<span style="color: #1f77b4; font-weight: 600;">RIPTE {mes_ripte}/{año_ripte}: {valor_ripte:,.0f}</span>')
        
        # IPC - Color verde
        if not df_ipc.empty:
            ultimo_ipc = get_ultimo_dato(df_ipc)
            fecha_ipc = ultimo_ipc['periodo']
            variacion_ipc = ultimo_ipc['variacion_mensual']
            mes_ipc = fecha_ipc.month
            año_ipc = fecha_ipc.year
            textos_datos.append(f'<span style="color: #2ca02c; font-weight: 600;">IPC {mes_ipc}/{año_ipc}: {variacion_ipc:.2f}%</span>')
        
        # TASA - Color naranja
        if not df_tasa.empty:
            ultima_tasa = get_ultimo_dato(df_tasa)
            valor_tasa = ultima_tasa['Valor']
            fecha_hasta = ultima_tasa['Hasta']
            fecha_txt = fecha_hasta.strftime("%d/%m/%Y")
            textos_datos.append(f'<span style="color: #ff7f0e; font-weight: 600;">TASA {fecha_txt}: {valor_tasa:.2f}%</span>')
        
        # JUS - Color morado
        try:
            ultimo_jus = get_ultimo_dato(df_jus)
            fecha_jus = ultimo_jus['FECHA ENTRADA EN VIGENCIA '].strip() if isinstance(ultimo_jus['FECHA ENTRADA EN VIGENCIA '], str) else ultimo_jus['FECHA ENTRADA EN VIGENCIA ']
            valor_jus_str = ultimo_jus['VALOR IUS'].strip()
            acuerdo_jus = ultimo_jus['ACUERDO'].strip()
            
            # Limpiar valor (quitar $ y espacios, convertir a float)
            valor_jus = float(valor_jus_str.replace('$', '').replace('.', '').replace(',', '.').strip())
            
            # Simplificar acuerdo (solo número)
            acuerdo_num = acuerdo_jus.replace('Acuerdo ', '').replace('acuerdo ', '')
            
            textos_datos.append(f'<span style="color: #9467bd; font-weight: 600;">JUS {fecha_jus} - Ac.{acuerdo_num}: ${valor_jus:,.2f}</span>')
        except Exception as e_jus:
            pass
        
        # PISOS - Color rojo
        try:
            ultimo_piso = get_ultimo_dato(df_pisos)
            fecha_inicio = ultimo_piso['fecha_inicio']
            norma_piso = ultimo_piso['norma']
            monto_piso = float(ultimo_piso['monto_minimo'])
            
            textos_datos.append(f'<span style="color: #d62728; font-weight: 600;">PISO desde {fecha_inicio} - {norma_piso}: ${monto_piso:,.2f}</span>')
        except Exception as e_piso:
            pass
        
        # Mostrar alerta solo si hay datos - con fondo crema suave
        if textos_datos:
            st.markdown(f"""
                <div style='background-color: #fffef0; padding: 1rem; border-radius: 8px; border-left: 4px solid #f0ad4e; margin-bottom: 1.5rem; margin-top: 2rem;'>
                    <p style='margin: 0; font-size: 0.95rem;'>
                        <strong style='color: #856404;'>📊 Últimos Datos Disponibles:</strong><br>
                        {' <span style="color: #ccc;">|</span> '.join(textos_datos)}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        # No mostrar error, simplemente omitir la alerta
        pass