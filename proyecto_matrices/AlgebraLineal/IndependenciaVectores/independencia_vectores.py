import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from proyecto_matrices.Run.styles import BG_COLOR, BUTTON_COLOR, ACCENT_COLOR, TEXT_COLOR, BUTTON_HOVER_COLOR, BUTTON_FONT, TITLE_FONT, MONO_FONT, style_tk_button, style_label, style_text


def leer_entero_positivo(mensaje, minimo=1, parent=None):
    while True:
        valor = simpledialog.askinteger("Entrada requerida", mensaje, parent=parent)
        if valor is None:
            return None
        if valor >= minimo:
            return valor
        messagebox.showerror("Error", f"Debe ser un número entero ≥ {minimo}.", parent=parent)


def leer_double(mensaje, parent=None):
    while True:
        entrada = simpledialog.askstring("Entrada requerida", mensaje, parent=parent)
        if entrada is None:
            return None
        entrada = entrada.strip()
        try:
            if '/' in entrada:
                num, den = entrada.split('/')
                return float(num) / float(den)
            return float(entrada.replace(',', '.'))
        except Exception:
            messagebox.showerror("Error", "Por favor introduzca un número válido.", parent=parent)


def gauss_eliminacion(m):
    # m: list of rows (each row is list of floats)
    # returns rank (number of non-zero rows after row-echelon form)
    if not m:
        return 0
    rows = len(m)
    cols = len(m[0])
    r = 0
    for c in range(cols):
        # find pivot
        pivot = None
        for i in range(r, rows):
            if abs(m[i][c]) > 1e-12:
                pivot = i
                break
        if pivot is None:
            continue
        # swap
        if pivot != r:
            m[r], m[pivot] = m[pivot], m[r]
        # normalize pivot row
        pv = m[r][c]
        m[r] = [val / pv for val in m[r]]
        # eliminate below
        for i in range(r + 1, rows):
            factor = m[i][c]
            if abs(factor) > 1e-12:
                m[i] = [m[i][j] - factor * m[r][j] for j in range(cols)]
        r += 1
        if r == rows:
            break
    # count non-zero rows
    rank = 0
    for i in range(rows):
        if any(abs(x) > 1e-9 for x in m[i]):
            rank += 1
    return rank


def mostrar_matriz(m):
    lines = []
    for row in m:
        lines.append('[ ' + '  '.join(f"{v:.4g}" for v in row) + ' ]')
    return '\n'.join(lines)


