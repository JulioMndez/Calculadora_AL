import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import random # Para el botón de ejemplo aleatorio

# ============================================================
# === FUNCIONES DE LÓGICA (Cálculo) ==========================
# ============================================================

def matrix_to_text(matrix, tol=1e-12):
    """
    Convierte una matriz (lista de listas) en un string formateado
    con alineación de columnas.
    """
    if not matrix:
        return "(Matriz vacía)"
        
    lines = []
    str_matrix = []
    max_lens = [0] * len(matrix[0])

    # Convertir todos los números a string y encontrar el ancho máximo de columna
    for i, row in enumerate(matrix):
        str_matrix.append([])
        for j, x in enumerate(row):
            s_val = ""
            if abs(round(x) - x) < tol:
                s_val = str(int(round(x)))
            else:
                s_val = f"{x:.6f}".rstrip('0').rstrip('.')
            
            str_matrix[i].append(s_val)
            max_lens[j] = max(max_lens[j], len(s_val))

    # Formatear las líneas con el ancho de columna
    for row in str_matrix:
        parts = []
        for j, s_val in enumerate(row):
            # Alinear a la derecha
            parts.append(f"{s_val:>{max_lens[j]}}")
        lines.append("   ".join(parts)) # Usar 3 espacios como separador
    return "\n".join(lines)

def imprimir_matriz_text(matriz, titulo="Matriz:"):
    """Formato de matriz mejorado para el log de pasos."""
    if not matriz:
        return f"\n{titulo}\n(Matriz vacía)\n"
    
    filas = len(matriz)
    cols = len(matriz[0])
    # Detectar si es matriz aumentada [A|I] (cols == 2*filas)
    es_aumentada = (filas * 2 == cols)
    
    max_lens = [0] * cols
    for fila in matriz:
        for j, val in enumerate(fila):
            # Usar un formato consistente para medir
            s_val = f"{val:.4f}"
            max_lens[j] = max(max_lens[j], len(s_val.strip()))
    
    s = f"\n{titulo}\n"
    for fila in matriz:
        s += "| "
        for j, val in enumerate(fila):
            # Añadir separador para [A|I]
            if es_aumentada and j == filas:
                s += "  |  "
            s += f"{val:>{max_lens[j]+2}.4f} "
        s += "|\n"
    s += "\n"
    return s

def multiply_matrices_step(a, b):
    """Multiplica dos matrices y devuelve el log del paso a paso."""
    if len(a[0]) != len(b):
        raise ValueError("Número de columnas de A debe igualar número de filas de B para multiplicar.")
    rows, cols, inner = len(a), len(b[0]), len(b)
    result = [[0.0 for _ in range(cols)] for _ in range(rows)]
    salida = ""
    for i in range(rows):
        for j in range(cols):
            salida += f"Calculando elemento ({i+1},{j+1}): "
            total = 0.0
            for k in range(inner):
                salida += f"{a[i][k]:.3f}*{b[k][j]:.3f}"
                total += a[i][k]*b[k][j]
                if k < inner-1:
                    salida += " + "
            salida += f" = {total:.6f}\n"
            result[i][j] = total
    salida += "\nResultado de la multiplicación:\n"
    salida += matrix_to_text(result) # Usar la nueva función de formato
    return salida, result

