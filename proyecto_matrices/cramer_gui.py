# ============================================================
#  Cramer GUI paso a paso (Tkinter - sin librerías externas)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ---------- Utilidades numéricas y de impresión ----------

def copiar_matriz(M):
    return [fila[:] for fila in M]

def form_num(x, prec=6):
    s = f"{x:.{prec}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s == "-0":
        s = "0"
    return s

def matriz_a_texto(M, prec=6):
    if not M or not M[0]:
        return "[]\n"
    txt = [[form_num(v, prec) for v in fila] for fila in M]
    col_ancho = [0]*len(M[0])
    for fila in txt:
        for j, cel in enumerate(fila):
            col_ancho[j] = max(col_ancho[j], len(cel))
    lineas = []
    for fila in txt:
        lineas.append("[ " + "  ".join(cel.rjust(col_ancho[j]) for j, cel in enumerate(fila)) + " ]")
    return "\n".join(lineas) + "\n"

def vector_a_texto(v, nombre="b", prec=6):
    return f"{nombre} = [ " + "  ".join(form_num(x, prec) for x in v) + " ]\n"

def determinante_por_eliminacion(M, nombre, prec, logwrite):
    """
    Calcula det(M) por eliminación gaussiana con pivoteo parcial simple.
    Escribe cada paso en logwrite(str).
    Retorna (det, exito_bool).
    """
    n = len(M)
    A = copiar_matriz(M)
    signo = 1.0

    logwrite(f"\n== Cálculo de det({nombre}) por eliminación (Gauss)\nMatriz inicial {nombre}:\n")
    logwrite(matriz_a_texto(A, prec))

    for k in range(n):
        # Buscar pivote máximo en la columna k desde fila k
        piv_row = k
        max_abs = abs(A[k][k])
        for i in range(k+1, n):
            if abs(A[i][k]) > max_abs:
                max_abs = abs(A[i][k])
                piv_row = i
        if max_abs == 0:
            logwrite(f"Columna {k+1}: no hay pivote (todos ceros). det({nombre}) = 0.\n")
            return 0.0, False

        if piv_row != k:
            A[k], A[piv_row] = A[piv_row], A[k]
            signo *= -1.0
            logwrite(f"\nIntercambio de filas R{k+1} <-> R{piv_row+1}  (signo del det cambia)\n")
            logwrite(matriz_a_texto(A, prec))

        pivote = A[k][k]
        logwrite(f"Pivote en (fila {k+1}, col {k+1}) = {form_num(pivote, prec)}\n")

        for i in range(k+1, n):
            if A[i][k] == 0:
                continue
            factor = A[i][k] / pivote
            for j in range(k, n):
                A[i][j] -= factor * A[k][j]
            logwrite(f"R{i+1} = R{i+1} - ({form_num(factor, prec)}) * R{k+1}\n")
            logwrite(matriz_a_texto(A, prec))

    det = signo
    factores = []
    for i in range(n):
        det *= A[i][i]
        factores.append(form_num(A[i][i], prec))

    logwrite("Diagonal superior: " + " × ".join(factores) + "\n")
    logwrite(f"Signo por intercambios: {form_num(signo, prec)}\n")
    logwrite(f"det({nombre}) = " + " × ".join(factores) + f" × {form_num(signo, prec)} = {form_num(det, prec)}\n")
    return det, True

def reemplazar_columna(M, col, nueva_col):
    R = copiar_matriz(M)
    for i in range(len(M)):
        R[i][col] = nueva_col[i]
    return R

# ---------- Interfaz gráfica ----------

class CramerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cramer paso a paso (GUI)")
        self.geometry("980x640")
        self.minsize(900, 560)

        # Estado
        self.n = tk.IntVar(value=3)
        self.prec = tk.IntVar(value=6)
        self.entries_A = []  # matriz de Entry
        self.entries_b = []  # vector de Entry

        # Fuente monoespaciada para el log
        self.font_mono = ("Courier New", 10)

        self._crear_menu()
        self._crear_widgets()

        self._construir_cuadricula()  # por defecto n=3
        self._cargar_ejemplo()        # poner datos de ejemplo

    # ----- Menú -----
    def _crear_menu(self):
        menubar = tk.Menu(self)

        m_archivo = tk.Menu(menubar, tearoff=0)
        m_archivo.add_command(label="Nuevo", command=self._accion_nuevo)
        m_archivo.add_command(label="Cargar ejemplo", command=self._cargar_ejemplo)
        m_archivo.add_separator()
        m_archivo.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=m_archivo)

        m_ver = tk.Menu(menubar, tearoff=0)
        m_ver.add_command(label="Cambiar precisión…", command=self._cambiar_precision)
        menubar.add_cascade(label="Ver", menu=m_ver)

        m_ayuda = tk.Menu(menubar, tearoff=0)
        m_ayuda.add_command(label="Acerca de", command=self._acerca_de)
        menubar.add_cascade(label="Ayuda", menu=m_ayuda)

        self.config(menu=menubar)

    # ----- Cuerpo -----
    def _crear_widgets(self):
        # Panel superior: control de tamaño y botones
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        ttk.Label(top, text="Tamaño n (A es n×n):").pack(side="left")
        self.spin_n = ttk.Spinbox(top, from_=1, to=10, width=4, textvariable=self.n, command=self._construir_cuadricula, justify="center")
        self.spin_n.pack(side="left", padx=(6, 12))

        ttk.Button(top, text="Construir matriz", command=self._construir_cuadricula).pack(side="left", padx=4)
        ttk.Button(top, text="Resolver por Cramer", command=self._resolver).pack(side="left", padx=4)
        ttk.Button(top, text="Limpiar", command=self._limpiar_log).pack(side="left", padx=4)

        ttk.Label(top, text="Precisión:").pack(side="left", padx=(12, 4))
        self.lbl_prec = ttk.Label(top, textvariable=self.prec)
        self.lbl_prec.pack(side="left")

        # Panel medio: matriz A y vector b
        mid = ttk.Frame(self, padding=8)
        mid.pack(fill="x")

        self.frame_matriz = ttk.Frame(mid)
        self.frame_matriz.pack(side="left", anchor="n")

        # Ayuda visual
        ttk.Label(mid, text="(Ingresa A y b; b se coloca a la derecha de A)", foreground="#555").pack(side="left", padx=12, anchor="n")

        # Panel inferior: log
        bottom = ttk.Frame(self, padding=(8, 0, 8, 8))
        bottom.pack(fill="both", expand=True)

        ttk.Label(bottom, text="Explicación paso a paso:").pack(anchor="w")
        self.text = tk.Text(bottom, wrap="word", font=self.font_mono, undo=False)
        self.scroll = ttk.Scrollbar(bottom, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="left", fill="y")

    # ----- Construcción dinámica de la cuadricula de entradas -----
    def _construir_cuadricula(self):
        # Limpiar grid anterior
        for w in self.frame_matriz.winfo_children():
            w.destroy()
        self.entries_A.clear()
        self.entries_b.clear()

        n = max(1, int(self.n.get()))
        self.n.set(n)

        # Cabeceras
        ttk.Label(self.frame_matriz, text="A", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=n, pady=(0, 4))
        ttk.Label(self.frame_matriz, text="|").grid(row=1, column=n, padx=6)
        ttk.Label(self.frame_matriz, text="b", font=("Segoe UI", 10, "bold")).grid(row=0, column=n+1, pady=(0, 4))

        # Celdas de A y b
        for i in range(n):
            fila_entries = []
            for j in range(n):
                e = ttk.Entry(self.frame_matriz, width=8, justify="center")
                e.grid(row=i+1, column=j, padx=2, pady=2)
                fila_entries.append(e)
            self.entries_A.append(fila_entries)

            eb = ttk.Entry(self.frame_matriz, width=10, justify="center")
            eb.grid(row=i+1, column=n+1, padx=6, pady=2)
            self.entries_b.append(eb)

    # ----- Acciones de menú -----
    def _accion_nuevo(self):
        self.n.set(3)
        self.prec.set(6)
        self._construir_cuadricula()
        self._limpiar_log()

    def _cargar_ejemplo(self):
        """Ejemplo 3x3 sencillo con solución única."""
        self.n.set(3)
        self._construir_cuadricula()
        datos_A = [
            [2, -1, 3],
            [1,  1, 1],
            [3,  0, 2],
        ]
        datos_b = [5, 2, 7]
        for i in range(3):
            for j in range(3):
                self.entries_A[i][j].delete(0, "end")
                self.entries_A[i][j].insert(0, str(datos_A[i][j]))
            self.entries_b[i].delete(0, "end")
            self.entries_b[i].insert(0, str(datos_b[i]))
        self._limpiar_log()
        self._log("Ejemplo 3×3 cargado.\n")

    def _cambiar_precision(self):
        val = simpledialog.askinteger("Precisión", "Número de decimales a mostrar:", parent=self, minvalue=0, maxvalue=12, initialvalue=self.prec.get())
        if val is not None:
            self.prec.set(val)
            self._log(f"Precisión actualizada a {val} decimales.\n")

    def _acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "Regla de Cramer (GUI)\n\n"
            "• Ingresa A (n×n) y b.\n"
            "• Pulsa «Resolver por Cramer».\n"
            "• Verás cada paso del cálculo de determinantes y la solución.\n"
            "Sin librerías externas (solo Tkinter de la biblioteca estándar)."
        )

    # ----- Utilidades GUI -----
    def _log(self, text):
        self.text.insert("end", text)
        self.text.see("end")
        self.text.update_idletasks()

    def _limpiar_log(self):
        self.text.delete("1.0", "end")

    def _leer_A_b(self):
        """Lee A y b desde las celdas. Retorna (A, b) o None si hay error."""
        try:
            n = int(self.n.get())
        except:
            messagebox.showerror("Error", "n inválido.")
            return None
        if n <= 0:
            messagebox.showerror("Error", "n debe ser positivo.")
            return None

        A = []
        b = []
        for i in range(n):
            fila = []
            for j in range(n):
                s = self.entries_A[i][j].get().strip().replace(",", ".")
                fila.append(float(s))
            A.append(fila)
            sb = self.entries_b[i].get().strip().replace(",", ".")
            b.append(float(sb))
        return A, b

    # ----- Núcleo: Resolver por Cramer -----
    def _resolver(self):
        datos = self._leer_A_b()
        if not datos:
            return
        A, b = datos
        n = len(A)
        prec = int(self.prec.get())

        # Validaciones
        for fila in A:
            if len(fila) != n:
                messagebox.showerror("Error", "A debe ser cuadrada (n×n).")
                return
        if len(b) != n:
            messagebox.showerror("Error", "El vector b debe tener longitud n.")
            return

        self._limpiar_log()
        self._log("==============================\n")
        self._log("  SISTEMA A·x = b (Regla de Cramer)\n")
        self._log("==============================\n")
        self._log("Matriz A:\n")
        self._log(matriz_a_texto(A, prec))
        self._log(vector_a_texto(b, "b", prec))

        # det(A)
        detA, ok = determinante_por_eliminacion(A, "A", prec, self._log)
        if not ok or detA == 0.0:
            self._log("\n>>> det(A) = 0  => El sistema NO tiene solución única (sin solución o infinitas).\n")
            return

        # Cálculo de cada x_i
        self._log("\n== Cálculo de cada x_i: x_i = det(A_i) / det(A)\n")
        soluciones = [0.0]*n
        for i in range(n):
            Ai = reemplazar_columna(A, i, b)
            self._log(f"\nMatriz A_{i+1} (A con columna {i+1} reemplazada por b):\n")
            self._log(matriz_a_texto(Ai, prec))
            detAi, ok_i = determinante_por_eliminacion(Ai, f"A_{i+1}", prec, self._log)
            if not ok_i:
                self._log(f">>> No se pudo calcular det(A_{i+1}).\n")
                return
            xi = detAi / detA
            soluciones[i] = xi
            self._log(f"x_{i+1} = det(A_{i+1}) / det(A) = {form_num(detAi, prec)} / {form_num(detA, prec)} = {form_num(xi, prec)}\n")

        # Resultado final
        self._log("\n==============================\n")
        self._log("  SOLUCIÓN (vector x)\n")
        self._log("==============================\n")
        self._log(vector_a_texto(soluciones, "x", prec))
        self._log("\nListo. Fin del procedimiento paso a paso por Cramer.\n")

# ---- Main ----
if __name__ == "__main__":
    app = CramerGUI()
    app.mainloop()
    
def main():
    """Función principal para ejecutar la interfaz CramerGUI desde el menú principal."""
    app = CramerGUI()
    app.mainloop()