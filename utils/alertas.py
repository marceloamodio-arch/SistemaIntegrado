import streamlit as st
from utils.data_loader import DataLoader
from datetime import datetime

def mostrar_alerta_ultimos_datos():
    """Muestra alerta con últimos datos de TODOS los datasets - Estilo moderno sin flechas"""
    try:
        dl = DataLoader()

        # Cargar todos los datasets
        df_ripte = dl.cargar_dataset("ripte")
        df_ipc = dl.cargar_dataset("ipc")
        df_tasa = dl.cargar_dataset("tasa")
        df_jus = dl.cargar_dataset("jus")
        df_pisos = dl.cargar_dataset("pisos")

        # Obtener último dato de cada uno
        ult_ripte = dl.get_ultimo_dato(df_ripte)
        ult_ipc = dl.get_ultimo_dato(df_ipc)
        ult_tasa = dl.get_ultimo_dato(df_tasa)
        ult_jus = dl.get_ultimo_dato(df_jus)
        ult_pisos = dl.get_ultimo_dato(df_pisos)

        # Formatear fecha de tasa activa a DD/MM/AAAA
        try:
            fecha_tasa = datetime.strptime(ult_tasa['Desde'], '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            fecha_tasa = ult_tasa['Desde']

        # Título con divider
        st.subheader("📊 Últimos Datos del Sistema", divider="blue")
        
        # Crear 5 columnas para los 5 datasets
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="RIPTE",
                value=f"{ult_ripte['indice_ripte']:,.2f}",
                delta=None  # Sin flecha verde
            )
            st.caption(f"💰 ${ult_ripte['monto_en_pesos']:,.2f}")
            st.caption(f"📅 {ult_ripte['mes']} {ult_ripte['año']}")
        
        with col2:
            st.metric(
                label="IPC",
                value=f"{ult_ipc['variacion_mensual']}%",
                delta=None
            )
            st.caption(f"📅 {ult_ipc['periodo']}")
        
        with col3:
            st.metric(
                label="Tasa Activa",
                value=f"{ult_tasa['Valor']}%",
                delta=None
            )
            st.caption(f"📅 {fecha_tasa}")
        
        with col4:
            jus_valor = float(ult_jus['VALOR IUS'].replace('$', '').replace('.', '').replace(',', '.').strip())
            st.metric(
                label="JUS",
                value=f"${jus_valor:,.2f}",
                delta=None
            )
            st.caption(f"📄 {ult_jus['ACUERDO']}")
            st.caption(f"📅 {ult_jus['FECHA ENTRADA EN VIGENCIA '].strip()}")
        
        with col5:
            st.metric(
                label="Pisos Salariales",
                value=f"${float(ult_pisos['monto_minimo']):,.2f}",
                delta=None
            )
            st.caption(f"📋 {ult_pisos['norma']}")
            st.caption(f"📅 {ult_pisos['fecha_inicio']} - {ult_pisos['fecha_fin']}")

    except Exception as e:
        st.error(f"⚠️ Error al cargar últimos datos: {str(e)}")