def main(parent=None):
    ventana = tk.Toplevel(parent) if parent else tk.Tk()
    ventana.title("Verificar Independencia Lineal")
    ventana.geometry("900x640")
    ventana.configure(bg=BG_COLOR)

    # Top controls
    top = tk.Frame(ventana, bg=BG_COLOR, padx=10, pady=8)
    top.pack(side=tk.TOP, fill=tk.X)
    lbl_n = tk.Label(top, text="# Vectores:", bg=BG_COLOR, fg=TEXT_COLOR)
    style_label(lbl_n)
    lbl_n.grid(row=0, column=0, sticky="w")
    spin_n = tk.Spinbox(top, from_=1, to=20, width=4)
    spin_n.grid(row=0, column=1, padx=(6, 12))
    lbl_dim = tk.Label(top, text="Dimensión:", bg=BG_COLOR, fg=TEXT_COLOR)
    style_label(lbl_dim)
    lbl_dim.grid(row=0, column=2, sticky="w")
    spin_dim = tk.Spinbox(top, from_=1, to=50, width=4)
    spin_dim.grid(row=0, column=3, padx=(6, 12))

    btn_crear = tk.Button(top, text="Crear entradas")
    style_tk_button(btn_crear)
    btn_crear.grid(row=0, column=4, padx=6)
    btn_ej = tk.Button(top, text="Cargar ejemplo")
    style_tk_button(btn_ej)
    btn_ej.grid(row=0, column=5, padx=6)
    btn_ver = tk.Button(top, text="Verificar Independencia")
    style_tk_button(btn_ver)
    btn_ver.grid(row=0, column=6, padx=6)
    btn_limpiar = tk.Button(top, text="Limpiar")
    style_tk_button(btn_limpiar)
    btn_limpiar.grid(row=0, column=7, padx=6)

    # Middle: grid for vector entries
    middle = tk.Frame(ventana, bg=BG_COLOR, padx=10, pady=6)
    middle.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
    grid_frame = tk.Frame(middle, bg=BG_COLOR)
    grid_frame.pack()

    # Bottom: output
    bottom = tk.Frame(ventana, bg=BG_COLOR, padx=10, pady=6)
    bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    out = scrolledtext.ScrolledText(bottom)
    out.pack(fill=tk.BOTH, expand=True)
    style_text(out)

    entries = []

    def crear_entradas():
        nonlocal entries
        for w in grid_frame.winfo_children():
            w.destroy()
        entries = []
        try:
            n = int(spin_n.get())
            dim = int(spin_dim.get())
            if n < 1 or dim < 1:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Valores inválidos para número de vectores/dimensión.", parent=ventana)
            return

        # header labels for vectors
        for j in range(n):
            tk.Label(grid_frame, text=f"v{j+1}", bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=j+1, padx=4)
        for i in range(dim):
            tk.Label(grid_frame, text=f"{i+1}", bg=BG_COLOR, fg=TEXT_COLOR).grid(row=i+1, column=0, padx=6)
        for i in range(dim):
            row = []
            for j in range(n):
                e = tk.Entry(grid_frame, width=8, justify='center')
                e.grid(row=i+1, column=j+1, padx=4, pady=3)
                row.append(e)
            entries.append(row)

    def cargar_ejemplo():
        crear_entradas()
        # simple example: three 3-d vectors
        try:
            n = int(spin_n.get())
            dim = int(spin_dim.get())
        except Exception:
            return
        if n >= 3 and dim >= 3:
            ejemplo = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            for j in range(min(n, 3)):
                for i in range(min(dim, 3)):
                    entries[i][j].delete(0, tk.END)
                    entries[i][j].insert(0, str(ejemplo[j][i]))

    def limpiar():
        for w in grid_frame.winfo_children():
            w.destroy()
        out.configure(state='normal')
        out.delete(1.0, tk.END)
        out.configure(state='disabled')

    def verificar():
        # read entries into list of vectors: vectors[j][i]
        try:
            n = int(spin_n.get())
            dim = int(spin_dim.get())
        except Exception:
            messagebox.showerror("Error", "Valores inválidos para número de vectores/dimensión.", parent=ventana)
            return
        if not entries:
            messagebox.showerror("Error", "Primero cree las entradas.", parent=ventana)
            return
        vectors = []
        for j in range(n):
            vec = []
            for i in range(dim):
                try:
                    s = entries[i][j].get().strip().replace(',', '.')
                    if s == '':
                        s = '0'
                    vec.append(float(s))
                except Exception:
                    messagebox.showerror("Error", "Todas las celdas deben contener números.", parent=ventana)
                    return
            vectors.append(vec)

        # compose matrix with vectors as columns (rows = dim, cols = n)
        matriz = [[vectors[j][i] for j in range(n)] for i in range(dim)]
        rango = gauss_eliminacion([fila[:] for fila in matriz])

        out.configure(state='normal')
        out.delete(1.0, tk.END)
        out.insert(tk.END, "Vectores (cada vector como fila):\n")
        for idx, v in enumerate(vectors):
            out.insert(tk.END, f"v{idx+1} = {v}\n")
        out.insert(tk.END, "\nMatriz (vectores como columnas):\n")
        out.insert(tk.END, mostrar_matriz(matriz) + "\n")
        out.insert(tk.END, f"Rango de la matriz: {rango}\n")
        if rango == n:
            out.insert(tk.END, "\nLos vectores son linealmente independientes.\n")
        else:
            out.insert(tk.END, "\nLos vectores son linealmente dependientes.\n")
        out.see(tk.END)
        out.configure(state='disabled')

    # wire buttons
    btn_crear.config(command=crear_entradas)
    btn_ej.config(command=cargar_ejemplo)
    btn_ver.config(command=verificar)
    btn_limpiar.config(command=limpiar)

    # initial defaults
    spin_n.delete(0, tk.END)
    spin_n.insert(0, '3')
    spin_dim.delete(0, tk.END)
    spin_dim.insert(0, '3')

    if parent:
        ventana.transient(parent)
        ventana.grab_set()
    ventana.mainloop()
