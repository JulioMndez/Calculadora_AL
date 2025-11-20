import tkinter as tk
from tkinter import messagebox, scrolledtext, font
import random # Librería estándar de Python para generar datos de ejemplo

# --- Lógica del Algoritmo de Eliminación Gaussiana ---

def resolver_sistema(matriz_aumentada, pasos_texto):
    """
    Función principal para resolver el sistema de ecuaciones usando Eliminación Gaussiana.
    Lleva la matriz a su forma escalonada (triangular superior).
    """
    if not matriz_aumentada:
        return None

    filas = len(matriz_aumentada)
    columnas = len(matriz_aumentada[0])
    matriz = [fila[:] for fila in matriz_aumentada]

    pasos_texto.insert(tk.END, "Matriz Inicial:\n")
    imprimir_matriz_en_texto(matriz, pasos_texto)

    pivote_fila = 0
    pivote_col = 0

    while pivote_fila < filas and pivote_col < columnas - 1:
        # 1. Encontrar el pivote (Pivoteo parcial)
        max_fila = pivote_fila
        for i in range(pivote_fila + 1, filas):
            if abs(matriz[i][pivote_col]) > abs(matriz[max_fila][pivote_col]):
                max_fila = i
        
        # 2. Intercambiar filas
        if max_fila != pivote_fila:
            matriz[pivote_fila], matriz[max_fila] = matriz[max_fila], matriz[pivote_fila]
            pasos_texto.insert(tk.END, f"\nIntercambiando Fila {pivote_fila + 1} con Fila {max_fila + 1}:\n")
            imprimir_matriz_en_texto(matriz, pasos_texto)

        # 3. Si el pivote es (casi) cero, pasar a la siguiente columna
        if abs(matriz[pivote_fila][pivote_col]) < 1e-9:
            pivote_col += 1
            continue

        # --- CAMBIO CLAVE: Eliminación Gaussiana ---
        # 4. Eliminar solo las filas DEBAJO del pivote
        for i in range(pivote_fila + 1, filas):
            
            pivote_val = matriz[pivote_fila][pivote_col]
            # Evitar división por cero (aunque ya está cubierto por el continue de arriba)
            if abs(pivote_val) < 1e-9: continue

            factor = matriz[i][pivote_col] / pivote_val
            
            if factor != 0:
                for j in range(pivote_col, columnas):
                    matriz[i][j] -= factor * matriz[pivote_fila][j]
                
                # Mostrar el paso de eliminación
                paso_desc = f"\nEliminando en Fila {i + 1} (F{i + 1} - {factor:.2f} * F{pivote_fila + 1}):\n"
                pasos_texto.insert(tk.END, paso_desc)
                imprimir_matriz_en_texto(matriz, pasos_texto)

        pivote_fila += 1
        pivote_col += 1
    
    pasos_texto.insert(tk.END, "\n--- Matriz Final en Forma Escalonada (Triangular) ---\n")
    imprimir_matriz_en_texto(matriz, pasos_texto)
    return matriz

def analizar_solucion(matriz_reducida):
    """
    Analiza la matriz en forma escalonada (REF) para determinar la solución.
    Implementa la sustitución hacia atrás.
    """
    if not matriz_reducida:
        return "No se ha ingresado una matriz.", []

    filas = len(matriz_reducida)
    incognitas = len(matriz_reducida[0]) - 1
    
    # 1. Verificar inconsistencia (0 0 ... 0 | b) donde b != 0
    for i in range(filas):
        fila = matriz_reducida[i]
        suma_coeficientes = sum(abs(c) for c in fila[:incognitas])
        if suma_coeficientes < 1e-9 and abs(fila[incognitas]) > 1e-9:
            return "El sistema no tiene solución (Inconsistente).", []

    # 2. Verificar infinitas soluciones (rango < n)
    rango = sum(1 for fila in matriz_reducida if any(abs(c) > 1e-9 for c in fila))
    if rango < incognitas:
        return "El sistema tiene infinitas soluciones (variables libres).", []

    # --- CAMBIO CLAVE: Sustitución Hacia Atrás ---
    # 3. Solución única
    soluciones = [0.0] * incognitas
    
    # Iterar desde la última fila con pivote (rango-1) hacia arriba (hasta 0)
    for i in range(rango - 1, -1, -1):
        
        # Encontrar el pivote (primer no-cero) en esta fila
        pivote_col_idx = -1
        for j in range(incognitas):
            if abs(matriz_reducida[i][j]) > 1e-9:
                pivote_col_idx = j
                break
        
        if pivote_col_idx == -1: continue # Fila de ceros, saltar

        # Obtener el valor del lado derecho (término constante)
        suma = matriz_reducida[i][incognitas]
        
        # Restar los valores de las variables ya conocidas (las de la derecha)
        for j in range(pivote_col_idx + 1, incognitas):
            suma -= matriz_reducida[i][j] * soluciones[j]
            
        # Dividir por el coeficiente del pivote para hallar la variable
        # x_i = (B[i] - sum_de_conocidas) / A[i][i]
        soluciones[pivote_col_idx] = suma / matriz_reducida[i][pivote_col_idx]
    
    return "El sistema tiene una solución única (por Sustitución Hacia Atrás):", soluciones


