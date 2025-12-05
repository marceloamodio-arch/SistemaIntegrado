#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Autenticación
Tribunal de Trabajo 2 de Quilmes
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, Tuple, List

class AuthSystem:
    """Sistema de autenticación con SQLite"""
    
    def __init__(self, db_path: str = "data/usuarios.db"):
        """Inicializa el sistema de autenticación"""
        self.db_path = db_path
        self._crear_base_datos()
        self._crear_admin_default()
    
    def _crear_base_datos(self):
        """Crea la base de datos y tabla de usuarios si no existe"""
        # Crear directorio data si no existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nivel TEXT NOT NULL CHECK(nivel IN ('admin', 'normal')),
                nombre_completo TEXT,
                email TEXT,
                fecha_creacion TEXT NOT NULL,
                ultimo_acceso TEXT,
                activo INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _crear_admin_default(self):
        """Crea un usuario admin por defecto si no existe"""
        if not self.usuario_existe("admin"):
            self.crear_usuario(
                username="admin",
                password="admin123",
                nivel="admin",
                nombre_completo="Administrador del Sistema",
                email="admin@tribunal.gob.ar"
            )
    
    def crear_usuario(
        self,
        username: str,
        password: str,
        nivel: str = "normal",
        nombre_completo: str = "",
        email: str = ""
    ) -> Tuple[bool, str]:
        """Crea un nuevo usuario"""
        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        if nivel not in ['admin', 'normal']:
            return False, "Nivel debe ser 'admin' o 'normal'"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, nivel, nombre_completo, email, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, nivel, nombre_completo, email, fecha_actual))
            
            conn.commit()
            conn.close()
            
            return True, f"Usuario '{username}' creado exitosamente"
        
        except sqlite3.IntegrityError:
            return False, f"El usuario '{username}' ya existe"
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}"
    
    def autenticar(self, username: str, password: str) -> Tuple[bool, Optional[dict]]:
        """Autentica un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            
            cursor.execute('''
                SELECT id, username, nivel, nombre_completo, email, activo
                FROM usuarios
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            resultado = cursor.fetchone()
            
            if resultado and resultado[5] == 1:
                cursor.execute('''
                    UPDATE usuarios
                    SET ultimo_acceso = ?
                    WHERE username = ?
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), username))
                
                conn.commit()
                
                usuario = {
                    'id': resultado[0],
                    'username': resultado[1],
                    'nivel': resultado[2],
                    'nombre_completo': resultado[3],
                    'email': resultado[4]
                }
                
                conn.close()
                return True, usuario
            
            conn.close()
            return False, None
        
        except Exception as e:
            return False, None
    
    def usuario_existe(self, username: str) -> bool:
        """Verifica si un usuario existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE username = ?', (username,))
        existe = cursor.fetchone()[0] > 0
        
        conn.close()
        return existe
    
    def obtener_usuarios(self) -> List[dict]:
        """Obtiene lista de todos los usuarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nivel, nombre_completo, email, fecha_creacion, ultimo_acceso, activo
            FROM usuarios
            ORDER BY fecha_creacion DESC
        ''')
        
        resultados = cursor.fetchall()
        conn.close()
        
        usuarios = []
        for r in resultados:
            usuarios.append({
                'id': r[0],
                'username': r[1],
                'nivel': r[2],
                'nombre_completo': r[3],
                'email': r[4],
                'fecha_creacion': r[5],
                'ultimo_acceso': r[6],
                'activo': bool(r[7])
            })
        
        return usuarios
    
    def eliminar_usuario(self, username: str) -> Tuple[bool, str]:
        """Elimina un usuario"""
        if username == "admin":
            return False, "No se puede eliminar el usuario admin"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM usuarios WHERE username = ?', (username,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, f"Usuario '{username}' eliminado"
            else:
                conn.close()
                return False, f"Usuario '{username}' no encontrado"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def cambiar_password(self, username: str, nueva_password: str) -> Tuple[bool, str]:
        """Cambia la contraseña de un usuario"""
        if len(nueva_password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(nueva_password)
            
            cursor.execute('''
                UPDATE usuarios
                SET password_hash = ?
                WHERE username = ?
            ''', (password_hash, username))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Contraseña actualizada"
            else:
                conn.close()
                return False, "Usuario no encontrado"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
