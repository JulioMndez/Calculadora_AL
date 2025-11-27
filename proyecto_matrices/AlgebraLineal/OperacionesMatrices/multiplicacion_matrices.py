import tkinter as tk
from tkinter import messagebox, simpledialog
from proyecto_matrices.Run.styles import BG_COLOR, BUTTON_COLOR, ACCENT_COLOR, TEXT_COLOR, BUTTON_HOVER_COLOR, BUTTON_FONT, TITLE_FONT, style_tk_button, style_label, style_text


def leer_entero_positivo(mensaje, minimo=1, parent=None):
    """Solicita un entero positivo mediante un diálogo."""
    while True:
        try:
            valor = simpledialog.askinteger("Entrada requerida", mensaje, parent=parent)
            if valor is None:
                return None
            if valor >= minimo:
                return valor
            messagebox.showerror("Error", "Entrada inválida.", parent=parent)
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


def multiplicar_dos_matrices(A, B, text_widget):
    """Multiplica dos matrices con salida paso a paso."""
    filasA, columnasA = len(A), len(A[0])
    filasB, columnasB = len(B), len(B[0])
    if columnasA != filasB:
        raise ValueError("Dimensiones incompatibles para multiplicación")

    resultado = [[0 for _ in range(columnasB)] for _ in range(filasA)]

    for i in range(filasA):
        for j in range(columnasB):
            suma = 0
            text_widget.insert(tk.END, f"\nCalculando elemento [{i},{j}]:\n")
            for k in range(columnasA):
                producto = A[i][k] * B[k][j]
                suma += producto
                text_widget.insert(
                    tk.END,
                    f"  A[{i},{k}] * B[{k},{j}] = {A[i][k]} * {B[k][j]} = {producto} → suma acumulada = {suma}\n"
                )
            resultado[i][j] = suma
    return resultado


def imprimir_matriz(matriz):
    """Devuelve una cadena con la matriz formateada de manera legible (alineada, sin bordes Unicode)."""
    if not matriz or not matriz[0]:
        return "[Matriz vacía]"
    max_width = max(len(f"{valor:.2f}") for fila in matriz for valor in fila)
    lineas = []
    for fila in matriz:
        fila_str = "  ".join(f"{valor:>{max_width}.2f}" for valor in fila)
        lineas.append(f"[ {fila_str} ]")
    return "\n".join(lineas)


def main():
    ventana = tk.Toplevel()
    ventana.title("Multiplicación de Múltiples Matrices (Paso a Paso)")
    ventana.geometry("800x600")
    ventana.configure(bg=BG_COLOR)

    frame = tk.Frame(ventana, bg=BG_COLOR, padx=10, pady=10)
    frame.pack(expand=True, fill="both")

    text_box = tk.Text(frame, wrap="word")
    text_box.pack(expand=True, fill="both")
    style_text(text_box)

    num_matrices = leer_entero_positivo("¿Cuántas matrices desea multiplicar? (mínimo 2)", 2, parent=ventana)
    if not num_matrices:
        ventana.destroy()
        return

    matrices = []
    filas = []
    columnas = []

    for m in range(num_matrices):
        while True:
            f = leer_entero_positivo(f"Filas de la matriz {m + 1}:", parent=ventana)
            c = leer_entero_positivo(f"Columnas de la matriz {m + 1}:", parent=ventana)

            if f is None or c is None:
                ventana.destroy()
                return

            if m > 0 and f != columnas[m - 1]:
                messagebox.showerror("Error", "Dimensiones incompatibles: el número de filas de esta matriz debe coincidir con las columnas de la anterior.", parent=ventana)
                continue

            matriz = []
            for i in range(f):
                fila = []
                for j in range(c):
                    valor = leer_double(f"Elemento [{i},{j}] de la matriz {m + 1}:", parent=ventana)
                    if valor is None:
                        ventana.destroy()
                        return
                    fila.append(valor)
                matriz.append(fila)

            matrices.append(matriz)
            filas.append(f)
            columnas.append(c)
            break

    for i, mat in enumerate(matrices):
        text_box.insert(tk.END, f"\n===== MATRIZ {i + 1} =====\n{imprimir_matriz(mat)}\n")

    resultado = matrices[0]
    for i in range(1, num_matrices):
        text_box.insert(tk.END, f"\n===== MULTIPLICANDO MATRIZ {i} × MATRIZ {i + 1} =====\n")
        resultado = multiplicar_dos_matrices(resultado, matrices[i], text_box)

    text_box.insert(tk.END, f"\n===== RESULTADO FINAL =====\n{imprimir_matriz(resultado)}\n")
    text_box.see(tk.END)

    btn_cerrar = tk.Button(frame, text="Cerrar", command=ventana.destroy)
    style_tk_button(btn_cerrar)
    btn_cerrar.pack(pady=10)
    ventana.mainloop()


if __name__ == "__main__":
    main()
