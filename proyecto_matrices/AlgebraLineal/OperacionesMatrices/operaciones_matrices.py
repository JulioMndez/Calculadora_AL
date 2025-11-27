import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.suma_matrices import main as abrir_suma
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.resta_matrices import main as abrir_resta
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.multiplicacion_matrices import main as abrir_multiplicacion


class OperacionesMatricesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Operaciones Matriciales")
        self.root.geometry("500x420")
        self.root.resizable(False, False)

        # Estilo general
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        style.configure("TButton", font=('Helvetica', 11, 'bold'), padding=10)
        style.configure("TLabel", font=('Helvetica', 14, 'bold'))

        # Contenedor principal guardado para poder cambiar vistas
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(expand=True, fill='both')

        # Mostrar el menú principal de operaciones
        self.show_menu()

    def clear_frame(self):
        for w in self.frame.winfo_children():
            w.destroy()

    def show_menu(self):
        """Construye el menú principal de operaciones básicas."""
        self.clear_frame()

        # Título
        ttk.Label(self.frame, text="Operaciones Matriciales", style="TLabel").pack(pady=(0, 15))
        ttk.Label(self.frame, text="Seleccione el tipo de operación:", font=('Helvetica', 11)).pack(pady=(0, 15))

        # Botones de operaciones (reutilizan otros módulos)
        ttk.Button(
            self.frame, text="Suma de Matrices", width=35, command=abrir_suma
        ).pack(pady=8)

        ttk.Button(
            self.frame, text="Resta de Matrices", width=35, command=abrir_resta
        ).pack(pady=8)

        ttk.Button(
            self.frame, text="Multiplicación de Matrices", width=35, command=abrir_multiplicacion
        ).pack(pady=8)

        # Nuevo botón integrado: Trasponer Matriz (usa la misma ventana/frame)
        ttk.Button(
            self.frame, text="Transponer Matriz", width=35, command=self.show_transpose
        ).pack(pady=8)

        # Botón para volver al menú principal
        ttk.Button(
            self.frame, text="Volver al Menú Principal", width=35, command=self.root.destroy
        ).pack(pady=20)

        # Pie de ventana
        ttk.Label(
            self.frame,
            text="Universidad Americana (UAM) — Managua, Nicaragua\nDesarrollado por Julio César Méndez",
            font=('Helvetica', 9, 'italic')
        ).pack(pady=(10, 0))

    def show_transpose(self):
        """Muestra la UI para leer una matriz y mostrar su transpuesta en el mismo frame."""
        self.clear_frame()

        ttk.Label(self.frame, text="Trasponer Matriz", style="TLabel").pack(pady=(0, 10))

        info_label = ttk.Label(self.frame, text="Ingrese las dimensiones y elementos de la matriz.")
        info_label.pack(pady=(0, 8))

        # Pedir dimensiones mediante diálogos modales
        filas = leer_entero_positivo("Número de filas de la matriz:", parent=self.root)
        if filas is None:
            try:
                self.root.destroy()
            except Exception:
                pass
            return
        columnas = leer_entero_positivo("Número de columnas de la matriz:", parent=self.root)
        if columnas is None:
            try:
                self.root.destroy()
            except Exception:
                pass
            return

        matriz = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                valor = leer_double(f"Elemento [{i},{j}]:", parent=self.root)
                if valor is None:
                    try:
                        self.root.destroy()
                    except Exception:
                        pass
                    return
                fila.append(valor)
            matriz.append(fila)

        # Área de texto para mostrar matrices
        text_box = tk.Text(self.frame, wrap="word", font=("Consolas", 10), height=12)
        text_box.pack(expand=True, fill='both', pady=(5, 5))

        text_box.insert(tk.END, f"===== MATRIZ ORIGINAL =====\n{imprimir_matriz(matriz)}\n")
        matriz_traspuesta = trasponer_matriz(matriz)
        text_box.insert(tk.END, f"\n===== MATRIZ TRASPUESTA =====\n{imprimir_matriz(matriz_traspuesta)}\n")
        text_box.see(tk.END)

        controls = ttk.Frame(self.frame)
        controls.pack(pady=8)

        ttk.Button(controls, text="Volver", command=self.show_menu).pack(side='left', padx=6)
        ttk.Button(controls, text="Cerrar", command=self.root.destroy).pack(side='left', padx=6)

    # ------------------ Helpers copiados (reutilizables) ------------------
def leer_entero_positivo(mensaje, minimo=1, parent=None):
    """Solicita un entero positivo mediante un diálogo."""
    while True:
        try:
            valor = simpledialog.askinteger("Entrada requerida", mensaje, parent=parent)
            if valor is None:
                return None
            if valor >= minimo:
                return valor
            messagebox.showerror("Error", f"Debe ser un número entero ≥ {minimo}.", parent=parent)
        except ValueError:
            messagebox.showerror("Error", "Entrada inválida.", parent=parent)

def leer_double(mensaje, parent=None):
    """Solicita un número (puede ser decimal o fracción) mediante un diálogo."""
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
        except ValueError:
            messagebox.showerror("Error", "Entrada inválida, intente de nuevo.", parent=parent)

def trasponer_matriz(matriz):
    """Devuelve la matriz traspuesta."""
    filas = len(matriz)
    columnas = len(matriz[0])
    return [[matriz[i][j] for i in range(filas)] for j in range(columnas)]

def imprimir_matriz(matriz):
    filas = len(matriz)
    columnas = len(matriz[0])
    col_widths = [0] * columnas
    for j in range(columnas):
        col_widths[j] = max(len(f"{matriz[i][j]:.3g}") for i in range(filas))

    def linea_borde(esq_izq, sep, esq_der):
        return esq_izq + sep.join("─" * (col_widths[j] + 2) for j in range(columnas)) + esq_der

    line_sup = linea_borde("┌", "┬", "┐")
    line_mid = linea_borde("├", "┼", "┤")
    line_inf = linea_borde("└", "┴", "┘")

    lines = [line_sup]
    for i in range(filas):
        fila_str = "│" + "│".join(f" {matriz[i][j]:>{col_widths[j]}.3g} " for j in range(columnas)) + "│"
        lines.append(fila_str)
        if i != filas - 1:
            lines.append(line_mid)
    lines.append(line_inf)

    return "\n".join(lines)

    # --------------------------------------------------------------------


def main():
    ventana = tk.Toplevel()
    OperacionesMatricesApp(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    OperacionesMatricesApp(root)
    root.mainloop()


def abrir_transpose():
    """Abre la ventana de Operaciones Matriciales y muestra directamente la pantalla de trasponer matriz."""
    ventana = tk.Toplevel()
    app = OperacionesMatricesApp(ventana)
    # Llamar explícitamente al método que muestra la UI de trasponer
    try:
        app.show_transpose()
    except Exception:
        # Si por alguna razón no existe, volver al menú principal
        app.show_menu()
    ventana.mainloop()
