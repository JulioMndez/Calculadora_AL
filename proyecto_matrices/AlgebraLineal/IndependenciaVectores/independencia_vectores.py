import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

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
                return float(num)/float(den)
            return float(entrada.replace(',', '.'))
        except ValueError:
            messagebox.showerror("Error", "Entrada inválida. Intente de nuevo.", parent=parent)

def mostrar_matriz(matriz):
    return "\n".join(["\t".join(f"{elem:.3g}" for elem in fila) for fila in matriz])

def gauss_eliminacion(matriz):
    filas = len(matriz)
    columnas = len(matriz[0])
    rango = 0
    for col in range(columnas):
        pivote_fila = None
        for i in range(rango, filas):
            if matriz[i][col] != 0:
                pivote_fila = i
                break
        if pivote_fila is None:
            continue
        if pivote_fila != rango:
            matriz[rango], matriz[pivote_fila] = matriz[pivote_fila], matriz[rango]
        pivote = matriz[rango][col]
        for j in range(col, columnas):
            matriz[rango][j] /= pivote
        for i in range(rango+1, filas):
            factor = matriz[i][col]
            for j in range(col, columnas):
                matriz[i][j] -= factor * matriz[rango][j]
        rango += 1
    return rango

def main():
    ventana = tk.Toplevel()
    ventana.title("Verificar Independencia Lineal")
    ventana.geometry("800x600")
    frame = ttk.Frame(ventana, padding=10)
    frame.pack(expand=True, fill="both")
    text_box = tk.Text(frame, wrap="word", font=("Consolas", 10))
    text_box.pack(expand=True, fill="both")
    num_vectores = leer_entero_positivo("Ingrese el número de vectores:", 1, parent=ventana)
    if num_vectores is None:
        ventana.destroy()
        return
    dim = leer_entero_positivo("Ingrese la dimensión de los vectores:", 1, parent=ventana)
    if dim is None:
        ventana.destroy()
        return
    vectores = []
    for v in range(num_vectores):
        vector = []
        text_box.insert(tk.END, f"\n--- Vector {v+1} ---\n")
        for i in range(dim):
            valor = leer_double(f"Elemento {i+1} del vector {v+1}:", parent=ventana)
            if valor is None:
                ventana.destroy()
                return
            vector.append(valor)
        vectores.append(vector)
    text_box.insert(tk.END, "\nVectores ingresados (cada fila es un vector):\n")
    text_box.insert(tk.END, mostrar_matriz(vectores) + "\n")
    matriz = [[vectores[j][i] for j in range(num_vectores)] for i in range(dim)]
    text_box.insert(tk.END, "\nMatriz de vectores como columnas:\n")
    text_box.insert(tk.END, mostrar_matriz(matriz) + "\n")
    rango = gauss_eliminacion([fila[:] for fila in matriz])
    text_box.insert(tk.END, f"\nRango de la matriz: {rango}\n")
    if rango == num_vectores:
        text_box.insert(tk.END, "\nLos vectores son linealmente independientes.\n")
    else:
        text_box.insert(tk.END, "\nLos vectores son linealmente dependientes.\n")
    text_box.see(tk.END)
    ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack(pady=10)
    ventana.mainloop()

if __name__ == "__main__":
    main()
