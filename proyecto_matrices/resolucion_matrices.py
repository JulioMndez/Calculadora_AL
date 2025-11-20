

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from tkinter import scrolledtext

EPS = 1e-9

def copiar_matriz(m):
    return [fila[:] for fila in m]

#Es una función de redondeo para números con decimales muy pequeños
def format_num(x):
    if abs(x) < EPS:
        return "0"
    # si es entero
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.4f}".rstrip('0').rstrip('.')


def matriz_a_texto(matriz):
    # Convierte la matriz aumentada a texto formateado (monoespaciado)
    lines = []
    if not matriz:
        return ""
    cols = len(matriz[0])
    vars_count = cols - 1
    # calcular anchuras por columna para alineado
    anchuras = [0] * cols
    for j in range(cols):
        for i in range(len(matriz)):
            anchuras[j] = max(anchuras[j], len(format_num(matriz[i][j])))
    # construir líneas
    for i, fila in enumerate(matriz):
        izq = "  ".join(format_num(fila[j]).rjust(anchuras[j]) for j in range(vars_count))
        der = format_num(fila[-1]).rjust(anchuras[-1])
        lines.append(f"[ {izq}  |  {der} ]")
    return "\n".join(lines)


def rref_con_pasos(matriz):
    A = copiar_matriz(matriz)
    R = len(A)
    C = len(A[0]) if R > 0 else 0
    vars_count = C - 1

    pasos = []  # lista de (descripcion, copia_matriz)
    pivot_col_to_row = {}
    r = 0

    for c in range(vars_count):
        # buscar fila con mayor valor absoluto en columna c (desde r hacia abajo)
        sel = None
        maxval = 0.0
        for i in range(r, R):
            if abs(A[i][c]) > maxval + EPS:
                maxval = abs(A[i][c])
                sel = i
        if sel is None or abs(A[sel][c]) < EPS:
            # no hay pivote en esta columna
            continue

        # intercambiar
        if sel != r:
            A[r], A[sel] = A[sel], A[r]
            pasos.append((f"Intercambio: fila {r+1} <-> fila {sel+1}  (para pivote en columna {c+1})", copiar_matriz(A)))

        # normalizar fila r para que pivote sea 1
        piv = A[r][c]
        if abs(piv) < EPS:
            continue
        A[r] = [x / piv for x in A[r]]
        pasos.append((f"Normalizar: fila {r+1} (pivote en columna {c+1}) -> dividir por {format_num(piv)}", copiar_matriz(A)))

        # eliminar en la columna c todas las otras filas
        for i in range(R):
            if i != r and abs(A[i][c]) > EPS:
                factor = A[i][c]
                A[i] = [A[i][j] - factor * A[r][j] for j in range(C)]
                pasos.append((f"Eliminación: usar fila {r+1} para anular fila {i+1} (factor = {format_num(factor)})", copiar_matriz(A)))

        pivot_col_to_row[c] = r
        r += 1
        if r == R:
            break

    return A, pivot_col_to_row, pasos


def analizar_solucion(A, pivot_map):
    R = len(A)
    C = len(A[0])
    vars_count = C - 1

    # comprobar inconsistencia: fila de ceros en coef y término distinto de 0
    for i in range(R):
        all_zero = True
        for j in range(vars_count):
            if abs(A[i][j]) > EPS:
                all_zero = False
                break
        if all_zero and abs(A[i][-1]) > EPS:
            return "inconsistente", None

    rank = len(pivot_map)
    if rank == vars_count:
        # solución única: valores directos desde las filas pivote
        sol = [0.0] * vars_count
        for col, row in pivot_map.items():
            sol[col] = A[row][-1]
        return "única", sol

    # infinitas soluciones -> variables libres
    free_cols = [c for c in range(vars_count) if c not in pivot_map]
    params = [f"t{idx+1}" for idx in range(len(free_cols))]
    free_name = {free_cols[i]: params[i] for i in range(len(free_cols))}

    param = {}
    for c in range(vars_count):
        if c in free_cols:
            param[c] = (True, free_name[c])
        else:
            row = pivot_map[c]
            constante = A[row][-1]
            dependencias = []
            for fc in free_cols:
                coef = -A[row][fc]
                if abs(coef) > EPS:
                    dependencias.append((coef, free_name[fc]))
            param[c] = (False, constante, dependencias)

    return "infinitas", (param, free_cols, params)

