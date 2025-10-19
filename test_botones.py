# test_botones.py
import tkinter as tk
from tkinter import ttk, messagebox

def test_botones_simples():
    root = tk.Tk()
    root.title("Test Botones")
    root.geometry("400x300")
    
    def boton_editar_click():
        print("✅ Botón EDITAR clickeado!")
        messagebox.showinfo("Test", "Botón EDITAR funcionando")
    
    def boton_foto_click():
        print("✅ Botón FOTO clickeado!")
        messagebox.showinfo("Test", "Botón FOTO funcionando")
    
    # Frame principal
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Botones de prueba
    ttk.Button(main_frame, text="✏️ EDITAR - Prueba", 
              command=boton_editar_click).pack(pady=10)
    
    ttk.Button(main_frame, text="📷 SELECCIONAR FOTO - Prueba", 
              command=boton_foto_click).pack(pady=10)
    
    ttk.Label(main_frame, text="Si estos botones funcionan, el problema está en la lógica de la aplicación", 
             wraplength=350).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_botones_simples()