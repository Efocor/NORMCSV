"""
* ESTE CODIGO FUE HECHO PARA LA MUNICIPALIDAD DE RENGO CON EL MOTIVO DE CONSTRUIR UN NORMALIZADOR DE ARCHIVOS CSV
* ---- PROGRAMADO POR FELIPE ALEXANDER CORREA RODRÍGUEZ, AÑO 2025
* ---- EL CÓDIGO REALIZA EL SIGUIENTE EJERCICIO: TOMA UN ARCHIVO, CHEQUEA SUS CAMPOS, ELIMINA PUNTOS Y COMAS, QUITA ACENTOS, ETC
* ---- EL OUTPUT ES UN ARCHIVO QUE EN TEORÍA PUEDE SER SUBIDO SIN PROBLEMAS POR DBEAVER.
"""
#...................................................... | STACK DE LIBRERÍAS
import tkinter as tk
from tkinter import filedialog, messagebox,ttk
import pandas as pd
import unidecode
import re
from pathlib import Path
import sys
import os #para abrir path

#...................................................... | CLASE PRINCIPAL
class NormalizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Normalizador de CSV/Excel")
        self.root.geometry("600x400") #tamaño de pantalla
        # ..estilo
        self.root.configure(bg='#f0f0f0')
        # ..variables
        self.archivo_entrada = tk.StringVar()
        self.archivo_salida = tk.StringVar()
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # ..frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # ..título
        titulo = tk.Label(main_frame, 
                         text="Normalizador de Archivos CSV/Excel",
                         font=('Arial', 14, 'bold'),
                         bg='#f0f0f0')
        titulo.pack(pady=10)
        
        # ..frame para archivo de entrada
        frame_entrada = tk.LabelFrame(main_frame, 
                                    text="Archivo de Entrada", #hecho por felipe
                                    bg='#f0f0f0')
        frame_entrada.pack(fill='x', padx=5, pady=5)
        
        tk.Entry(frame_entrada, 
                 textvariable=self.archivo_entrada,
                 width=79).pack(side='left', padx=5, pady=5)
        
        tk.Button(frame_entrada,
                  text="Buscar",
                  command=self.seleccionar_archivo_entrada).pack(side='left', padx=5)
        
        # ..frame para archivo de salida
        frame_salida = tk.LabelFrame(main_frame,
                                   text="Archivo de Salida",
                                   bg='#f0f0f0')
        frame_salida.pack(fill='x', padx=5, pady=5)
        
        tk.Entry(frame_salida,
                 textvariable=self.archivo_salida,
                 width=79).pack(side='left', padx=5, pady=5)
        
        tk.Button(frame_salida, ##hecho por felipe
                  text="Buscar",
                  command=self.seleccionar_archivo_salida).pack(side='left', padx=5)
        
        # ..botón de proceso
        tk.Button(main_frame,
                  text="Normalizar Archivo",
                  command=self.procesar_archivo,
                  bg='#4CAF50',
                  fg='white',
                  font=('Arial', 12, 'bold'),
                  height=2).pack(pady=20)
        
        # ..se crea un frame para mi firmita
        firma_frame = ttk.Frame(main_frame)
        firma_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        firma_label = ttk.Label(
            firma_frame,
            text="Hecho por FECORO",
            font=('Arial', 8),
            foreground='gray'
        )
        firma_label.pack(side=tk.RIGHT)

        # ..log de eventos
        self.log_text = tk.Text(main_frame, height=10)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def recurso_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
        
    def seleccionar_archivo_entrada(self):
        filetypes = [
            ('Archivos CSV', '*.csv'),
            ('Archivos Excel', '*.xlsx *.xls'),
            ('Todos los archivos', '*.*')
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.archivo_entrada.set(filename)
            # ..sugiere nombre de archivo de salida
            path = Path(filename)
            nuevo_nombre = path.stem + "_normalizado" + path.suffix
            self.archivo_salida.set(str(Path(path.parent) / nuevo_nombre))
            
    def seleccionar_archivo_salida(self):
        filetypes = [
            ('Archivos CSV', '*.csv'),
            ('Archivos Excel', '*.xlsx')
        ]
        filename = filedialog.asksaveasfilename(filetypes=filetypes,
                                              defaultextension=".csv")
        if filename:
            self.archivo_salida.set(filename)
            
    def log(self, mensaje):
        self.log_text.insert(tk.END, mensaje + "\n")
        self.log_text.see(tk.END)
        self.root.update()
            
    def normalizar_texto(self, texto):
        try:
            # ..convertir a string y manejar valores nulos
            if pd.isna(texto):
                return ""
            texto = str(texto)
            
            # ..elimina puntos y comas
            texto = texto.replace('.', '').replace(',', '')
            
            # ..elimina acentos y caracteres especiales
            texto = unidecode.unidecode(texto)
            
            # ..elimina caracteres especiales adicionales
            texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
            
            return texto.strip()
        except Exception as e:
            self.log(f"Error al normalizar texto: {str(e)}")
            return texto
            
    def procesar_archivo(self):
        if not self.archivo_entrada.get() or not self.archivo_salida.get():
            messagebox.showerror("Error", "Debe seleccionar archivos de entrada y salida")
            return
            
        try:
            self.log("Iniciando proceso de normalización...")
            
            # ..detecta codificación y lee archivo
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    if self.archivo_entrada.get().endswith('.csv'):
                        df = pd.read_csv(self.archivo_entrada.get(), encoding=encoding)
                    else:
                        df = pd.read_excel(self.archivo_entrada.get())
                    self.log(f"Archivo leído exitosamente con codificación: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    self.log(f"Error con codificación {encoding}: {str(e)}")
                    continue
                    
            if df is None:
                raise Exception("No se pudo leer el archivo con ninguna codificación")
            
            # ..normaliza nombres de columnas
            df.columns = [self.normalizar_texto(col) for col in df.columns]
            
            # ..normaliza contenido
            for columna in df.columns:
                self.log(f"Normalizando columna: {columna}")
                df[columna] = df[columna].apply(self.normalizar_texto)
            
            # ..guarda archivo normalizado
            if self.archivo_salida.get().endswith('.csv'):
                df.to_csv(self.archivo_salida.get(), index=False, encoding='utf-8')
            else:
                df.to_excel(self.archivo_salida.get(), index=False)
                
            self.log("¡Proceso completado exitosamente!")
            messagebox.showinfo("Éxito", "Archivo normalizado correctamente")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error al procesar el archivo: {str(e)}")

#...................................................... | FUNCION MAIN
def main():
    root = tk.Tk()
    app = NormalizadorApp(root)
    root.mainloop() 

if __name__ == "__main__":
    main()
#...................................................... | END