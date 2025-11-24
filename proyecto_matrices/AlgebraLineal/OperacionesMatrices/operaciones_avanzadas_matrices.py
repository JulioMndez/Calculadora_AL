import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

def leer_entero_positivo(mensaje, minimo=1, parent=None):
    """Solicita un entero positivo mediante un diálogo."""
    while True:
        try:
            valor = simpledialog.askinteger("Entrada requerida", mensaje, parent=parent)
            if valor is None:
                return None
            if valor >= minimo:
                return valor
            messagebox.showerror("Error", "Debe ser un número entero ≥ {minimo}.", parent=parent)
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

def main():
    ventana = tk.Toplevel()
    ventana.title("Trasponer Matriz")
    ventana.geometry("700x600")

    frame = ttk.Frame(ventana, padding=10)
    frame.pack(expand=True, fill="both")

    text_box = tk.Text(frame, wrap="word", font=("Consolas", 10))
    text_box.pack(expand=True, fill="both")

    filas = leer_entero_positivo("Número de filas de la matriz:", parent=ventana)
    if filas is None:
        ventana.destroy()
        return
    columnas = leer_entero_positivo("Número de columnas de la matriz:", parent=ventana)
    if columnas is None:
        ventana.destroy()
        return

    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            valor = leer_double(f"Elemento [{i},{j}]:", parent=ventana)
            if valor is None:
                ventana.destroy()
                return
            fila.append(valor)
        matriz.append(fila)

    text_box.insert(tk.END, f"===== MATRIZ ORIGINAL =====\n{imprimir_matriz(matriz)}\n")
    matriz_traspuesta = trasponer_matriz(matriz)
    text_box.insert(tk.END, f"\n===== MATRIZ TRASPUESTA =====\n{imprimir_matriz(matriz_traspuesta)}\n")
    text_box.see(tk.END)

    ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack(pady=10)

    ventana.mainloop()


if __name__ == "__main__":
    main()
