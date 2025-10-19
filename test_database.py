from database import Database

# Crear instancia
db = Database()

# Verificar métodos disponibles
print("Métodos disponibles en Database:")
methods = [method for method in dir(db) if not method.startswith('_')]
for method in methods:
    print(f" - {method}")

# Verificar específicamente buscar_clientes
if hasattr(db, 'buscar_clientes'):
    print("✅ buscar_clientes está disponible!")
    
    # Probar el método
    resultados = db.buscar_clientes({}, "Todos")
    print(f"Resultados de búsqueda: {len(resultados)} clientes")
else:
    print("❌ buscar_clientes NO está disponible")