def invertir_matriz_pasoa_paso(A, tol=1e-12):
    """
    Calcula la inversa de la matriz A usando Gauss-Jordan y retorna un string 
    con todo el procedimiento.
    Si la matriz es singular, retorna el string explicando el error.
    """
    n = len(A)
    # Pequeña validación por si acaso (aunque la GUI ya la hace)
    if n == 0 or any(len(fila) != n for fila in A):
        raise ValueError("La matriz debe ser cuadrada.")

    M = [A[i][:] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    salida = imprimir_matriz_text(M, "Matriz aumentada [A | I] inicial:")

    for i in range(n):
        max_fila = i
        for k in range(i + 1, n):
            if abs(M[k][i]) > abs(M[max_fila][i]):
                max_fila = k
        
        if abs(M[max_fila][i]) < tol:
            salida += f"\n--- ERROR: PROCESO DETENIDO EN LA COLUMNA {i+1} ---\n"
            salida += "La matriz es singular y NO tiene inversa.\n\n"
            salida += f"RAZÓN: No se pudo encontrar un pivote (un valor no-cero) en la columna {i+1} (o las filas restantes).\n"
            salida += "Esto significa que el determinante de la matriz es 0.\n\n"
            salida += "Matriz en el momento del fallo (observe la columna de ceros en el lado izquierdo):\n"
            salida += imprimir_matriz_text(M, "Matriz [A|I] a medio reducir:")
            return salida 

        if max_fila != i:
            M[i], M[max_fila] = M[max_fila], M[i]
            salida += f"Intercambio fila {i+1} ↔ fila {max_fila+1}\n"
            salida += imprimir_matriz_text(M, f"Después del intercambio:")

        pivote = M[i][i]
        salida += f"Normalizando fila {i+1} (F{i+1} = F{i+1} / {pivote:.4f})\n"
        for j in range(2 * n):
            M[i][j] /= pivote
        salida += imprimir_matriz_text(M, f"Después de normalizar fila {i+1}:")

        for k in range(n):
            if k != i:
                factor = M[k][i]
                if abs(factor) > tol:
                    salida += f"Eliminando en fila {k+1} (F{k+1} = F{k+1} - {factor:.4f} * F{i+1})\n"
                    for j in range(2 * n):
                        M[k][j] -= factor * M[i][j]
                    salida += imprimir_matriz_text(M, f"Después de eliminar en fila {k+1}:")

    inversa = [fila[n:] for fila in M]
    salida += imprimir_matriz_text(M, "Matriz reducida final [I | A⁻¹]:")
    salida += "\nInversa de A (extraída de la derecha):\n"
    salida += matrix_to_text(inversa) + "\n" # Usar la nueva función de formato

    salida += "\nComprobación: A * A⁻¹ (debe dar la matriz Identidad)\n"
    mult_texto, mult_result = multiply_matrices_step(A, inversa)
    salida += mult_texto + "\n"

    identidad = [[1.0 if i==j else 0.0 for j in range(n)] for i in range(n)]
    es_identidad = all(abs(mult_result[i][j]-identidad[i][j])<0.001 for i in range(n) for j in range(n))
    salida += "Comprobación final: "
    salida += "Correcta (producto ≈ identidad)\n" if es_identidad else "Incorrecta (producto no es identidad)\n"

    return salida

# ============================================================
# === INTERFAZ GRÁFICA (REDISÑADA) ===========================
# ============================================================

class AppInversa:
    def __init__(self, root):
        self.root = root
        self.root.title("Inversión de Matriz (Gauss-Jordan) con Verificación")
        self.root.geometry("950x700")
        self.root.configure(bg="#2E2E2E")
        
        # --- Definición de paleta y fuentes ---
        self.BG_COLOR = "#2E2E2E"
        self.FRAME_COLOR = "#3C3C3C"
        self.TEXT_AREA_BG = "#1E1E1E"
        self.TEXT_COLOR = "#D4D4D4"
        self.BUTTON_GREEN = "#4CAF50"
        self.BUTTON_GREEN_HOVER = "#81C784"
        self.BUTTON_RED = "#D32F2F"
        self.BUTTON_RED_HOVER = "#E57373"
        self.BUTTON_BLUE = "#007ACC"
        self.BUTTON_BLUE_HOVER = "#00AFFF"
        self.BUTTON_PURPLE = "#9C27B0"
        self.BUTTON_PURPLE_HOVER = "#BA68C8"
        
        self.TITLE_FONT = font.Font(family="Arial", size=14, weight="bold")
        self.DEFAULT_FONT = font.Font(family="Arial", size=10)
        self.BUTTON_FONT = font.Font(family="Arial", size=10, weight="bold")
        self.MONO_FONT = font.Font(family="Courier New", size=10)
        
        self.entradas_matriz = []

        # --- Frame principal ---
        main_frame = tk.Frame(root, bg=self.BG_COLOR)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # --- Frame de Configuración (Izquierda) ---
        setup_frame = tk.Frame(main_frame, bg=self.FRAME_COLOR, relief="ridge", borderwidth=2, padx=10, pady=10)
        setup_frame.pack(side="left", fill="y", padx=(0, 10))
        
        tk.Label(setup_frame, text="Configuración", font=self.TITLE_FONT, bg=self.FRAME_COLOR, fg="#FFFFFF").pack(pady=(0, 15))
        
        dim_frame = tk.Frame(setup_frame, bg=self.FRAME_COLOR)
        dim_frame.pack(pady=5, padx=10)
        tk.Label(dim_frame, text="Dimensión (N x N):", font=self.DEFAULT_FONT, bg=self.FRAME_COLOR, fg="#FFFFFF").grid(row=0, column=0, sticky="w")
        self.dim_var = tk.StringVar(value="3")
        self.dim_entry = tk.Entry(dim_frame, textvariable=self.dim_var, width=5, justify="center")
        self.dim_entry.grid(row=0, column=1, padx=5)

        # --- Botones de acción ---
        actions_frame = tk.Frame(setup_frame, bg=self.FRAME_COLOR)
        actions_frame.pack(pady=15)
        
        self.btn_crear = tk.Button(actions_frame, text="Crear Matriz", command=self.crear_grid_matriz, 
                                   font=self.BUTTON_FONT, bg=self.BUTTON_BLUE, fg="#FFFFFF", 
                                   relief="flat", activebackground=self.BUTTON_BLUE_HOVER, padx=5, pady=5)
        self.btn_crear.pack(side="left", padx=5)
        
        self.btn_ejemplo = tk.Button(actions_frame, text="Ejemplo Aleatorio", command=self.generar_ejemplo_aleatorio,
                                     font=self.BUTTON_FONT, bg=self.BUTTON_PURPLE, fg="#FFFFFF", 
                                     relief="flat", activebackground=self.BUTTON_PURPLE_HOVER, padx=5, pady=5)
        self.btn_ejemplo.pack(side="left", padx=5)
        
        self.btn_limpiar = tk.Button(actions_frame, text="Limpiar Matriz", command=self.limpiar_matriz,
                                     font=self.BUTTON_FONT, bg=self.BUTTON_RED, fg="#FFFFFF", 
                                     relief="flat", activebackground=self.BUTTON_RED_HOVER, padx=5, pady=5)
        self.btn_limpiar.pack(side="left", padx=5)

        # Asignar efectos hover
        self.btn_crear.bind("<Enter>", lambda e: e.widget.config(bg=self.BUTTON_BLUE_HOVER))
        self.btn_crear.bind("<Leave>", lambda e: e.widget.config(bg=self.BUTTON_BLUE))
        self.btn_ejemplo.bind("<Enter>", lambda e: e.widget.config(bg=self.BUTTON_PURPLE_HOVER))
        self.btn_ejemplo.bind("<Leave>", lambda e: e.widget.config(bg=self.BUTTON_PURPLE))
        self.btn_limpiar.bind("<Enter>", lambda e: e.widget.config(bg=self.BUTTON_RED_HOVER))
        self.btn_limpiar.bind("<Leave>", lambda e: e.widget.config(bg=self.BUTTON_RED))

        # --- Frame para la cuadrícula de la matriz ---
        self.matriz_frame = tk.Frame(setup_frame, bg=self.FRAME_COLOR)
        self.matriz_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        # --- Botón principal de cálculo ---
        self.btn_calcular = tk.Button(setup_frame, text="Calcular Inversa y Verificar", command=self.calcular_inversa, 
                                      font=self.BUTTON_FONT, bg=self.BUTTON_GREEN, fg="#FFFFFF", 
                                      relief="flat", activebackground=self.BUTTON_GREEN_HOVER, height=2)
        self.btn_calcular.pack(side="bottom", pady=10, fill="x")
        self.btn_calcular.bind("<Enter>", lambda e: e.widget.config(bg=self.BUTTON_GREEN_HOVER))
        self.btn_calcular.bind("<Leave>", lambda e: e.widget.config(bg=self.BUTTON_GREEN))

        # --- Frame de Resultados (Derecha) ---
        results_frame = tk.Frame(main_frame, bg=self.FRAME_COLOR, relief="ridge", borderwidth=2)
        results_frame.pack(side="right", fill="both", expand=True)
        
        tk.Label(results_frame, text="Resultado Paso a Paso", font=self.TITLE_FONT, bg=self.FRAME_COLOR, fg="#FFFFFF").pack(pady=10)
        
        # --- INICIO: CAMBIO A SCROLL HORIZONTAL Y VERTICAL ---
        text_frame = tk.Frame(results_frame, bg=self.TEXT_AREA_BG, relief="sunken", borderwidth=1)
        text_frame.pack(pady=5, padx=10, expand=True, fill="both")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        v_scroll = ttk.Scrollbar(text_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(text_frame, orient="horizontal")

        self.res = tk.Text(text_frame, wrap=tk.NONE, height=20, # <--- wrap=tk.NONE
                           font=self.MONO_FONT, bg=self.TEXT_AREA_BG, fg=self.TEXT_COLOR, 
                           relief="flat", borderwidth=0, insertbackground="#FFFFFF",
                           yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=self.res.yview)
        h_scroll.config(command=self.res.xview)

        self.res.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        # --- FIN: CAMBIO A SCROLL HORIZONTAL Y VERTICAL ---
        
        self.res.config(state="disabled")

        self.crear_grid_matriz() # Crear la matriz inicial 3x3

    def crear_grid_matriz(self):
        """Crea la cuadrícula de N x N para la entrada de la matriz."""
        try:
            n = int(self.dim_var.get())
            if n <= 0 or n > 20: # Límite para que no colapse la UI
                messagebox.showwarning("Dimensión Inválida", "Por favor, ingrese un número entre 1 y 20.")
                return
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un número entero para la dimensión.")
            return

        # Limpiar frame anterior
        for widget in self.matriz_frame.winfo_children():
            widget.destroy()
        self.entradas_matriz = []

        for i in range(n):
            fila_entradas = []
            for j in range(n):
                entry = tk.Entry(self.matriz_frame, width=5, justify="center",
                                 bg=self.TEXT_AREA_BG, fg=self.TEXT_COLOR, 
                                 insertbackground="#FFFFFF", relief="solid", borderwidth=1)
                entry.grid(row=i, column=j, padx=2, pady=2)
                fila_entradas.append(entry)
            self.entradas_matriz.append(fila_entradas)
    
    def get_matrix_from_grid(self):
        """Lee los valores de la cuadrícula y los devuelve como una matriz (lista de listas)."""
        matriz = []
        try:
            n = len(self.entradas_matriz)
            if n == 0:
                raise ValueError("La cuadrícula de la matriz no ha sido creada.")
            
            for i in range(n):
                fila = []
                for j in range(n):
                    valor_str = self.entradas_matriz[i][j].get()
                    if not valor_str:
                        raise ValueError(f"La celda en la fila {i+1}, columna {j+1} está vacía.")
                    fila.append(float(valor_str))
                matriz.append(fila)
            
            # Validación final de que sea cuadrada (aunque la GUI lo fuerza)
            if len(matriz) != len(matriz[0]):
                 raise ValueError(f"Error interno: La matriz leída no es cuadrada ({len(matriz)}x{len(matriz[0])}).")
            
            return matriz
        except ValueError as e:
            # Relanzar para que sea capturado por 'calcular_inversa'
            raise ValueError(f"Error al leer la matriz: {e}")
        except IndexError:
             raise ValueError("Error al leer la matriz. Intente 'Crear Matriz' de nuevo.")


    def generar_ejemplo_aleatorio(self):
        """Rellena la matriz actual con enteros aleatorios."""
        if not self.entradas_matriz:
            messagebox.showwarning("Matriz no creada", "Primero debes hacer clic en 'Crear Matriz'.")
            return
        
        self.limpiar_resultados()
        for fila_entradas in self.entradas_matriz:
            for entry in fila_entradas:
                num_aleatorio = random.randint(-9, 9)
                entry.delete(0, tk.END)
                entry.insert(0, str(num_aleatorio))

    def limpiar_matriz(self):
        """Borra todos los valores de las celdas de la matriz."""
        for fila_entradas in self.entradas_matriz:
            for entry in fila_entradas:
                entry.delete(0, tk.END)
        self.limpiar_resultados()

    def limpiar_resultados(self):
        """Limpia el widget de texto de resultados."""
        self.res.config(state="normal")
        self.res.delete(1.0, tk.END)
        self.res.config(fg=self.TEXT_COLOR) # Resetear color de texto
        self.res.config(state="disabled")

    def calcular_inversa(self):
        """Manejador del botón para calcular la inversa."""
        self.limpiar_resultados()
        self.res.config(state="normal")
        
        try:
            matriz = self.get_matrix_from_grid()
            pasos = invertir_matriz_pasoa_paso([fila[:] for fila in matriz])
            self.res.insert(tk.END, pasos)
            
            if "--- ERROR:" in pasos:
                self.res.config(fg="#FF6B6B") # Rojo brillante
            else:
                self.res.config(fg=self.TEXT_COLOR)
                
        except Exception as e:
            messagebox.showerror("Error de Entrada", str(e))
            self.res.config(fg="#FF6B6B")
            self.res.insert(tk.END, f"Error de Entrada: {e}")
        
        self.res.config(state="disabled") # Siempre deshabilitar al final

# ============================================================
# === EJECUCIÓN PRINCIPAL ===================================
# ============================================================

def main():
    """Función que se ejecuta al abrir el módulo desde el menú principal."""
    sub_root = tk.Toplevel()
    sub_root.grab_set() 
    app = AppInversa(sub_root)
    sub_root.mainloop()

if __name__ == "__main__":
    root_main = tk.Tk()
    app = AppInversa(root_main)
    root_main.mainloop()

