import sqlite3
import os
import shutil
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        try:
            os.makedirs('data', exist_ok=True)
        except OSError as e:
            print(f"Error creating directory: {e}")
        
        self.conn = sqlite3.connect('data/gimnasio.db', check_same_thread=False)
        self.create_tables()
        self.actualizar_registros_existentes()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                cedula TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT,
                telefono_emergencia TEXT,
                direccion TEXT,
                foto_path TEXT,
                fecha_registro DATE
            )
        ''')
        
        # Tabla de pagos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula_cliente TEXT,
                monto REAL,
                duracion_meses INTEGER,
                fecha_pago DATE,
                fecha_vencimiento DATE,
                metodo_pago TEXT,
                activo BOOLEAN DEFAULT 1,
                FOREIGN KEY (cedula_cliente) REFERENCES clientes (cedula) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de accesos (FALTABA ESTA TABLA)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accesos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula_cliente TEXT,
                tipo_movimiento TEXT,
                fecha_hora DATETIME,
                FOREIGN KEY (cedula_cliente) REFERENCES clientes (cedula) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
        print("Tablas verificadas o creadas exitosamente!")
        
        # Asegurar que la columna activo existe
        self.agregar_columna_activo()
    
    def agregar_columna_activo(self):
        """Agrega la columna activo si no existe"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(pagos)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if 'activo' not in columnas:
                print("Agregando columna 'activo' a la tabla pagos...")
                cursor.execute("ALTER TABLE pagos ADD COLUMN activo BOOLEAN DEFAULT 1")
                self.conn.commit()
                print("Columna 'activo' agregada exitosamente")
                
        except Exception as e:
            print(f"Error al agregar columna activo: {e}")
    
    def actualizar_registros_existentes(self):
        """Actualiza los registros existentes"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE pagos SET activo = 1 WHERE activo IS NULL")
            self.conn.commit()
        except Exception as e:
            print(f"Error actualizando registros: {e}")
    
    # --- MÉTODOS DE CLIENTES ---
    
    def insert_cliente(self, cedula, nombre, apellido, telefono="", telefono_emergencia="", direccion="", foto_path=""):
        """Inserta un nuevo cliente (MÉTODO AÑADIDO)"""
        try:
            cursor = self.conn.cursor()
            fecha_registro = datetime.now().date()
            cursor.execute('''
                INSERT INTO clientes 
                (cedula, nombre, apellido, telefono, telefono_emergencia, direccion, foto_path, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cedula, nombre, apellido, telefono, telefono_emergencia, direccion, foto_path, fecha_registro))
            self.conn.commit()
            print(f"Cliente {nombre} {apellido} insertado correctamente.")
            return True
        except sqlite3.IntegrityError:
            print(f"Error: Cliente con cédula {cedula} ya existe.")
            return False
        except Exception as e:
            print(f"Error insertando cliente: {e}")
            return False
            
    def get_cliente_by_cedula(self, cedula):
        """Obtiene un cliente por su cédula (MÉTODO AÑADIDO)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM clientes WHERE cedula = ?', (cedula,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error obteniendo cliente: {e}")
            return None

    def actualizar_cliente(self, cedula, nombre, apellido, telefono, telefono_emergencia, direccion, foto_path):
        """Actualiza la información de un cliente"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE clientes 
                SET nombre = ?, apellido = ?, telefono = ?, telefono_emergencia = ?, 
                    direccion = ?, foto_path = ?
                WHERE cedula = ?
            ''', (nombre, apellido, telefono, telefono_emergencia, direccion, foto_path, cedula))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error actualizando cliente: {e}")
            return False

    def buscar_clientes(self, criterios, estado="Todos"):
        """Busca clientes con información de estado de pago (VERSIÓN CORREGIDA)"""
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT c.*, 
                       p.fecha_vencimiento as fecha_vencimiento,
                       CASE 
                           WHEN p.fecha_vencimiento >= date('now') THEN 'Activo'
                           WHEN p.fecha_vencimiento < date('now') THEN 'Vencido'
                           ELSE 'Sin pago'
                       END as estado_pago
                FROM clientes c
                LEFT JOIN pagos p ON c.cedula = p.cedula_cliente AND p.activo = 1
                WHERE 1=1
            """
            params = []
            
            # Agregar criterios de búsqueda
            for field in ['cedula', 'nombre', 'apellido', 'telefono']:
                if criterios.get(field):
                    query += f" AND c.{field} LIKE ?"
                    params.append(f"%{criterios[field]}%")
            
            # Filtro por estado (LÓGICA CORREGIDA)
            if estado == "Activos":
                query += " AND p.fecha_vencimiento >= date('now')"
            elif estado == "Vencidos":
                # Vencidos O que nunca han tenido un pago activo
                query += " AND (p.fecha_vencimiento < date('now') OR p.id IS NULL)"
            
            query += " ORDER BY c.nombre, c.apellido"
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Error en buscar_clientes: {e}")
            return []
            
    def get_historial_completo_cliente(self, cedula):
        """Obtiene el historial completo de un cliente"""
        cursor = self.conn.cursor()
        
        # Información del cliente
        cliente = self.get_cliente_by_cedula(cedula)
        
        # Historial de pagos
        pagos = self.get_pagos_by_cliente(cedula)
        
        # Historial de accesos
        cursor.execute('''
            SELECT * FROM accesos 
            WHERE cedula_cliente = ? 
            ORDER BY fecha_hora DESC 
            LIMIT 100
        ''', (cedula,))
        accesos = cursor.fetchall()
        
        return {
            'cliente': cliente,
            'pagos': pagos,
            'accesos': accesos
        }

    # --- MÉTODOS DE PAGOS ---

    def insert_pago(self, cedula_cliente, monto, duracion_meses, metodo_pago):
        try:
            cursor = self.conn.cursor()
            
            fecha_pago = datetime.now().date()
            fecha_vencimiento = fecha_pago + timedelta(days=30 * duracion_meses)
            
            # Desactivar pagos anteriores
            cursor.execute('UPDATE pagos SET activo = 0 WHERE cedula_cliente = ?', (cedula_cliente,))
            
            # Insertar nuevo pago
            cursor.execute('''
                INSERT INTO pagos 
                (cedula_cliente, monto, duracion_meses, fecha_pago, fecha_vencimiento, metodo_pago, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cedula_cliente, monto, duracion_meses, fecha_pago, fecha_vencimiento, metodo_pago, 1))
            
            self.conn.commit()
            print(f"Pago insertado para {cedula_cliente}.")
            return True
        except Exception as e:
            print(f"Error insertando pago: {e}")
            return False
    
    def get_pagos_by_cliente(self, cedula_cliente):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pagos WHERE cedula_cliente = ? ORDER BY fecha_pago DESC', (cedula_cliente,))
        return cursor.fetchall()
    
    def get_pago_activo(self, cedula_cliente):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pagos WHERE cedula_cliente = ? AND activo = 1', (cedula_cliente,))
        return cursor.fetchone()

    # --- MÉTODOS DE ACCESOS ---

    def registrar_acceso(self, cedula_cliente, tipo_movimiento="Entrada"):
        """Registra entrada o salida de un cliente"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar si el cliente existe
            cliente = self.get_cliente_by_cedula(cedula_cliente)
            if not cliente:
                return False, "Cliente no encontrado"
            
            # Verificar si tiene membresía activa
            pago_activo = self.get_pago_activo(cedula_cliente)
            if not pago_activo:
                return False, "Membresía vencida o sin pago"
            
            # Verificar si la membresía no está vencida
            # pago_activo[5] es 'fecha_vencimiento'
            fecha_vencimiento = datetime.strptime(pago_activo[5], '%Y-%m-%d').date()
            if fecha_vencimiento < datetime.now().date():
                return False, "Membresía vencida"
            
            # Registrar acceso
            cursor.execute('''
                INSERT INTO accesos (cedula_cliente, tipo_movimiento, fecha_hora)
                VALUES (?, ?, ?)
            ''', (cedula_cliente, tipo_movimiento, datetime.now()))
            
            self.conn.commit()
            return True, f"Acceso {tipo_movimiento.lower()} registrado correctamente"
            
        except Exception as e:
            print(f"Error registrando acceso: {e}")
            return False, "Error al registrar acceso"

    def get_accesos_recientes(self, limite=50):
        """Obtiene los accesos más recientes"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, c.nombre, c.apellido 
            FROM accesos a
            JOIN clientes c ON a.cedula_cliente = c.cedula
            ORDER BY a.fecha_hora DESC 
            LIMIT ?
        ''', (limite,))
        return cursor.fetchall()

    # --- MÉTODOS DE ESTADÍSTICAS Y ADMIN ---

    def get_estadisticas_completas(self):
        """Obtiene estadísticas completas del gimnasio"""
        cursor = self.conn.cursor()
        
        # Total de clientes
        cursor.execute('SELECT COUNT(*) FROM clientes')
        total_clientes = cursor.fetchone()[0]
        
        # Clientes activos
        cursor.execute('''
            SELECT COUNT(DISTINCT cedula_cliente) 
            FROM pagos 
            WHERE activo = 1 AND fecha_vencimiento >= date('now')
        ''')
        clientes_activos = cursor.fetchone()[0]
        
        # Clientes vencidos
        clientes_vencidos = total_clientes - clientes_activos
        
        # Ingresos del mes actual
        cursor.execute('''
            SELECT SUM(monto) 
            FROM pagos 
            WHERE strftime('%Y-%m', fecha_pago) = strftime('%Y-%m', 'now')
        ''')
        ingresos_mes_actual = cursor.fetchone()[0] or 0
        
        # Ingresos del mes anterior
        cursor.execute('''
            SELECT SUM(monto) 
            FROM pagos 
            WHERE strftime('%Y-%m', fecha_pago) = strftime('%Y-%m', date('now', '-1 month'))
        ''')
        ingresos_mes_anterior = cursor.fetchone()[0] or 0
        
        # Accesos hoy
        cursor.execute('''
            SELECT COUNT(*) 
            FROM accesos 
            WHERE DATE(fecha_hora) = DATE('now') AND tipo_movimiento = 'Entrada'
        ''')
        accesos_hoy = cursor.fetchone()[0]
        
        return {
            'total_clientes': total_clientes,
            'clientes_activos': clientes_activos,
            'clientes_vencidos': clientes_vencidos,
            'ingresos_mes_actual': ingresos_mes_actual,
            'ingresos_mes_anterior': ingresos_mes_anterior,
            'accesos_hoy': accesos_hoy,
            'tasa_retencion': (clientes_activos / total_clientes * 100) if total_clientes > 0 else 0
        }

    def get_clientes_proximos_vencer(self, dias=7):
        """Obtiene clientes cuya membresía está por vencer"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.cedula, c.nombre, c.apellido, p.fecha_vencimiento,
                   JULIANDAY(p.fecha_vencimiento) - JULIANDAY('now') as dias_restantes
            FROM clientes c
            JOIN pagos p ON c.cedula = p.cedula_cliente
            WHERE p.activo = 1 
              AND p.fecha_vencimiento >= date('now')
              AND p.fecha_vencimiento <= date('now', ?)
            ORDER BY p.fecha_vencimiento ASC
        ''', (f'+{dias} days',))
        return cursor.fetchall()

    def crear_backup(self, ruta_backup=None):
        """Crea un backup de la base de datos"""
        try:
            if ruta_backup is None:
                # Crear directorio backups si no existe
                os.makedirs('backups', exist_ok=True)
                fecha = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                ruta_backup = f'backups/backup_gimnasio_{fecha}.db'
            
            # Copiar archivo de base de datos
            shutil.copy2('data/gimnasio.db', ruta_backup)
            print(f"Backup creado exitosamente: {ruta_backup}")
            return True
        except Exception as e:
            print(f"Error creando backup: {e}")
            return False
        
        # --- MÉTODOS ADICIONALES DE ACCESOS ---

    def get_accesos_por_fecha(self, fecha_inicio, fecha_fin=None):
        """Obtiene accesos en un rango de fechas"""
        cursor = self.conn.cursor()
        
        if fecha_fin is None:
            fecha_fin = fecha_inicio
            
        cursor.execute('''
            SELECT a.*, c.nombre, c.apellido 
            FROM accesos a
            JOIN clientes c ON a.cedula_cliente = c.cedula
            WHERE DATE(a.fecha_hora) BETWEEN ? AND ?
            ORDER BY a.fecha_hora DESC
        ''', (fecha_inicio, fecha_fin))
        return cursor.fetchall()

    def get_estadisticas_accesos(self):
        """Estadísticas de accesos"""
        cursor = self.conn.cursor()
        
        # Accesos hoy
        cursor.execute('''
            SELECT COUNT(*) 
            FROM accesos 
            WHERE DATE(fecha_hora) = DATE('now') 
            AND tipo_movimiento = 'Entrada'
        ''')
        accesos_hoy = cursor.fetchone()[0]
        
        # Accesos esta semana
        cursor.execute('''
            SELECT COUNT(*) 
            FROM accesos 
            WHERE fecha_hora >= date('now', 'weekday 0', '-7 days')
            AND tipo_movimiento = 'Entrada'
        ''')
        accesos_semana = cursor.fetchone()[0]
        
        # Hora pico de accesos
        cursor.execute('''
            SELECT strftime('%H', fecha_hora) as hora, COUNT(*) as cantidad
            FROM accesos
            WHERE tipo_movimiento = 'Entrada'
            GROUP BY hora
            ORDER BY cantidad DESC
            LIMIT 1
        ''')
        hora_pico = cursor.fetchone()
        
        return {
            'accesos_hoy': accesos_hoy,
            'accesos_semana': accesos_semana,
            'hora_pico': hora_pico[0] if hora_pico else 'N/A'
        }

    def get_ultimo_acceso_cliente(self, cedula_cliente):
        """Obtiene el último acceso de un cliente"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM accesos 
            WHERE cedula_cliente = ? 
            ORDER BY fecha_hora DESC 
            LIMIT 1
        ''', (cedula_cliente,))
        return cursor.fetchone()

    # --- MÉTODOS ADICIONALES DE CLIENTES ---

    def get_all_clientes(self):
        """Obtiene todos los clientes"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM clientes ORDER BY nombre, apellido')
        return cursor.fetchall()

    def eliminar_cliente(self, cedula):
        """Elimina un cliente y sus registros asociados"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE cedula = ?", (cedula,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error eliminando cliente: {e}")
            return False

    # --- MÉTODOS ADICIONALES DE PAGOS ---

    def get_clientes_vencidos(self):
        """Obtiene clientes con membresía vencida"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.cedula, c.nombre, c.apellido, p.fecha_vencimiento 
            FROM clientes c
            JOIN pagos p ON c.cedula = p.cedula_cliente
            WHERE p.activo = 1 AND p.fecha_vencimiento < date('now')
            ORDER BY p.fecha_vencimiento ASC
        ''')
        return cursor.fetchall()

    def get_ingresos_por_mes(self, año=None):
        """Obtiene ingresos mensuales"""
        cursor = self.conn.cursor()
        
        if año is None:
            año = datetime.now().year
            
        cursor.execute('''
            SELECT 
                strftime('%m', fecha_pago) as mes,
                SUM(monto) as total_mes,
                COUNT(*) as cantidad_pagos
            FROM pagos 
            WHERE strftime('%Y', fecha_pago) = ?
            GROUP BY mes
            ORDER BY mes
        ''', (str(año),))
        
        return cursor.fetchall()
        
    