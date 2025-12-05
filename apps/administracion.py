#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APP DE ADMINISTRACIÓN
Sistema de Cálculos y Herramientas - Tribunal de Trabajo 2 de Quilmes
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem

# Inicializar sistema de autenticación
auth = AuthSystem()

st.markdown("# ⚙️ ADMINISTRACIÓN DEL SISTEMA")
st.markdown("---")

# Tabs para las diferentes funciones
tab1, tab2 = st.tabs(["👥 Gestión de Usuarios", "📊 Edición de Datasets"])

# TAB 1: GESTIÓN DE USUARIOS
with tab1:
    st.markdown("## 👥 Gestión de Usuarios")
    
    subtab1, subtab2, subtab3 = st.tabs(["Crear Usuario", "Ver Usuarios", "Modificar"])
    
    with subtab1:
        st.markdown("### ➕ Crear Nuevo Usuario")
        
        with st.form("form_crear_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_username = st.text_input("Nombre de usuario*", max_chars=50)
                nuevo_nombre = st.text_input("Nombre completo", max_chars=100)
            
            with col2:
                nuevo_password = st.text_input("Contraseña*", type="password", max_chars=50)
                nuevo_email = st.text_input("Email", max_chars=100)
            
            nuevo_nivel = st.selectbox("Nivel de acceso*", ["normal", "admin"])
            
            submitted = st.form_submit_button("Crear Usuario", use_container_width=True, type="primary")
            
            if submitted:
                if not nuevo_username or not nuevo_password:
                    st.error("Usuario y contraseña son obligatorios")
                else:
                    exito, mensaje = auth.crear_usuario(
                        username=nuevo_username,
                        password=nuevo_password,
                        nivel=nuevo_nivel,
                        nombre_completo=nuevo_nombre,
                        email=nuevo_email
                    )
                    
                    if exito:
                        st.success(mensaje)
                    else:
                        st.error(mensaje)
    
    with subtab2:
        st.markdown("### 📋 Usuarios del Sistema")
        
        usuarios = auth.obtener_usuarios()
        
        if usuarios:
            df_usuarios = pd.DataFrame(usuarios)
            df_display = df_usuarios[['username', 'nivel', 'nombre_completo', 'email', 'ultimo_acceso', 'activo']].copy()
            df_display.columns = ['Usuario', 'Nivel', 'Nombre', 'Email', 'Último Acceso', 'Activo']
            df_display['Activo'] = df_display['Activo'].map({True: '✅', False: '❌'})
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption(f"Total de usuarios: {len(usuarios)}")
        else:
            st.info("No hay usuarios en el sistema")
    
    with subtab3:
        st.markdown("### ✏️ Modificar Usuario")
        
        usuarios = auth.obtener_usuarios()
        usernames = [u['username'] for u in usuarios]
        
        usuario_sel = st.selectbox("Seleccionar usuario", usernames)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔑 Cambiar Contraseña")
            with st.form("form_cambiar_pass"):
                nueva_pass = st.text_input("Nueva contraseña", type="password")
                confirmar_pass = st.text_input("Confirmar contraseña", type="password")
                
                if st.form_submit_button("Cambiar Contraseña"):
                    if nueva_pass != confirmar_pass:
                        st.error("Las contraseñas no coinciden")
                    elif nueva_pass:
                        exito, mensaje = auth.cambiar_password(usuario_sel, nueva_pass)
                        if exito:
                            st.success(mensaje)
                        else:
                            st.error(mensaje)
        
        with col2:
            st.markdown("#### 🗑️ Eliminar Usuario")
            st.warning(f"¿Eliminar usuario **{usuario_sel}**?")
            
            if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                exito, mensaje = auth.eliminar_usuario(usuario_sel)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

# TAB 2: EDICIÓN DE DATASETS
with tab2:
    st.markdown("## 📊 Edición de Datasets")
    
    datasets = {
        "JUS": "data/Dataset_JUS.csv",
        "IPC": "data/dataset_ipc.csv",
        "RIPTE": "data/dataset_ripte.csv",
        "Pisos Salariales": "data/dataset_pisos.csv",
        "Tasa Activa": "data/dataset_tasa.csv"
    }
    
    dataset_sel = st.selectbox("Seleccionar dataset", list(datasets.keys()))
    archivo = datasets[dataset_sel]
    
    try:
        df = pd.read_csv(archivo, encoding='utf-8')
        
        st.markdown(f"### 📄 {dataset_sel}")
        st.caption(f"📁 `{archivo}` • 📊 {len(df)} filas • 📋 {len(df.columns)} columnas")
        
        st.markdown("---")
              
        # Sistema de edición custom
        st.markdown("#### ✏️ Editor de Datos")
        
        # CSS para compactar filas
        st.markdown("""
        <style>
        /* Compactar contenedores */
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="column"]) {
            gap: 0.25rem !important;
            margin-bottom: 0.25rem !important;
        }
        
        /* Compactar inputs de texto */
        div[data-testid="stTextInput"] > div {
            margin-bottom: 0 !important;
        }
        
        div[data-testid="stTextInput"] input {
            padding: 0.25rem 0.5rem !important;
            height: 2rem !important;
            font-size: 0.85rem !important;
        }
        
        /* Compactar botones */
        button[kind="secondary"], button[kind="primary"] {
            padding: 0.25rem 0.5rem !important;
            min-height: 2rem !important;
            height: 2rem !important;
            font-size: 0.85rem !important;
        }
        
        /* Compactar separadores */
        hr {
            margin: 0.25rem 0 !important;
        }
        
        /* Compactar texto de filas */
        .compact-text {
            padding: 0.25rem 0.5rem;
            font-size: 0.85rem;
            line-height: 1.5;
            margin: 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Inicializar estado si no existe
        if f'df_edit_{dataset_sel}' not in st.session_state:
            st.session_state[f'df_edit_{dataset_sel}'] = df.copy()
        
        if f'editing_row_{dataset_sel}' not in st.session_state:
            st.session_state[f'editing_row_{dataset_sel}'] = None
        
        # Estado de paginación
        if f'rows_visible_{dataset_sel}' not in st.session_state:
            st.session_state[f'rows_visible_{dataset_sel}'] = 10  # Mostrar 10 inicialmente
        
        df_trabajo = st.session_state[f'df_edit_{dataset_sel}']
        rows_visible = st.session_state[f'rows_visible_{dataset_sel}']
        
        # Botón para agregar nueva fila - Pequeño a la izquierda
        col_btn_agregar, col_espacio = st.columns([1, 5])
        with col_btn_agregar:
            if st.button("➕ Agregar", type="secondary", use_container_width=True, key=f"add_top_{dataset_sel}"):
                # Crear fila vacía
                nueva_fila = pd.DataFrame([{col: "" for col in df_trabajo.columns}])
                # Agregar al INICIO (arriba)
                df_trabajo = pd.concat([nueva_fila, df_trabajo], ignore_index=True)
                st.session_state[f'df_edit_{dataset_sel}'] = df_trabajo
                # Poner en modo edición la nueva fila (índice 0)
                st.session_state[f'editing_row_{dataset_sel}'] = 0
                st.rerun()
        
        st.markdown("")  # Pequeño espacio
        
        # ENCABEZADOS DE COLUMNAS
        cols_header = st.columns([0.3] + [2] * len(df_trabajo.columns) + [0.8])
        
        with cols_header[0]:
            st.markdown("<div class='compact-text'><b>#</b></div>", unsafe_allow_html=True)
        
        for col_idx, columna in enumerate(df_trabajo.columns):
            with cols_header[col_idx + 1]:
                st.markdown(f"<div class='compact-text'><b>{columna}</b></div>", unsafe_allow_html=True)
        
        with cols_header[-1]:
            st.markdown("<div class='compact-text'><b>Acciones</b></div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 0.3rem 0; border-width: 2px; border-color: #333;'>", unsafe_allow_html=True)
        
        # Mostrar tabla con botones (solo filas visibles)
        if len(df_trabajo) > 0:
            # Determinar cuántas filas mostrar
            filas_a_mostrar = min(rows_visible, len(df_trabajo))
            
            for idx in range(filas_a_mostrar):
                cols = st.columns([0.3] + [2] * len(df_trabajo.columns) + [0.8])
                
                # Número de fila
                with cols[0]:
                    st.markdown(f"<div class='compact-text'><b>{idx}</b></div>", unsafe_allow_html=True)
                
                # Si está editando esta fila
                if st.session_state[f'editing_row_{dataset_sel}'] == idx:
                    # Modo edición
                    nuevos_valores = {}
                    for col_idx, columna in enumerate(df_trabajo.columns):
                        with cols[col_idx + 1]:
                            valor_actual = df_trabajo.iloc[idx][columna]
                            nuevos_valores[columna] = st.text_input(
                                columna,
                                value=str(valor_actual) if pd.notna(valor_actual) else "",
                                key=f"edit_{dataset_sel}_{idx}_{columna}",
                                label_visibility="collapsed"
                            )
                    
                    # Botones de acción
                    with cols[-1]:
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("✅", key=f"save_{dataset_sel}_{idx}", help="Guardar"):
                                # Actualizar fila
                                for col, val in nuevos_valores.items():
                                    df_trabajo.at[idx, col] = val
                                st.session_state[f'df_edit_{dataset_sel}'] = df_trabajo
                                st.session_state[f'editing_row_{dataset_sel}'] = None
                                st.rerun()
                        
                        with col_cancel:
                            if st.button("❌", key=f"cancel_{dataset_sel}_{idx}", help="Cancelar"):
                                st.session_state[f'editing_row_{dataset_sel}'] = None
                                st.rerun()
                else:
                    # Modo visualización
                    for col_idx, columna in enumerate(df_trabajo.columns):
                        with cols[col_idx + 1]:
                            valor = df_trabajo.iloc[idx][columna]
                            st.markdown(f"<div class='compact-text'>{str(valor) if pd.notna(valor) else ''}</div>", unsafe_allow_html=True)
                    
                    # Botones de acción
                    with cols[-1]:
                        col_edit, col_delete = st.columns(2)
                        with col_edit:
                            if st.button("✏️", key=f"edit_btn_{dataset_sel}_{idx}", help="Editar"):
                                st.session_state[f'editing_row_{dataset_sel}'] = idx
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️", key=f"delete_{dataset_sel}_{idx}", help="Eliminar"):
                                df_trabajo = df_trabajo.drop(idx).reset_index(drop=True)
                                st.session_state[f'df_edit_{dataset_sel}'] = df_trabajo
                                st.rerun()
                
                st.markdown("<hr style='margin: 0.15rem 0; border-color: #e0e0e0;'>", unsafe_allow_html=True)
            
            # Botones de paginación
            total_filas = len(df_trabajo)
            if total_filas > 10:
                st.markdown("")  # Espacio
                
                col_pag1, col_pag2, col_pag3, col_pag4 = st.columns([2, 2, 2, 4])
                
                with col_pag1:
                    # Botón cargar 10 más
                    if rows_visible < total_filas:
                        if st.button("⬇️ Cargar 10 más", use_container_width=True, key=f"load_more_{dataset_sel}"):
                            st.session_state[f'rows_visible_{dataset_sel}'] = min(rows_visible + 10, total_filas)
                            st.rerun()
                
                with col_pag2:
                    # Botón mostrar todo
                    if rows_visible < total_filas:
                        if st.button("📄 Mostrar Todo", use_container_width=True, key=f"show_all_{dataset_sel}"):
                            st.session_state[f'rows_visible_{dataset_sel}'] = total_filas
                            st.rerun()
                
                with col_pag3:
                    # Botón colapsar
                    if rows_visible > 10:
                        if st.button("⬆️ Mostrar menos", use_container_width=True, key=f"collapse_{dataset_sel}"):
                            st.session_state[f'rows_visible_{dataset_sel}'] = 10
                            st.rerun()
                
                with col_pag4:
                    st.caption(f"Mostrando {rows_visible} de {total_filas} filas")
        
        else:
            st.info("📝 No hay datos. Usa el botón '➕ Agregar' de arriba para comenzar.")
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2, col3 = st.columns([2, 2, 6])
        
        with col1:
            if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                try:
                    df_trabajo = st.session_state[f'df_edit_{dataset_sel}']
                    
                    # Ordenar según el tipo de dataset
                    if dataset_sel == "Tasa Activa":
                        # Mantener orden descendente por fecha
                        if 'Desde' in df_trabajo.columns:
                            df_trabajo['Desde'] = pd.to_datetime(
                                df_trabajo['Desde'],
                                dayfirst=True,
                                format='mixed'
                            )
                            df_trabajo = df_trabajo.sort_values('Desde', ascending=False)
                    
                    df_trabajo.to_csv(archivo, index=False, encoding='utf-8')
                    st.success("✅ Cambios guardados exitosamente")
                    
                    # Resetear estado
                    del st.session_state[f'df_edit_{dataset_sel}']
                    del st.session_state[f'editing_row_{dataset_sel}']
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")
        
        with col2:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar",
                data=csv,
                file_name=f"{dataset_sel}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔄 Recargar Original", use_container_width=True):
                # Resetear a los datos originales
                if f'df_edit_{dataset_sel}' in st.session_state:
                    del st.session_state[f'df_edit_{dataset_sel}']
                if f'editing_row_{dataset_sel}' in st.session_state:
                    del st.session_state[f'editing_row_{dataset_sel}']
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error al cargar dataset: {str(e)}")
        st.exception(e)

st.markdown("---")
st.caption("**Administración del Sistema** | Tribunal de Trabajo N° 2 de Quilmes")