# -----------------------------
# Interfaz Gráfica
# -----------------------------

class GaussJordanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gauss-Jordan — Paso a paso")
        self.root.geometry("980x680")

        # Estilos
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TFrame', background='#f5f7fa')
        style.configure('TLabel', background='#f5f7fa')
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'), background='#f5f7fa')
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))

        # fuente monoespaciada para matrices
        self.mono = tkfont.Font(family='Courier', size=10)
        self.bold = tkfont.Font(family='Helvetica', size=10, weight='bold')

        # Layout principal
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Input: número de ecuaciones y variables
        input_frame = ttk.Frame(top_frame)
        input_frame.pack(side=tk.LEFT, anchor='nw')

        ttk.Label(input_frame, text="Número de ecuaciones:", font=('Helvetica', 10)).grid(row=0, column=0, sticky='w')
        self.n_entry = ttk.Entry(input_frame, width=6)
        self.n_entry.grid(row=0, column=1, padx=6)

        ttk.Label(input_frame, text="Número de incógnitas:", font=('Helvetica', 10)).grid(row=0, column=2, sticky='w')
        self.v_entry = ttk.Entry(input_frame, width=6)
        self.v_entry.grid(row=0, column=3, padx=6)

        ttk.Button(input_frame, text="Crear matriz", style='Accent.TButton', command=self.crear_matriz).grid(row=0, column=4, padx=8)
        ttk.Button(input_frame, text="Cargar ejemplo", command=self.cargar_ejemplo).grid(row=0, column=5, padx=8)
        ttk.Button(input_frame, text="Limpiar", command=self.limpiar_todo).grid(row=0, column=6, padx=8)

        # Frame central: matriz de entrada a la izquierda, información y botones a la derecha
        center = ttk.Frame(root, padding=(10,5))
        center.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.matriz_frame = ttk.LabelFrame(center, text="Matriz aumentada (coeficientes | término)", padding=8)
        self.matriz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        right_frame = ttk.Frame(center)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12,0))

        # Panel de controles en la derecha
        controls = ttk.Frame(right_frame)
        controls.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(controls, text="Resolver", command=self.resolver).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Exportar RREF (texto)", command=self.exportar_rref).pack(side=tk.LEFT, padx=4)

        # Panel de información (pivotes, tipo de solución, variables libres)
        info_box = ttk.LabelFrame(right_frame, text="Información de la solución", padding=8)
        info_box.pack(side=tk.TOP, fill=tk.X, pady=(8,6))

        ttk.Label(info_box, text="Tipo de sistema:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky='w')
        self.tipo_label = ttk.Label(info_box, text="-", font=('Helvetica', 10))
        self.tipo_label.grid(row=0, column=1, sticky='w', padx=6)

        ttk.Label(info_box, text="Columnas pivote:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky='w')
        self.pivotes_label = ttk.Label(info_box, text="-", font=('Helvetica', 10))
        self.pivotes_label.grid(row=1, column=1, sticky='w', padx=6)

        ttk.Label(info_box, text="Variables libres:", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky='w')
        self.libres_label = ttk.Label(info_box, text="-", font=('Helvetica', 10))
        self.libres_label.grid(row=2, column=1, sticky='w', padx=6)

        # Solución final en bloque
        sol_box = ttk.LabelFrame(right_frame, text="Solución (compacta)", padding=8)
        sol_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(8,6))
        self.sol_text = scrolledtext.ScrolledText(sol_box, height=8, font=self.mono)
        self.sol_text.pack(fill=tk.BOTH, expand=True)
        self.sol_text.configure(state='disabled')

        # Panel de pasos abajo (matrices intermedias y descripciones)
        pasos_box = ttk.LabelFrame(root, text="Pasos del método (Gauss-Jordan)", padding=8)
        pasos_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(4,10))

        self.pasos_text = scrolledtext.ScrolledText(pasos_box, font=self.mono)
        self.pasos_text.pack(fill=tk.BOTH, expand=True)
        self.pasos_text.configure(state='disabled')

        # almacenamiento de entradas
        self.entries = []
        self.ultima_rref = None
        self.ultima_pivot_map = None

    # -----------------------------
    # Funciones de GUI
    # -----------------------------
    def crear_matriz(self):
        # limpiar frame
        for widget in self.matriz_frame.winfo_children():
            widget.destroy()
        self.entries = []

        try:
            n = int(self.n_entry.get())
            v = int(self.v_entry.get())
            if n <= 0 or v <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Ingrese números válidos para ecuaciones y variables (enteros > 0).")
            return

        # crear grid de entradas
        for i in range(n):
            fila_entries = []
            for j in range(v + 1):
                e = ttk.Entry(self.matriz_frame, width=8, justify='center')
                e.grid(row=i, column=j, padx=3, pady=3)
                # hint visual en la primera fila para separar coef | término
                if j == v:
                    e.config(background='#fff8dc')
                fila_entries.append(e)
            self.entries.append(fila_entries)

        # etiqueta de columnas encima
        for j in range(v):
            lbl = ttk.Label(self.matriz_frame, text=f"x{j+1}", font=self.bold)
            lbl.grid(row=-1, column=j, pady=(0,4))
        lbl = ttk.Label(self.matriz_frame, text="b", font=self.bold)
        lbl.grid(row=-1, column=v, pady=(0,4))

    def cargar_ejemplo(self):
        # Ejemplo con variables libres (2 ecuaciones, 3 incógnitas)
        self.n_entry.delete(0, tk.END)
        self.v_entry.delete(0, tk.END)
        self.n_entry.insert(0, '2')
        self.v_entry.insert(0, '3')
        self.crear_matriz()
        ejemplo = [[1,1,1,2], [2,3,1,5]]
        for i in range(2):
            for j in range(4):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(ejemplo[i][j]))

    def limpiar_todo(self):
        # limpiar entradas, resultados y pasos
        for widget in self.matriz_frame.winfo_children():
            widget.destroy()
        self.entries = []
        self.pasos_text.configure(state='normal')
        self.pasos_text.delete(1.0, tk.END)
        self.pasos_text.configure(state='disabled')
        self.sol_text.configure(state='normal')
        self.sol_text.delete(1.0, tk.END)
        self.sol_text.configure(state='disabled')
        self.tipo_label.config(text='-')
        self.pivotes_label.config(text='-')
        self.libres_label.config(text='-')
        self.n_entry.delete(0, tk.END)
        self.v_entry.delete(0, tk.END)
        self.ultima_rref = None
        self.ultima_pivot_map = None

    def leer_matriz_desde_gui(self):
        if not self.entries:
            messagebox.showerror("Error", "Primero cree la matriz.")
            return None
        matriz = []
        try:
            for i, fila in enumerate(self.entries):
                fila_vals = []
                for j, e in enumerate(fila):
                    val = e.get().strip()
                    if val == '':
                        val = '0'
                    fila_vals.append(float(val))
                matriz.append(fila_vals)
        except Exception:
            messagebox.showerror("Error", "Todas las celdas deben contener números (use punto . para decimales).")
            return None
        return matriz

    def resolver(self):
        matriz = self.leer_matriz_desde_gui()
        if matriz is None:
            return
        if not matriz:
            messagebox.showerror("Error", "La matriz está vacía.")
            return

        # mostrar matriz inicial
        self.pasos_text.configure(state='normal')
        self.pasos_text.delete(1.0, tk.END)
        self.pasos_text.insert(tk.END, "Matriz inicial:\n")
        self.pasos_text.insert(tk.END, matriz_a_texto(matriz) + "\n\n")

        A_final, pivot_map, pasos = rref_con_pasos(matriz)

        # mostrar pasos
        for idx, (desc, mat) in enumerate(pasos):
            self.pasos_text.insert(tk.END, f"Paso {idx+1}: {desc}\n")
            self.pasos_text.insert(tk.END, matriz_a_texto(mat) + "\n\n")

        # Analizar y mostrar solución
        resultado, datos = analizar_solucion(A_final, pivot_map)

        if resultado == 'inconsistente':
            tipo = 'Sistema inconsistente (sin solución)'
            self.tipo_label.config(text=tipo)
            self.pivotes_label.config(text='-')
            self.libres_label.config(text='-')
            self.sol_text.configure(state='normal')
            self.sol_text.delete(1.0, tk.END)
            self.sol_text.insert(tk.END, "El sistema no tiene solución. Hay una fila 0 ... | b con b != 0.")
            self.sol_text.configure(state='disabled')
        elif resultado == 'única':
            tipo = 'Solución única'
            sol = datos
            cols = sorted(pivot_map.keys())
            self.tipo_label.config(text=tipo)
            self.pivotes_label.config(text=', '.join(str(c+1) for c in cols) if cols else '-')
            self.libres_label.config(text='No hay variables libres')
            # mostrar solución
            self.sol_text.configure(state='normal')
            self.sol_text.delete(1.0, tk.END)
            self.sol_text.insert(tk.END, "Solución única:\n")
            for i, val in enumerate(sol):
                self.sol_text.insert(tk.END, f"x{i+1} = {format_num(val)}\n")
            self.sol_text.configure(state='disabled')
        else:
            tipo = 'Infinitas soluciones (paramétrica)'
            param, free_cols, params = datos
            cols = sorted(pivot_map.keys())
            self.tipo_label.config(text=tipo)
            self.pivotes_label.config(text=', '.join(str(c+1) for c in cols) if cols else '-')
            self.libres_label.config(text=', '.join(f"x{c+1}" for c in free_cols) if free_cols else 'Ninguna')

            # construir solución paramétrica en bloque
            self.sol_text.configure(state='normal')
            self.sol_text.delete(1.0, tk.END)
            self.sol_text.insert(tk.END, "Solución paramétrica:\n")
            self.sol_text.insert(tk.END, "{\n")
            vars_count = len(A_final[0]) - 1
            for c in range(vars_count):
                entry = param[c]
                if entry[0]:
                    self.sol_text.insert(tk.END, f"  x{c+1} = {entry[1]}  (libre)\n")
                else:
                    constante = entry[1]
                    deps = entry[2]
                    partes = []
                    if abs(constante) > EPS:
                        partes.append(format_num(constante))
                    for coef, pname in deps:
                        scoef = format_num(coef)
                        if partes:
                            partes.append(("+ " if coef > 0 else "- ") + (scoef if coef > 0 else scoef.lstrip('-')) + f"*{pname}")
                        else:
                            partes.append((scoef if coef < 0 else scoef) + f"*{pname}")
                    rhs = " ".join(partes) if partes else "0"
                    self.sol_text.insert(tk.END, f"  x{c+1} = {rhs}\n")
            self.sol_text.insert(tk.END, "}\n")
            self.sol_text.configure(state='disabled')

        # mostrar matriz final RREF al final
        self.pasos_text.insert(tk.END, "==== Matriz final (RREF) ====" + "\n")
        self.pasos_text.insert(tk.END, matriz_a_texto(A_final) + "\n")
        self.pasos_text.configure(state='disabled')

        # guardar para exportar
        self.ultima_rref = A_final
        self.ultima_pivot_map = pivot_map

    def exportar_rref(self):
        if self.ultima_rref is None:
            messagebox.showinfo("Info", "Primero resuelva una matriz para tener la RREF.")
            return
        # solicitar nombre de archivo simple
        try:
            nombre = 'rref_resultado.txt'
            with open(nombre, 'w', encoding='utf-8') as f:
                f.write("Matriz final (RREF):\n")
                f.write(matriz_a_texto(self.ultima_rref) + "\n\n")
                # tipo de solución
                f.write("Columnas pivote: ")
                if self.ultima_pivot_map:
                    f.write(', '.join(str(c+1) for c in sorted(self.ultima_pivot_map.keys())))
                else:
                    f.write('-')
                f.write('\n')
            messagebox.showinfo("Exportado", f"RREF exportado a {nombre} (en el directorio actual).")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

# -----------------------------
# Ejecutar la aplicación
# -----------------------------

def main():
    ventana = tk.Toplevel()
    app = GaussJordanGUI(ventana)
    ventana.mainloop()

