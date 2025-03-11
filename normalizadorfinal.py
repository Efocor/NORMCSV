"""
NORMALIZADOR UNIVERSAL DE ARCHIVOS CSV/EXCEL 2025
Desarrollado por Felipe Alexander Correa Rodríguez
Versión: 2.0.0

Características:
- Normalización inteligente de fechas
- Procesamiento avanzado de valores monetarios y temporales
- Interfaz gráfica mejorada
- Manejo de múltiples formatos de entrada
- Sistema de logging detallado
"""

#...................................................... | STACK DE LIBRERÍAS
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
import pandas as pd
import numpy as np
import unidecode
import re
from pathlib import Path
import sys
import os
import chardet
import csv
from datetime import datetime
import locale
import logging
from decimal import Decimal

class EstilosApp:
    """Clase para manejar los estilos de la aplicación"""
    
    COLORES = {
        'primary': '#2196F3',
        'secondary': '#4CAF50',
        'background': '#f5f5f5',
        'text': '#333333',
        'error': '#f44336',
        'warning': '#ff9800',
        'success': '#4caf50'
    }
    
    FUENTES = {
        'titulo': ('Helvetica', 16, 'bold'),
        'subtitulo': ('Helvetica', 12, 'bold'),
        'normal': ('Helvetica', 10),
        'pequeño': ('Helvetica', 8)
    }

class ProcesadorDatos:
    """Clase para el procesamiento de datos"""
    
    @staticmethod
    def es_fecha(texto):
        patrones_fecha = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{2}\.\d{2}\.\d{4}',
            r'\d{4}/\d{2}/\d{2}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{2}',
        ]
        return any(re.match(pattern, str(texto)) for pattern in patrones_fecha)

    @staticmethod
    def normalizar_fecha(texto):
        try:
            if pd.isna(texto):
                return None
                
            # Eliminar espacios y caracteres no deseados
            texto = str(texto).strip()
            
            # Intentar diferentes formatos de fecha
            formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y']
            
            for formato in formatos:
                try:
                    fecha = datetime.strptime(texto, formato)
                    return fecha.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            return texto
        except Exception:
            return texto

    @staticmethod
    def procesar_valor_monetario(texto):
        """
        Procesa un valor monetario y devuelve el monto como número.
        Ejemplo: "$ 13.843 : 4,00 hrs" -> 13843.0
        """
        try:
            if pd.isna(texto) or texto == '' or texto.upper() == 'NO TIENE':
                return 0.0

            # Buscar el monto hasta el primer espacio (ej: "$ 13.843")
            match = re.search(r'\$?\s?(\d+[\d\.,]*)', str(texto))
            if match:
                monto = match.group(1).replace('.', '').replace(',', '.')
                return float(Decimal(monto))
            return 0.0
        except Exception:
            return 0.0

    @staticmethod
    def procesar_horas(texto):
        """
        Procesa las horas y devuelve el valor como número.
        Ejemplo: "$ 13.843 : 4,00 hrs" -> 4.0
        """
        try:
            if pd.isna(texto) or texto == '' or texto.upper() == 'NO TIENE':
                return 0.0

            # Buscar el patrón de horas (ej: "4,00 hrs")
            match = re.search(r'(\d+[\.,]\d+|\d+)\s*hrs?', str(texto))
            if match:
                horas = match.group(1).replace(',', '.')
                return float(Decimal(horas))
            return 0.0
        except Exception:
            return 0.0

    @staticmethod
    def es_columna_monetaria(nombre_columna):
        palabras_clave = ['MONTO', 'VALOR', 'PRECIO', 'EXTRAORDINARIA', 'PAGO']
        return any(palabra in nombre_columna.upper() for palabra in palabras_clave)

class NormalizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Normalizador Universal de CSV/Excel 2025 | FECORO")
        self.root.geometry("900x700")
        self.root.configure(bg=EstilosApp.COLORES['background'])
        
        # Variables de control
        self.archivo_entrada = tk.StringVar()
        self.archivo_salida = tk.StringVar()
        self.encoding_detectado = tk.StringVar(value="No detectado")
        self.delimiter_detectado = tk.StringVar(value="No detectado")
        self.progreso = tk.DoubleVar()
        
        # Configurar logging
        self.configurar_logging()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def configurar_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('normalizador.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def crear_interfaz(self):
        # Frame principal con padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título y descripción
        self.crear_encabezado()
        
        # Sección de archivos
        self.crear_seccion_archivos()
        
        # Sección de información
        self.crear_seccion_info()
        
        # Sección de controles
        self.crear_seccion_controles()
        
        # Barra de progreso
        self.crear_barra_progreso()
        
        # Log de eventos
        self.crear_log_eventos()
        
        # Pie de página
        self.crear_pie_pagina()

    def crear_encabezado(self):
        frame_titulo = ttk.Frame(self.main_frame)
        frame_titulo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            frame_titulo,
            text="Normalizador Universal de Archivos CSV/Excel",
            font=EstilosApp.FUENTES['titulo']
        ).pack()
        
        ttk.Label(
            frame_titulo,
            text="Normalización inteligente de datos con preservación de fechas y valores",
            font=EstilosApp.FUENTES['subtitulo']
        ).pack()

    def crear_seccion_archivos(self):
        """Crea la sección para seleccionar archivos de entrada y salida"""
        frame_archivos = ttk.LabelFrame(self.main_frame, text="Gestión de Archivos", padding="10")
        frame_archivos.pack(fill=tk.X, pady=(0, 10))

        # Archivo de entrada
        frame_entrada = ttk.Frame(frame_archivos)
        frame_entrada.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(frame_entrada, text="Archivo de Entrada:", width=15).pack(side=tk.LEFT)
        ttk.Entry(frame_entrada, textvariable=self.archivo_entrada, width=50).pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
        ttk.Button(frame_entrada, text="Buscar", command=self.seleccionar_archivo_entrada).pack(side=tk.LEFT)

        # Archivo de salida
        frame_salida = ttk.Frame(frame_archivos)
        frame_salida.pack(fill=tk.X)
        ttk.Label(frame_salida, text="Archivo de Salida:", width=15).pack(side=tk.LEFT)
        ttk.Entry(frame_salida, textvariable=self.archivo_salida, width=50).pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
        ttk.Button(frame_salida, text="Buscar", command=self.seleccionar_archivo_salida).pack(side=tk.LEFT)

    def crear_seccion_info(self):
        """Crea la sección de información del archivo"""
        frame_info = ttk.LabelFrame(self.main_frame, text="Información del Archivo", padding="10")
        frame_info.pack(fill=tk.X, pady=(0, 10))

        # Información de encoding
        frame_encoding = ttk.Frame(frame_info)
        frame_encoding.pack(fill=tk.X)
        ttk.Label(frame_encoding, text="Encoding detectado:", width=20).pack(side=tk.LEFT)
        ttk.Label(frame_encoding, textvariable=self.encoding_detectado, foreground="#0078D7").pack(side=tk.LEFT)

        # Información del delimitador
        frame_delimiter = ttk.Frame(frame_info)
        frame_delimiter.pack(fill=tk.X)
        ttk.Label(frame_delimiter, text="Delimitador detectado:", width=20).pack(side=tk.LEFT)
        ttk.Label(frame_delimiter, textvariable=self.delimiter_detectado, foreground="#0078D7").pack(side=tk.LEFT)

    def crear_seccion_controles(self):
        """Crea la sección de controles de proceso"""
        frame_controles = ttk.Frame(self.main_frame)
        frame_controles.pack(fill=tk.X, pady=(0, 10))

        # Botón para analizar archivo
        ttk.Button(
            frame_controles,
            text="Analizar Archivo",
            command=self.analizar_archivo,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Botón para normalizar archivo
        ttk.Button(
            frame_controles,
            text="Normalizar Archivo",
            command=self.procesar_archivo,
            style="Accent.TButton"
        ).pack(side=tk.LEFT)

    def crear_barra_progreso(self):
        """Crea la barra de progreso"""
        self.barra_progreso = ttk.Progressbar(
            self.main_frame,
            variable=self.progreso,
            maximum=100,
            style="Horizontal.TProgressbar"
        )
        self.barra_progreso.pack(fill=tk.X, pady=(0, 10))

    def crear_log_eventos(self):
        """Crea el área de log de eventos"""
        frame_log = ttk.LabelFrame(self.main_frame, text="Eventos", padding="10")
        frame_log.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(frame_log, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar para el log
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def crear_pie_pagina(self):
        """Crea el pie de página con la firma"""
        frame_pie = ttk.Frame(self.main_frame)
        frame_pie.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(
            frame_pie,
            text="© 2025 FECORO (Felipe Correa Rodríguez)",
            font=("Helvetica", 8),
            foreground="gray"
        ).pack(side=tk.RIGHT)

    # --------------------------------------------
    # Funcionalidades principales
    # --------------------------------------------

    def seleccionar_archivo_entrada(self):
        """Abre un diálogo para seleccionar el archivo de entrada"""
        filetypes = [
            ('Archivos CSV', '*.csv'),
            ('Archivos Excel', '*.xlsx *.xls'),
            ('Todos los archivos', '*.*')
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.archivo_entrada.set(filename)
            # Generar nombre de salida automático
            path = Path(filename)
            nuevo_nombre = f"{path.stem}_normalizado{path.suffix}"
            self.archivo_salida.set(str(Path(path.parent) / nuevo_nombre))
            self.encoding_detectado.set("No detectado")
            self.delimiter_detectado.set("No detectado")

    def seleccionar_archivo_salida(self):
        """Abre un diálogo para seleccionar el archivo de salida"""
        filetypes = [
            ('Archivos CSV', '*.csv'),
            ('Archivos Excel', '*.xlsx *.xls')
        ]
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".csv")
        if filename:
            self.archivo_salida.set(filename)

    def detectar_encoding(self):
        """Detecta el encoding del archivo"""
        try:
            with open(self.archivo_entrada.get(), 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                self.encoding_detectado.set(encoding)
                self.log(f"Encoding detectado: {encoding}")
        except Exception as e:
            self.log(f"Error detectando encoding: {str(e)}", error=True)
            self.encoding_detectado.set("Error")

    def detectar_delimitador(self):
        """Detecta el delimitador del archivo CSV"""
        try:
            with open(self.archivo_entrada.get(), 'r', encoding=self.encoding_detectado.get()) as file:
                sample = file.read(4096)
                dialect = csv.Sniffer().sniff(sample)
                self.delimiter_detectado.set(dialect.delimiter)
                self.log(f"Delimitador detectado: {dialect.delimiter}")
        except Exception as e:
            self.log(f"Error detectando delimitador: {str(e)}", error=True)
            self.delimiter_detectado.set("Error")

    def analizar_archivo(self):
        """Analiza el archivo seleccionado"""
        try:
            if not self.archivo_entrada.get():
                raise ValueError("Debe seleccionar un archivo de entrada")
                
            self.log("Iniciando análisis del archivo...")
            self.progreso.set(0)
            
            # Detectar encoding y delimitador
            self.detectar_encoding()
            self.progreso.set(33)
            self.detectar_delimitador()
            self.progreso.set(66)
            
            # Verificar lectura del archivo
            if self.archivo_entrada.get().endswith('.csv'):
                df = pd.read_csv(
                    self.archivo_entrada.get(),
                    encoding=self.encoding_detectado.get(),
                    delimiter=self.delimiter_detectado.get(),
                    nrows=5
                )
            else:
                df = pd.read_excel(self.archivo_entrada.get(), nrows=5)
            self.progreso.set(100)
            self.log("Archivo analizado correctamente", success=True)
        except Exception as e:
            self.log(f"Error en análisis: {str(e)}", error=True)
            messagebox.showerror("Error", f"Error en análisis: {str(e)}")
            self.progreso.set(0)

    def procesar_archivo(self):
        """Procesa el archivo y lo normaliza"""
        try:
            if not self.archivo_entrada.get() or not self.archivo_salida.get():
                raise ValueError("Debe seleccionar archivos de entrada y salida")
            
            self.log("Iniciando procesamiento del archivo...")
            self.progreso.set(0)
            
            # Leer el archivo
            if self.archivo_entrada.get().endswith('.csv'):
                df = pd.read_csv(
                    self.archivo_entrada.get(),
                    encoding=self.encoding_detectado.get(),
                    delimiter=self.delimiter_detectado.get()
                )
            else:
                df = pd.read_excel(self.archivo_entrada.get())
            self.progreso.set(20)
            self.log("Archivo leído correctamente", success=True)
            
            # Normalizar nombres de columnas
            df.columns = [self.normalizar_nombre_columna(col) for col in df.columns]
            self.progreso.set(40)
            self.log("Nombres de columnas normalizados", success=True)
            
            # Normalizar datos
            for columna in df.columns:
                if any(palabra in columna.upper() for palabra in ['FECHA', 'DATE']):
                    df[columna] = df[columna].apply(ProcesadorDatos.normalizar_fecha)
                elif ProcesadorDatos.es_columna_monetaria(columna):
                    df[f"{columna}_MONTO"] = df[columna].apply(ProcesadorDatos.procesar_valor_monetario)
                    df[f"{columna}_HORAS"] = df[columna].apply(ProcesadorDatos.procesar_horas)
                    df.drop(columna, axis=1, inplace=True)
                else:
                    df[columna] = df[columna].apply(self.normalizar_texto)
            self.progreso.set(80)
            self.log("Datos normalizados", success=True)
            
            # Guardar archivo
            if self.archivo_salida.get().endswith('.csv'):
                df.to_csv(self.archivo_salida.get(), index=False, encoding='utf-8')
            else:
                df.to_excel(self.archivo_salida.get(), index=False)
            self.progreso.set(100)
            self.log("Archivo guardado correctamente", success=True)
            messagebox.showinfo("Éxito", "Archivo normalizado y guardado correctamente")
        except Exception as e:
            self.log(f"Error en procesamiento: {str(e)}", error=True)
            messagebox.showerror("Error", f"Error en procesamiento: {str(e)}")
            self.progreso.set(0)

    # --------------------------------------------
    # Métodos de normalización
    # --------------------------------------------

    @staticmethod
    def normalizar_nombre_columna(nombre):
        """Normaliza el nombre de una columna"""
        nombre = str(nombre).strip().upper()
        nombre = unidecode.unidecode(nombre)
        nombre = re.sub(r'[^A-Z0-9_]', '_', nombre)
        nombre = re.sub(r'_+', '_', nombre)
        return nombre.strip('_')

    @staticmethod
    def normalizar_texto(texto):
        """Normaliza un texto genérico"""
        if pd.isna(texto):
            return ""
        texto = str(texto).strip()
        texto = unidecode.unidecode(texto)
        texto = re.sub(r'[^\w\s]', '', texto)
        return texto.upper()

    # --------------------------------------------
    # Métodos de logging
    # --------------------------------------------

    def log(self, mensaje, error=False, success=False):
        """Registra un mensaje en el log"""
        hora_actual = datetime.now().strftime("%H:%M:%S")
        mensaje_formateado = f"[{hora_actual}] {mensaje}\n"
        
        if error:
            self.log_text.tag_config("error", foreground="red")
            self.log_text.insert(tk.END, mensaje_formateado, "error")
        elif success:
            self.log_text.tag_config("success", foreground="green")
            self.log_text.insert(tk.END, mensaje_formateado, "success")
        else:
            self.log_text.insert(tk.END, mensaje_formateado)
            
        self.log_text.see(tk.END)
        self.root.update()

# --------------------------------------------
# Punto de entrada
# --------------------------------------------

def main():
    # Configurar la interfaz gráfica
    root = tk.Tk()
    app = NormalizadorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

#...................................................... | END