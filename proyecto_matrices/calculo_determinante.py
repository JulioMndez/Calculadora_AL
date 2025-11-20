import tkinter as tk
from tkinter import messagebox, scrolledtext

# === Funciones de cálculo ===

def parsear_valor(valor_str: str) -> float:
    """Convierte un valor ingresado a float, aceptando decimales o fracciones a/b."""
    valor_str = valor_str.strip()
    if '/' in valor_str:
        try:
            numerador, denominador = valor_str.split('/')
            return float(numerador) / float(denominador)
        except Exception:
            raise ValueError(f"Valor inválido como fracción: {valor_str}")
    else:
        try:
            return float(valor_str)
        except Exception:
            raise ValueError(f"Valor inválido: {valor_str}")

def imprimir_matriz_texto(matriz):
    """Convierte una matriz en texto legible."""
    texto = ""
    for fila in matriz:
        texto += "[ " + "  ".join(f"{val:8.4f}" for val in fila) + " ]\n"
    return texto

def calcular_determinante(matriz, mostrar_pasos=True):
    n = len(matriz)
    for fila in matriz:
        if len(fila) != n:
            return None, "Error: La matriz no es cuadrada."

    A = [fila[:] for fila in matriz]
    signo = 1.0
    pasos = ""

    if mostrar_pasos:
        pasos += "Matriz inicial:\n" + imprimir_matriz_texto(A) + "\n"

    for i in range(n):
        pivote_fila = i
        pivote_valor = abs(A[i][i])
        for j in range(i + 1, n):
            if abs(A[j][i]) > pivote_valor:
                pivote_valor = abs(A[j][i])
                pivote_fila = j

        if pivote_fila != i:
            A[i], A[pivote_fila] = A[pivote_fila], A[i]
            signo *= -1
            pasos += f"Intercambiando fila {i + 1} con fila {pivote_fila + 1}\n"
            pasos += imprimir_matriz_texto(A) + "\n"

        pivote = A[i][i]
        if abs(pivote) < 1e-12:
            pasos += f"El pivote en columna {i + 1} es cero. Determinante = 0\n"
            return 0.0, pasos

        pasos += f"Pivote en fila {i + 1}, columna {i + 1}: {pivote:.4f}\n"
        pasos += "Eliminando entradas debajo del pivote:\n"

        for j in range(i + 1, n):
            factor = A[j][i] / pivote
            for k in range(i, n):
                A[j][k] -= factor * A[i][k]
            pasos += f"  Fila {j + 1} <- Fila {j + 1} - ({factor:.4f}) * Fila {i + 1}\n"

        pasos += "Estado después del paso {}:\n".format(i + 1)
        pasos += imprimir_matriz_texto(A) + "\n"

    determinante = signo
    for i in range(n):
        determinante *= A[i][i]

    pasos += "Producto de los elementos de la diagonal principal:\n"
    pasos += "  " + " * ".join(f"{A[i][i]:.4f}" for i in range(n)) + "\n"
    pasos += f"Determinante final = {determinante:.6f}\n"

    return determinante, pasos

# === Interfaz gráfica ===

class DeterminanteGUI:
    def __init__(self, root):
        self.root = root
        root.title("Cálculo de Determinante")
        root.geometry("750x600")

        self.label = tk.Label(root, text="Ingrese el tamaño de la matriz:")
        self.label.pack(pady=5)

        self.entry_n = tk.Entry(root)
        self.entry_n.pack(pady=5)

        self.boton_crear = tk.Button(root, text="Crear campos de matriz", command=self.crear_campos)
        self.boton_crear.pack(pady=5)

        self.frame_matriz = tk.Frame(root)
        self.frame_matriz.pack(pady=10)

        self.boton_calcular = tk.Button(root, text="Calcular determinante", command=self.calcular)
        self.boton_calcular.pack(pady=5)

        self.resultado_texto = scrolledtext.ScrolledText(root, height=25)
        self.resultado_texto.pack(pady=10, fill=tk.BOTH, expand=True)

        self.campos = []

    def crear_campos(self):
        for widget in self.frame_matriz.winfo_children():
            widget.destroy()
        self.campos = []

        try:
            n = int(self.entry_n.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número entero positivo.")
            return

        for i in range(n):
            fila_campos = []
            for j in range(n):
                e = tk.Entry(self.frame_matriz, width=6)
                e.grid(row=i, column=j, padx=2, pady=2)
                fila_campos.append(e)
            self.campos.append(fila_campos)

    def calcular(self):
        if not self.campos:
            messagebox.showerror("Error", "Primero cree los campos de la matriz.")
            return

        matriz = []
        try:
            for fila_campos in self.campos:
                fila = [parsear_valor(c.get()) for c in fila_campos]
                matriz.append(fila)
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return

        det, pasos = calcular_determinante(matriz, mostrar_pasos=True)
        self.resultado_texto.delete(1.0, tk.END)
        self.resultado_texto.insert(tk.END, pasos)
        self.resultado_texto.insert(tk.END, f"\nDeterminante = {det:.6f}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = DeterminanteGUI(root)
    root.mainloop()

# === FUNCIÓN PARA LLAMAR DESDE EL MENÚ PRINCIPAL ===
def main():
    root = tk.Tk()
    app = DeterminanteGUI(root)
    root.mainloop()
