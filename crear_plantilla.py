import pandas as pd
from datetime import datetime

def crear_plantilla_excel():
    # Datos de ejemplo para la plantilla
    datos_ejemplo = [
        {
            'cedula': '1-234-567',
            'nombre': 'Ana',
            'apellido': 'Martínez',
            'telefono': '6001-2345',
            'telefono_emergencia': '6009-8765',
            'direccion': 'Calle Principal #123, Ciudad',
            'foto': 'fotos/ana_martinez.jpg'
        },
        {
            'cedula': '2-345-678',
            'nombre': 'Carlos',
            'apellido': 'Ruiz',
            'telefono': '6002-3456',
            'telefono_emergencia': '6008-7654',
            'direccion': 'Avenida Central #456, Ciudad',
            'foto': 'fotos/carlos_ruiz.jpg'
        },
        {
            'cedula': '3-456-789',
            'nombre': 'María',
            'apellido': 'González',
            'telefono': '6003-4567',
            'telefono_emergencia': '6007-6543',
            'direccion': 'Barrio Norte #789, Ciudad',
            'foto': 'fotos/maria_gonzalez.jpg'
        },
        {
            'cedula': '4-567-890',
            'nombre': 'Pedro',
            'apellido': 'López',
            'telefono': '6004-5678',
            'telefono_emergencia': '6006-5432',
            'direccion': 'Sector Sur #321, Ciudad',
            'foto': 'fotos/pedro_lopez.jpg'
        },
        {
            'cedula': '5-678-901',
            'nombre': 'Laura',
            'apellido': 'Díaz',
            'telefono': '6005-6789',
            'telefono_emergencia': '6005-4321',
            'direccion': 'Urbanización Este #654, Ciudad',
            'foto': 'fotos/laura_diaz.jpg'
        }
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(datos_ejemplo)
    
    # Crear archivo Excel
    nombre_archivo = f"plantilla_clientes_gimnasio.xlsx"
    
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        # Hoja con datos de ejemplo
        df.to_excel(writer, sheet_name='Clientes Ejemplo', index=False)
        
        # Hoja con plantilla vacía
        df_vacio = pd.DataFrame(columns=df.columns)
        df_vacio.to_excel(writer, sheet_name='Plantilla Vacía', index=False)
        
        # Obtener el libro de trabajo para formatear
        workbook = writer.book
        worksheet_ejemplo = writer.sheets['Clientes Ejemplo']
        worksheet_vacia = writer.sheets['Plantilla Vacía']
        
        # Ajustar ancho de columnas
        for column in worksheet_ejemplo.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet_ejemplo.column_dimensions[column_letter].width = adjusted_width
            worksheet_vacia.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Plantilla creada: {nombre_archivo}")
    print("📋 Hojas incluidas:")
    print("   - 'Clientes Ejemplo': Con datos de ejemplo")
    print("   - 'Plantilla Vacía': Para que llenes con tus datos")
    print("\n💡 Instrucciones:")
    print("   1. Usa la hoja 'Plantilla Vacía' para agregar tus clientes")
    print("   2. Mantén los nombres de columnas exactamente igual")
    print("   3. Las únicas columnas obligatorias son: cedula, nombre, apellido")
    print("   4. Guarda el archivo y cárgalo en el sistema")

def crear_plantilla_minima():
    """Crear una plantilla mínima sin datos de ejemplo"""
    columnas = [
        'cedula',
        'nombre', 
        'apellido',
        'telefono',
        'telefono_emergencia',
        'direccion',
        'foto'
    ]
    
    df = pd.DataFrame(columns=columnas)
    
    # Agregar una fila con ejemplos en los headers
    df.loc[0] = [
        'Ej: 1-234-567',
        'Ej: Ana',
        'Ej: Martínez', 
        'Ej: 6001-2345',
        'Ej: 6009-8765',
        'Ej: Calle Principal #123',
        'Ej: fotos/cliente.jpg'
    ]
    
    nombre_archivo = "plantilla_clientes_minima.xlsx"
    df.to_excel(nombre_archivo, index=False, sheet_name='Clientes')
    
    print(f"✅ Plantilla mínima creada: {nombre_archivo}")

if __name__ == "__main__":
    print("🎯 Creando plantillas Excel para carga masiva...")
    print("-" * 50)
    
    crear_plantilla_excel()
    print("\n" + "-" * 50)
    crear_plantilla_minima()
    
    print("\n🎉 ¡Plantillas listas! Puedes usarlas en el sistema.")