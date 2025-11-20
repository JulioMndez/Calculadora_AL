import tkinter as tk
from tkinter import font

# === Importaciones de tus módulos ===
from operaciones_matrices import main as abrir_operaciones_matrices
from operaciones.operaciones_avanzadas_matrices import main as abrir_operaciones_avanzadas
from calculo_determinante import main as abrir_determinante
from inversion_matriz import main as abrir_inversa
from cramer_gui import main as abrir_cramer
from independencia_vectores import main as abrir_independencia
from resolucion_matrices import main as abrir_resolucion
from eliminacion_gauss import main as abrir_gauss_jordan


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        """Configura la ventana principal."""
        self.root.title("Álgebra Lineal Interactiva")
        # Ajustamos la altura para el nuevo botón
        self.root.geometry("600x700") 
        self.root.resizable(False, False)
        self.root.configure(bg="#2E2E2E")

        # Paleta de colores y fuentes
        self.BG_COLOR = "#2E2E2E"
        self.BUTTON_COLOR = "#505050"
        self.ACCENT_COLOR = "#007ACC"
        self.TEXT_COLOR = "#FFFFFF"
        self.BUTTON_HOVER_COLOR = "#6a6a6a"
        
        self.TITLE_FONT = font.Font(family="Arial", size=22, weight="bold")
        self.SUBTITLE_FONT = font.Font(family="Arial", size=11)
        self.BUTTON_FONT = font.Font(family="Arial", size=10, weight="bold")
        self.CREDITS_FONT = font.Font(family="Arial", size=9, slant="italic")

    def create_widgets(self):
        """Crea y posiciona todos los widgets en la ventana."""
        main_frame = tk.Frame(self.root, bg=self.BG_COLOR, padx=30, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="ÁLGEBRA LINEAL INTERACTIVA 📐", font=self.TITLE_FONT, bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=(10, 5))
        tk.Label(main_frame, text="Seleccione una herramienta para comenzar", font=self.SUBTITLE_FONT, bg=self.BG_COLOR, fg="#CCCCCC").pack(pady=(0, 30))

        buttons_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        buttons_frame.pack(expand=True, fill="x")

        # === LISTA DE BOTONES ACTUALIZADA ===
        buttons_data = [
            ("Operaciones Básicas", "∑", abrir_operaciones_matrices),
            ("Transponer Matriz", "⟷", abrir_operaciones_avanzadas),
            ("Calcular Determinante", "|A|", abrir_determinante),
            ("Calcular Inversa", "A⁻¹", abrir_inversa),
            ("Independencia Lineal", "‖v‖", abrir_independencia),
            ("Resolver por Cramer", "C", abrir_cramer),
            ("Resolver Sistemas (General)", "x=?", abrir_resolucion),
            # --- === NUEVO BOTÓN AÑADIDO === ---
            ("Resolver por Eliminación", "G-J", abrir_gauss_jordan) 
        ]
        # --------------------------------------

        for i, (text, icon, command) in enumerate(buttons_data):
            row, col = divmod(i, 2)
            
            button_text = f"{icon}  {text}"
            btn = tk.Button(
                buttons_frame,
                text=button_text,
                font=self.BUTTON_FONT,
                bg=self.BUTTON_COLOR,
                fg=self.TEXT_COLOR,
                command=command,
                relief="flat",
                pady=15,
                width=25,
                activebackground=self.ACCENT_COLOR,
                activeforeground=self.TEXT_COLOR,
                justify="left",
                anchor="w",
                padx=20
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.BUTTON_HOVER_COLOR))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.BUTTON_COLOR))

        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        footer_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        footer_frame.pack(side="bottom", fill="x", pady=(30, 0))

        exit_button = tk.Button(
            footer_frame,
            text="⏻   Salir del Programa",
            font=self.BUTTON_FONT,
            bg="#D32F2F",
            fg=self.TEXT_COLOR,
            command=self.root.destroy,
            relief="flat",
            pady=10,
            activebackground="#E57373"
        )
        exit_button.pack(fill="x", ipady=5)
        
        exit_button.bind("<Enter>", lambda e: e.widget.config(bg="#E57373"))
        exit_button.bind("<Leave>", lambda e: e.widget.config(bg="#D32F2F"))
        
        tk.Label(
            footer_frame,
            text="\nUniversidad Americana (UAM) — Managua, Nicaragua\nDesarrollado por Julio César Méndez",
            font=self.CREDITS_FONT,
            bg=self.BG_COLOR,
            fg="#AAAAAA",
            justify="center"
        ).pack(pady=(15, 0))

def main():
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
