from database import Database

db = Database()

# Probar búsqueda
resultados = db.buscar_clientes({'nombre': ''}, 'Todos')
print(f"Clientes encontrados: {len(resultados)}")

# Probar inserción de pago
if db.insert_pago('12345678', 100.0, 1, 'Efectivo'):
    print("✅ Pago insertado correctamente")
else:
    print("❌ Error insertando pago")

# Probar obtener pago activo
pago_activo = db.get_pago_activo('12345678')
print(f"Pago activo: {pago_activo}")