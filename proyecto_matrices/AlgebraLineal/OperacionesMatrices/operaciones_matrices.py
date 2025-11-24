import tkinter as tk
from tkinter import ttk
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.suma_matrices import main as abrir_suma
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.resta_matrices import main as abrir_resta
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.multiplicacion_matrices import main as abrir_multiplicacion


class OperacionesMatricesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Operaciones Matriciales")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        # Estilo general
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        style.configure("TButton", font=('Helvetica', 11, 'bold'), padding=10)
        style.configure("TLabel", font=('Helvetica', 14, 'bold'))

        # Contenedor principal
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        # Título
        ttk.Label(frame, text="Operaciones Matriciales", style="TLabel").pack(pady=(0, 15))
        ttk.Label(frame, text="Seleccione el tipo de operación:", font=('Helvetica', 11)).pack(pady=(0, 15))

        # Botones de operaciones
        ttk.Button(
            frame, text="Suma de Matrices", width=35, command=abrir_suma
        ).pack(pady=8)

        ttk.Button(
            frame, text="Resta de Matrices", width=35, command=abrir_resta
        ).pack(pady=8)

        ttk.Button(
            frame, text="Multiplicación de Matrices", width=35, command=abrir_multiplicacion
        ).pack(pady=8)

        # Botón para volver al menú principal
        ttk.Button(
            frame, text="Volver al Menú Principal", width=35, command=self.root.destroy
        ).pack(pady=20)

        # Pie de ventana
        ttk.Label(
            frame,
            text="Universidad Americana (UAM) — Managua, Nicaragua\nDesarrollado por Julio César Méndez",
            font=('Helvetica', 9, 'italic')
        ).pack(pady=(10, 0))


def main():
    ventana = tk.Toplevel()
    OperacionesMatricesApp(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    OperacionesMatricesApp(root)
    root.mainloop()
