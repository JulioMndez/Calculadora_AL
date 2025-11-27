import tkinter as tk
from tkinter import messagebox, simpledialog
from proyecto_matrices.Run.styles import BG_COLOR, BUTTON_COLOR, ACCENT_COLOR, TEXT_COLOR, BUTTON_HOVER_COLOR, BUTTON_FONT, TITLE_FONT, style_tk_button, style_label, style_text


def leer_entero_positivo(mensaje, minimo=1, parent=None):
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


def formatear_matriz(matriz):
    if not matriz or not matriz[0]:
        return "[Matriz vacía]"
    max_width = max(len(f"{v:.2f}") for fila in matriz for v in fila)
    filas = []
    for fila in matriz:
        fila_texto = "  ".join(f"{v:>{max_width}.2f}" for v in fila)
        filas.append(f"[ {fila_texto} ]")
    return "\n".join(filas)


def restar_matrices(matrices, escalares, text_widget):
    filas = len(matrices[0])
    columnas = len(matrices[0][0])
    resultado = [[matrices[0][i][j] * escalares[0] for j in range(columnas)] for i in range(filas)]

    text_widget.insert(tk.END, f"\n===== Iniciando con MATRIZ 1 * Escalar {escalares[0]} =====\n")
    for i in range(filas):
        for j in range(columnas):
            text_widget.insert(tk.END, f"Elemento [{i},{j}] = {resultado[i][j]}\n")

    for m in range(1, len(matrices)):
        text_widget.insert(tk.END, f"\n===== Restando MATRIZ {m+1} * Escalar {escalares[m]} =====\n")
        for i in range(filas):
            for j in range(columnas):
                valor = matrices[m][i][j] * escalares[m]
                resultado[i][j] -= valor
                text_widget.insert(
                    tk.END,
                    f"  - ({escalares[m]}) * M{m+1}[{i},{j}] = {valor} → resultado acumulado = {resultado[i][j]}\n"
                )
    return resultado


def main():
    ventana = tk.Toplevel()
    ventana.title("Resta de Múltiples Matrices con Escalares")
    ventana.geometry("800x600")
    ventana.configure(bg=BG_COLOR)

    frame = tk.Frame(ventana, bg=BG_COLOR, padx=10, pady=10)
    frame.pack(expand=True, fill="both")

    text_box = tk.Text(frame, wrap="word")
    text_box.pack(expand=True, fill="both")
    style_text(text_box)

    num_matrices = leer_entero_positivo("¿Cuántas matrices desea restar? (mínimo 2)", 2, parent=ventana)
    if not num_matrices:
        ventana.destroy()
        return

    filas = leer_entero_positivo("Número de filas:", 1, parent=ventana)
    columnas = leer_entero_positivo("Número de columnas:", 1, parent=ventana)
    if not filas or not columnas:
        ventana.destroy()
        return

    matrices = []
    escalares = []
    for m in range(num_matrices):
        matriz = []
        messagebox.showinfo("Ingreso", f"Ingrese los datos de la matriz {m+1}", parent=ventana)
        for i in range(filas):
            fila = []
            for j in range(columnas):
                valor = leer_double(f"Elemento [{i},{j}] de la matriz {m+1}:", parent=ventana)
                if valor is None:
                    ventana.destroy()
                    return
                fila.append(valor)
            matriz.append(fila)
        matrices.append(matriz)

        escalar = leer_double(f"Escalar para multiplicar la matriz {m+1} (1 por defecto):", parent=ventana)
        if escalar is None:
            escalar = 1
        escalares.append(escalar)

    for i, mat in enumerate(matrices):
        text_box.insert(tk.END, f"\n===== MATRIZ {i+1} (Escalar {escalares[i]}) =====\n{formatear_matriz(mat)}\n")

    resultado = restar_matrices(matrices, escalares, text_box)

    text_box.insert(tk.END, f"\n===== RESULTADO FINAL =====\n{formatear_matriz(resultado)}\n")
    text_box.see(tk.END)

    btn_cerrar = tk.Button(frame, text="Cerrar", command=ventana.destroy)
    style_tk_button(btn_cerrar)
    btn_cerrar.pack(pady=10)
    ventana.mainloop()


if __name__ == "__main__":
    main()
