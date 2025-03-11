"""
* ESTE CODIGO FUE HECHO PARA LA MUNICIPALIDAD DE RENGO CON EL MOTIVO DE CONSTRUIR UN NORMALIZADOR DE ARCHIVOS CSV
* ---- PROGRAMADO POR FELIPE ALEXANDER CORREA RODRÍGUEZ, AÑO 2025
* ---- EL CÓDIGO REALIZA EL SIGUIENTE EJERCICIO: TOMA UN ARCHIVO, CHEQUEA SUS CAMPOS, ELIMINA PUNTOS Y COMAS, QUITA ACENTOS, ETC
* ---- EL OUTPUT ES UN ARCHIVO QUE EN TEORÍA PUEDE SER SUBIDO SIN PROBLEMAS POR DBEAVER.
"""
#...................................................... | STACK DE LIBRERÍAS
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import unidecode
import re
from pathlib import Path
import sys
import os #para abrir path
import chardet
import csv

#...................................................... | CLASE PRINCIPAL
class NormalizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Normalizador Universal de CSV/Excel | FECORO")
        self.root.geometry("800x607")
        self.root.configure(bg='#f0f0f0')
        
        # ..variables
        self.archivo_entrada = tk.StringVar()
        self.archivo_salida = tk.StringVar()
        self.encoding_detectado = tk.StringVar(value="No detectado")
        self.delimiter_detectado = tk.StringVar(value="No detectado")
        
        self.crear_interfaz()

