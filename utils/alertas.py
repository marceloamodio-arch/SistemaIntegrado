
import streamlit as st
from utils.data_loader import DataLoader

def mostrar_alerta_ultimos_datos():
    try:
        dl = DataLoader()

        df_ripte = dl.cargar_dataset("ripte")
        df_ipc = dl.cargar_dataset("ipc")
        df_tasa = dl.cargar_dataset("tasa")
        df_jus = dl.cargar_dataset("jus")

        ult_ripte = dl.get_ultimo_dato(df_ripte)
        ult_ipc   = dl.get_ultimo_dato(df_ipc)
        ult_tasa  = dl.get_ultimo_dato(df_tasa)
        ult_jus   = dl.get_ultimo_dato(df_jus)

        html = f"""
        <div style='margin-top:45px; background:#E6ECF2; padding:14px 18px;
                    border-left:5px solid #2A4C7C; border-radius:6px;
                    font-size:0.92rem;'>
            <strong>Últimos datos disponibles</strong><br>
            • RIPTE: {ult_ripte['Valor']} ({ult_ripte['Fecha']})<br>
            • IPC: {ult_ipc['Valor']} ({ult_ipc['Mes']})<br>
            • Tasa Activa: {ult_tasa['Valor']} ({ult_tasa['Fecha']})<br>
            • JUS: {ult_jus['Valor']} ({ult_jus['Fecha']})<br>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"<div style='margin-top:20px; color:#7A0000;'>⚠️ Error al cargar últimos datos: {e}</div>",
                    unsafe_allow_html=True)
