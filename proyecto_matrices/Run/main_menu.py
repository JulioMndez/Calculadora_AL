import tkinter as tk
from tkinter import font
import os
import sys

# Permitir ejecutar este archivo directamente añadiendo la raíz del proyecto a sys.path
_this_dir = os.path.dirname(os.path.abspath(__file__))
# subir dos niveles: Run/ -> proyecto_matrices/ -> (raíz del workspace)
_workspace_root = os.path.abspath(os.path.join(_this_dir, '..', '..'))
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# === Importaciones de tus módulos (actualizadas a imports absolutos) ===
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.operaciones_matrices import main as abrir_operaciones_matrices
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.operaciones_matrices import abrir_transpose
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.suma_matrices import main as abrir_suma
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.resta_matrices import main as abrir_resta
from proyecto_matrices.AlgebraLineal.OperacionesMatrices.multiplicacion_matrices import main as abrir_multiplicacion
from proyecto_matrices.AlgebraLineal.Determinante.calculo_determinante import main as abrir_determinante
from proyecto_matrices.AlgebraLineal.InversionMatriz.inversion_matriz import main as abrir_inversa
from proyecto_matrices.AlgebraLineal.IndependenciaVectores.independencia_vectores import main as abrir_independencia
from proyecto_matrices.AlgebraLineal.SistemasEcuaciones.resolucion_matrices import main as abrir_resolucion
from proyecto_matrices.AlgebraLineal.SistemasEcuaciones.cramer_gui import main as abrir_cramer
from proyecto_matrices.AlgebraLineal.SistemasEcuaciones.eliminacion_gauss import main as abrir_gauss_jordan


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        # Crear el frame principal compartido y mostrar la pantalla inicial
        self.main_frame = tk.Frame(self.root, bg=self.BG_COLOR, padx=30, pady=20)
        self.main_frame.pack(expand=True, fill="both")
        self.create_initial_screen()

    def setup_window(self):
        """Configura la ventana principal."""
        self.root.title("Álgebra Lineal Interactiva")
        # Abrir en pantalla completa; usar 'zoomed' como fallback en Windows
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            try:
                self.root.state('zoomed')
            except Exception:
                self.root.geometry("1920x1080")

        # Permitimos redimensionar cuando estemos fuera de fullscreen
        self.root.resizable(True, True)
        self.root.configure(bg="#2E2E2E")

        # Función para salir de pantalla completa (vía Escape o programáticamente)
        def exit_fullscreen(event=None):
            try:
                self.root.attributes("-fullscreen", False)
            except Exception:
                try:
                    self.root.state('normal')
                except Exception:
                    pass

        # Vincular Escape para salir de fullscreen
        self.root.bind("<Escape>", exit_fullscreen)

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

    def clear_main_frame(self):
        """Eliminar widgets del frame principal antes de mostrar nuevo contenido."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_initial_screen(self):
        """Muestra la pantalla inicial con dos botones grandes."""
        self.clear_main_frame()

        tk.Label(self.main_frame, text="Calculadora 📐", font=self.TITLE_FONT, bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=(40, 10))
        tk.Label(self.main_frame, text="Elija la categoría a continuación", font=self.SUBTITLE_FONT, bg=self.BG_COLOR, fg="#CCCCCC").pack(pady=(0, 30))

        # Contenedor para botones grandes
        choices_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        choices_frame.pack(expand=True)

        # Botón Álgebra Lineal
        algebra_btn = tk.Button(
            choices_frame,
            text="Álgebra Lineal",
            font=font.Font(family="Arial", size=14, weight="bold"),
            bg=self.BUTTON_COLOR,
            fg=self.TEXT_COLOR,
            command=self.show_algebra_menu,
            relief="flat",
            pady=25,
            padx=40,
            activebackground=self.ACCENT_COLOR,
            activeforeground=self.TEXT_COLOR,
            width=20
        )
        algebra_btn.grid(row=0, column=0, padx=20, pady=20)

        # Botón Método Numérico
        numeric_btn = tk.Button(
            choices_frame,
            text="Método Numérico",
            font=font.Font(family="Arial", size=14, weight="bold"),
            bg=self.BUTTON_COLOR,
            fg=self.TEXT_COLOR,
            command=self.show_metodo_numerico,
            relief="flat",
            pady=25,
            padx=40,
            activebackground=self.ACCENT_COLOR,
            activeforeground=self.TEXT_COLOR,
            width=20
        )
        numeric_btn.grid(row=0, column=1, padx=20, pady=20)

        # Footer con créditos y botón salir
        footer_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
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

    def show_metodo_numerico(self):
        """Acción del botón 'Método Numérico' — por ahora imprime y muestra mensaje."""
        print("Método Numérico aún no disponible")
        self.clear_main_frame()

        tk.Label(self.main_frame, text="Método Numérico", font=self.TITLE_FONT, bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=(20, 10))
        tk.Label(self.main_frame, text="Aún no disponible.", font=self.SUBTITLE_FONT, bg=self.BG_COLOR, fg="#CCCCCC").pack(pady=(0, 30))

        back_btn = tk.Button(
            self.main_frame,
            text="← Volver",
            font=self.BUTTON_FONT,
            bg=self.BUTTON_COLOR,
            fg=self.TEXT_COLOR,
            command=self.create_initial_screen,
            relief="flat",
            pady=8,
            activebackground=self.ACCENT_COLOR
        )
        back_btn.pack(pady=10)

    def show_algebra_menu(self):
        """Muestra el menú actual de Álgebra Lineal (refactorizado desde create_widgets)."""
        self.clear_main_frame()

        tk.Label(self.main_frame, text="ÁLGEBRA LINEAL INTERACTIVA 📐", font=self.TITLE_FONT, bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=(10, 5))
        tk.Label(self.main_frame, text="Seleccione una herramienta para comenzar", font=self.SUBTITLE_FONT, bg=self.BG_COLOR, fg="#CCCCCC").pack(pady=(0, 30))
        # Botón para volver a la pantalla inicial
        back_btn = tk.Button(
            self.main_frame,
            text="← Volver",
            font=self.BUTTON_FONT,
            bg=self.BUTTON_COLOR,
            fg=self.TEXT_COLOR,
            command=self.create_initial_screen,
            relief="flat",
            pady=6,
            padx=10,
            activebackground=self.ACCENT_COLOR
        )
        back_btn.pack(anchor="w", pady=(0, 10))

        buttons_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        buttons_frame.pack(expand=True, fill="x")

        # === LISTA DE BOTONES ACTUALIZADA ===
        buttons_data = [
            ("Operaciones Básicas", "∑", self.show_operaciones_basicas),
            ("Calcular Determinante", "|A|", abrir_determinante),
            ("Calcular Inversa", "A⁻¹", abrir_inversa),
            ("Independencia Lineal", "‖v‖", abrir_independencia),
            ("Resolver Sistemas (General)", "x=?", self.show_resolver_sistemas_menu),
        ]

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
        
        footer_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
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

    def show_operaciones_basicas(self):
        """Muestra las operaciones básicas (submenu) dentro del mismo frame."""
        self.clear_main_frame()
        tk.Label(self.main_frame, text="Operaciones Básicas", font=self.TITLE_FONT, bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=(10, 5))
        tk.Label(self.main_frame, text="Elija una operación:", font=self.SUBTITLE_FONT, bg=self.BG_COLOR, fg="#CCCCCC").pack(pady=(0, 15))

        back_btn = tk.Button(
            self.main_frame,
            text="← Volver",
            font=self.BUTTON_FONT,
            bg=self.BUTTON_COLOR,
            fg=self.TEXT_COLOR,
            command=self.show_algebra_menu,
            relief="flat",
            pady=6,
            padx=10,
            activebackground=self.ACCENT_COLOR
        )
        back_btn.pack(anchor="w", pady=(0, 10))

        ops_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        ops_frame.pack(expand=True, fill="both")

        btn_suma = tk.Button(ops_frame, text="➕  Suma de Matrices", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_suma, relief="flat", pady=10, width=30)
        btn_suma.pack(pady=8)
        btn_resta = tk.Button(ops_frame, text="➖  Resta de Matrices", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_resta, relief="flat", pady=10, width=30)
        btn_resta.pack(pady=8)
        btn_mult = tk.Button(ops_frame, text="✖️  Multiplicación de Matrices", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_multiplicacion, relief="flat", pady=10, width=30)
        btn_mult.pack(pady=8)
        btn_trans = tk.Button(ops_frame, text="🔁  Transponer Matriz", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_transpose, relief="flat", pady=10, width=30)
        btn_trans.pack(pady=8)

    def show_independencia_menu(self):
        """Muestra la pantalla para independencia lineal dentro del frame (lanzará la herramienta en ventana aparte)."""
        self.clear_main_frame()
        tk.Label(self.main_frame, text="Independencia Lineal", font=self.TITLE_FONT, bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=(10, 5))
        tk.Label(self.main_frame, text="Verifique si un conjunto de vectores es linealmente independiente.", font=self.SUBTITLE_FONT, bg=self.BG_COLOR, fg="#CCCCCC").pack(pady=(0, 15))

        back_btn = tk.Button(self.main_frame, text="← Volver", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=self.show_algebra_menu, relief="flat", pady=6, padx=10, activebackground=self.ACCENT_COLOR)
        back_btn.pack(anchor="w", pady=(0, 10))

        tk.Button(self.main_frame, text="Verificar Independencia", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_independencia, relief="flat", pady=12, width=30).pack(pady=8)

    def show_resolver_sistemas_menu(self):
        """Muestra las opciones para resolver sistemas dentro del mismo frame."""
        self.clear_main_frame()
        tk.Label(self.main_frame, text="Resolver Sistemas de Ecuaciones", font=self.TITLE_FONT, bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=(10, 5))
        tk.Label(self.main_frame, text="Elija un método para resolver el sistema:", font=self.SUBTITLE_FONT, bg=self.BG_COLOR, fg="#CCCCCC").pack(pady=(0, 15))

        back_btn = tk.Button(self.main_frame, text="← Volver", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=self.show_algebra_menu, relief="flat", pady=6, padx=10, activebackground=self.ACCENT_COLOR)
        back_btn.pack(anchor="w", pady=(0, 10))

        # Botones específicos dentro del submenú "Resolver Sistemas"
        tk.Button(self.main_frame, text="Resolver por Cramer", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_cramer, relief="flat", pady=12, width=36).pack(pady=8)
        tk.Button(self.main_frame, text="Resolver (General)", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_resolucion, relief="flat", pady=12, width=36).pack(pady=8)
        tk.Button(self.main_frame, text="Eliminación / Gauss", font=self.BUTTON_FONT, bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, command=abrir_gauss_jordan, relief="flat", pady=12, width=36).pack(pady=8)

def main():
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