#...................................................... | INTERFAZ
    def crear_interfaz(self):
        # ..frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # ..titulo
        titulo = tk.Label(main_frame,
                         text="Normalizador Universal de Archivos CSV",
                         font=('Arial', 16, 'bold'),
                         bg='#f0f0f0')
        titulo.pack(pady=10)

        # ..frame de información
        info_frame = tk.LabelFrame(main_frame,
                                 text="Información del Archivo",
                                 bg='#f0f0f0')
        info_frame.pack(fill='x', padx=5, pady=5)

        # ..labels de información
        tk.Label(info_frame,
                text="Encoding detectado:",
                bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=5)
        tk.Label(info_frame,
                textvariable=self.encoding_detectado,
                bg='#f0f0f0').grid(row=0, column=1, padx=5, pady=5)
        tk.Label(info_frame,
                text="Delimitador detectado:",
                bg='#f0f0f0').grid(row=1, column=0, padx=5, pady=5)
        tk.Label(info_frame,
                textvariable=self.delimiter_detectado,
                bg='#f0f0f0').grid(row=1, column=1, padx=5, pady=5)

        # ..frame para archivo de entrada
        frame_entrada = tk.LabelFrame(main_frame,
                                    text="Archivo de Entrada",
                                    bg='#f0f0f0')
        frame_entrada.pack(fill='x', padx=5, pady=5)

        tk.Entry(frame_entrada,
                 textvariable=self.archivo_entrada,
                 width=112).pack(side='left', padx=5, pady=5)

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
                 width=112).pack(side='left', padx=5, pady=5)

        tk.Button(frame_salida,
                  text="Buscar",
                  command=self.seleccionar_archivo_salida).pack(side='left', padx=5)

        # ..boton de proceso
        proceso_frame = tk.Frame(main_frame, bg='#f0f0f0')
        proceso_frame.pack(fill='x', pady=10)

        tk.Button(proceso_frame,
                  text="Analizar Archivo",
                  command=self.analizar_archivo,
                  bg='#4CAF50',
                  fg='white',
                  font=('Arial', 11)).pack(side='left', padx=5)

        tk.Button(proceso_frame,
                  text="Normalizar Archivo",
                  command=self.procesar_archivo,
                  bg='#2196F3',
                  fg='white',
                  font=('Arial', 11, 'bold')).pack(side='left', padx=5)

        # ..barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame,
                                          variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(fill='x', padx=5, pady=5)

        # ..log de eventos
        self.log_text = tk.Text(main_frame, height=12)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

        # ..firma
        firma_frame = tk.Frame(main_frame, bg='#f0f0f0')
        firma_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        firma_label = tk.Label(
            firma_frame,
            text="© 2025 HECHO POR FECORO (Felipe Correa Rodríguez) | Normalizador Universal",
            font=('Arial', 8),
            fg='gray',
            bg='#f0f0f0'
        )
        firma_label.pack(side=tk.RIGHT)

    def detectar_encoding(self, archivo):
        with open(archivo, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding']

    def detectar_delimiter(self, archivo, encoding):
        sniffer = csv.Sniffer()
        with open(archivo, 'r', encoding=encoding) as file:
            sample = file.read(4096)
            try:
                dialect = sniffer.sniff(sample)
                return dialect.delimiter
            except:
                return None

    def analizar_archivo(self):
        try:
            archivo = self.archivo_entrada.get()
            if not archivo:
                raise ValueError("Seleccione un archivo primero")

            self.log("Analizando archivo...")
            
            # ..detectar encoding
            encoding = self.detectar_encoding(archivo)
            self.encoding_detectado.set(encoding or "No detectado")
            self.log(f"Encoding detectado: {encoding}")

            # ..detectar delimiter si es CSV
            if archivo.endswith('.csv'):
                delimiter = self.detectar_delimiter(archivo, encoding)
                self.delimiter_detectado.set(delimiter or "No detectado")
                self.log(f"Delimitador detectado: {delimiter}")

            self.log("Análisis completado")
            
        except Exception as e:
            self.log(f"Error en análisis: {str(e)}")
            messagebox.showerror("Error", f"Error en análisis: {str(e)}")

    def normalizar_texto(self, texto):
        try:
            if pd.isna(texto):
                return ""
            
            texto = str(texto).strip()
            
            # ..reemplazar caracteres problemáticos
            texto = texto.replace('"', '')
            texto = texto.replace("'", "")
            
            # ..normalizar espacios y puntuación
            texto = re.sub(r'[\s,;]+', ' ', texto)
            texto = texto.replace('.', '')
            
            # ..quitar acentos
            texto = unidecode.unidecode(texto)
            
            # ..eliminar caracteres especiales
            texto = re.sub(r'[^a-zA-Z0-9\s_-]', '', texto)
            
            return texto.strip().upper()
        except Exception as e:
            self.log(f"Error normalizando texto: {str(e)}")
            return str(texto)

    def procesar_archivo(self):
        try:
            if not self.archivo_entrada.get() or not self.archivo_salida.get():
                raise ValueError("Debe seleccionar archivos de entrada y salida")

            self.log("Iniciando normalización...")
            self.progress_var.set(0)
            
            # ..detectar encoding si no se ha hecho
            if self.encoding_detectado.get() == "No detectado":
                self.analizar_archivo()

            encoding = self.encoding_detectado.get()
            
            # ..leer archivo
            if self.archivo_entrada.get().endswith('.csv'):
                delimiter = self.delimiter_detectado.get()
                if delimiter == "No detectado":
                    delimiter = ','
                
                df = pd.read_csv(
                    self.archivo_entrada.get(),
                    encoding=encoding,
                    delimiter=delimiter,
                    on_bad_lines='skip',
                    low_memory=False
                )
            else:
                df = pd.read_excel(self.archivo_entrada.get())

            self.progress_var.set(20)
            self.log("Archivo leído correctamente")

            # ..normalizar nombres de columnas
            df.columns = [self.normalizar_texto(col) for col in df.columns]
            self.progress_var.set(40)
            self.log("Nombres de columnas normalizados")

            # ..normalizar contenido
            total_columns = len(df.columns)
            for idx, columna in enumerate(df.columns):
                df[columna] = df[columna].apply(self.normalizar_texto)
                progress = 40 + (40 * (idx + 1) / total_columns)
                self.progress_var.set(progress)
                self.log(f"Columna {idx+1}/{total_columns} normalizada: {columna}")

            # ..guardar archivo
            if self.archivo_salida.get().endswith('.csv'):
                df.to_csv(
                    self.archivo_salida.get(),
                    index=False,
                    encoding='utf-8',
                    sep=',',
                    quoting=csv.QUOTE_MINIMAL
                )
            else:
                df.to_excel(
                    self.archivo_salida.get(),
                    index=False,
                    engine='openpyxl'
                )

            self.progress_var.set(100)
            self.log("¡Normalización completada exitosamente!")
            messagebox.showinfo("Éxito", "Archivo normalizado correctamente")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error al procesar archivo: {str(e)}")

    def log(self, mensaje):
        self.log_text.insert(tk.END, f"{mensaje}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def seleccionar_archivo_entrada(self):
        filetypes = [
            ('Archivos CSV', '*.csv'),
            ('Archivos Excel', '*.xlsx *.xls'),
            ('Todos los archivos', '*.*')
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.archivo_entrada.set(filename)
            path = Path(filename)
            nuevo_nombre = path.stem + "_normalizado" + path.suffix
            self.archivo_salida.set(str(Path(path.parent) / nuevo_nombre))
            self.encoding_detectado.set("No detectado")
            self.delimiter_detectado.set("No detectado")

    def seleccionar_archivo_salida(self):
        filetypes = [
            ('Archivos CSV', '*.csv'),
            ('Archivos Excel', '*.xlsx')
        ]
        filename = filedialog.asksaveasfilename(
            filetypes=filetypes,
            defaultextension=".csv"
        )
        if filename:
            self.archivo_salida.set(filename)
#...................................................... | FUNCION MAIN
def main():
    root = tk.Tk()
    app = NormalizadorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
#...................................................... | END