def imprimir_matriz_en_texto(matriz, widget_texto):
    """Formatea e imprime la matriz en el widget de texto de la GUI."""
    if not matriz: return
    max_len = max(len(f"{val:.2f}") for fila in matriz for val in fila) if matriz else 0
    texto_matriz = ""
    for fila in matriz:
        texto_fila = " | ".join(f"{val:>{max_len}.2f}" for val in fila)
        texto_matriz += f"| {texto_fila} |\n"
    widget_texto.insert(tk.END, texto_matriz + "\n")
    widget_texto.see(tk.END)

# --- Interfaz Gráfica de Usuario (GUI) con Tkinter ---

class AppEliminacionGaussiana: # Renombrado de AppGaussJordan
    def __init__(self, root):
        self.root = root
        # Título actualizado
        self.root.title("Calculadora de Eliminación Gaussiana")
        self.root.geometry("950x700")
        self.root.configure(bg="#2E2E2E")
        
        # Estilos
        self.default_font = font.Font(family="Arial", size=10)
        self.title_font = font.Font(family="Arial", size=14, weight="bold")
        self.mono_font = font.Font(family="Courier New", size=10)
        self.entradas_matriz = []

        # --- Frame principal ---
        main_frame = tk.Frame(root, bg="#2E2E2E")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # --- Frame de Configuración (Izquierda) ---
        setup_frame = tk.Frame(main_frame, bg="#3C3C3C", relief="ridge", borderwidth=2, padx=10, pady=10)
        setup_frame.pack(side="left", fill="y", padx=(0, 10))
        
        tk.Label(setup_frame, text="Configuración del Sistema", font=self.title_font, bg="#3C3C3C", fg="#FFFFFF").pack(pady=(0, 15))
        
        dim_frame = tk.Frame(setup_frame, bg="#3C3C3C")
        dim_frame.pack(pady=5, padx=10)
        tk.Label(dim_frame, text="Ecuaciones:", font=self.default_font, bg="#3C3C3C", fg="#FFFFFF").grid(row=0, column=0, sticky="w")
        self.filas_var = tk.StringVar(value="3")
        self.filas_entry = tk.Entry(dim_frame, textvariable=self.filas_var, width=5)
        self.filas_entry.grid(row=0, column=1)
        tk.Label(dim_frame, text="Incógnitas:", font=self.default_font, bg="#3C3C3C", fg="#FFFFFF").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.cols_var = tk.StringVar(value="3")
        self.cols_entry = tk.Entry(dim_frame, textvariable=self.cols_var, width=5)
        self.cols_entry.grid(row=1, column=1, pady=(5,0))

        actions_frame = tk.Frame(setup_frame, bg="#3C3C3C")
        actions_frame.pack(pady=15)
        tk.Button(actions_frame, text="Crear Matriz", command=self.crear_grid_matriz, bg="#007ACC", fg="#FFFFFF", relief="flat").pack(side="left", padx=5)
        tk.Button(actions_frame, text="Ejemplo Aleatorio", command=self.generar_ejemplo_aleatorio, bg="#9C27B0", fg="#FFFFFF", relief="flat").pack(side="left", padx=5)
        tk.Button(actions_frame, text="Limpiar Matriz", command=self.limpiar_matriz, bg="#F44336", fg="#FFFFFF", relief="flat").pack(side="left", padx=5)
        
        self.matriz_frame = tk.Frame(setup_frame, bg="#3C3C3C")
        self.matriz_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        tk.Button(setup_frame, text="Resolver Sistema", command=self.resolver, font=self.default_font, bg="#4CAF50", fg="#FFFFFF", relief="flat", height=2).pack(side="bottom", pady=10, fill="x")
        
        # --- Frame de Resultados (Derecha) ---
        results_frame = tk.Frame(main_frame, bg="#3C3C3C")
        results_frame.pack(side="right", fill="both", expand=True)
        
        tk.Label(results_frame, text="Procedimiento Paso a Paso", font=self.title_font, bg="#3C3C3C", fg="#FFFFFF").pack(pady=10)
        self.pasos_texto = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20, font=self.mono_font, bg="#1E1E1E", fg="#D4D4D4", relief="sunken", borderwidth=1, insertbackground="#FFFFFF")
        self.pasos_texto.pack(pady=5, padx=10, expand=True, fill="both")
        
        tk.Label(results_frame, text="Solución Final", font=self.title_font, bg="#3C3C3C", fg="#FFFFFF").pack(pady=(15, 5))
        
        self.solucion_widget = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=8, font=self.default_font, bg="#1E1E1E", fg="#4CAF50", relief="sunken", borderwidth=1)
        self.solucion_widget.pack(pady=5, padx=10, fill="x")
        self.solucion_widget.config(state="disabled") 

        self.crear_grid_matriz()

    def crear_grid_matriz(self):
        for widget in self.matriz_frame.winfo_children(): widget.destroy()
        self.entradas_matriz = []
        try:
            filas = int(self.filas_var.get())
            cols = int(self.cols_var.get())
            if filas <= 0 or cols <= 0:
                messagebox.showwarning("Dimensiones Inválidas", "Las filas y columnas deben ser mayores que cero.")
                return
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce números enteros para las dimensiones.")
            return
        
        for i in range(filas):
            fila_entradas = []
            for j in range(cols + 1):
                entry = tk.Entry(self.matriz_frame, width=5, justify="center")
                entry.grid(row=i, column=j, padx=2, pady=2)
                if j == cols: entry.configure(bg="#252526", fg="#FFFFFF", insertbackground="#FFFFFF")
                fila_entradas.append(entry)
            self.entradas_matriz.append(fila_entradas)
    
    def generar_ejemplo_aleatorio(self):
        if not self.entradas_matriz:
            messagebox.showwarning("Matriz no creada", "Primero debes hacer clic en 'Crear Matriz' para definir las dimensiones.")
            return
        self.limpiar_resultados()
        for fila_entradas in self.entradas_matriz:
            for entry in fila_entradas:
                num_aleatorio = random.randint(-9, 9)
                entry.delete(0, tk.END)
                entry.insert(0, str(num_aleatorio))

    def limpiar_matriz(self):
        for fila_entradas in self.entradas_matriz:
            for entry in fila_entradas:
                entry.delete(0, tk.END)
        self.limpiar_resultados()

    def limpiar_resultados(self):
        self.pasos_texto.delete(1.0, tk.END)
        self.solucion_widget.config(state="normal")
        self.solucion_widget.delete(1.0, tk.END)
        self.solucion_widget.config(state="disabled")

    def resolver(self):
        self.limpiar_resultados()
        try:
            matriz_aumentada = []
            for i in range(len(self.entradas_matriz)):
                fila = []
                for j in range(len(self.entradas_matriz[0])):
                    valor_str = self.entradas_matriz[i][j].get()
                    if not valor_str:
                        messagebox.showwarning("Entrada inválida", f"La celda en la fila {i+1}, columna {j+1} está vacía.")
                        return
                    fila.append(float(valor_str))
                matriz_aumentada.append(fila)
        except ValueError:
            messagebox.showerror("Error de Datos", "Por favor, introduce solo números válidos en la matriz.")
            return
            
        matriz_reducida = resolver_sistema(matriz_aumentada, self.pasos_texto)
        
        mensaje, solucion = analizar_solucion(matriz_reducida)
        texto_solucion = mensaje
        if solucion:
            sol_formateada = "\n" + "\n".join([f"x{i+1} = {s:.4f}" for i, s in enumerate(solucion)])
            texto_solucion += sol_formateada
        
        self.solucion_widget.config(state="normal")
        self.solucion_widget.insert(tk.END, texto_solucion)
        self.solucion_widget.config(state="disabled")

def main():
    """
    Función principal que lanza la calculadora de Eliminación Gaussiana.
    """
    root = tk.Toplevel() # Usar Toplevel para que se abra sobre el menú principal
    root.grab_set() # Modal
    app = AppEliminacionGaussiana(root)
    root.mainloop()

if __name__ == "__main__":
    # Esto permite probar el módulo de forma independiente
    root_main = tk.Tk()
    app = AppEliminacionGaussiana(root_main)
    root_main.mainloop()
