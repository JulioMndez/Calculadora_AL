import tkinter as tk
from tkinter import messagebox, ttk
from matematicas import validar_ecuacion
from grafico import dibujar_grafico, dibujar_punto_raiz
from metodo_secante import ejecutar_metodo_secante
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ToolTip:
    """Clase para crear tooltips"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.show_timer = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        self.show_timer = self.widget.after(500, self.show_tooltip)
    
    def on_leave(self, event=None):
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
            self.show_timer = None
        self.hide_tooltip()
    
    def show_tooltip(self, event=None):
        if self.tooltip:
            return
        
        temp_tooltip = tk.Toplevel(self.widget)
        temp_tooltip.wm_overrideredirect(True)
        temp_tooltip.withdraw()
        
        temp_label = tk.Label(temp_tooltip, text=self.text, background="#ffffe0", 
                             relief="solid", borderwidth=1, font=("Arial", 9), padx=5, pady=3)
        temp_label.pack()
        temp_tooltip.update_idletasks()
        
        tooltip_width = temp_label.winfo_reqwidth()
        tooltip_height = temp_label.winfo_reqheight()
        temp_tooltip.destroy()
        
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty() + self.widget.winfo_height() // 2
        
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        if x + tooltip_width > screen_width:
            x = self.widget.winfo_rootx() - tooltip_width - 5
        
        if y + tooltip_height > screen_height:
            y = screen_height - tooltip_height - 10
        
        if y < 0:
            y = 10
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", 
                        relief="solid", borderwidth=1, font=("Arial", 9), padx=5, pady=3)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class ExampleDialog(ttk.Frame):
    """Diálogo de ejemplos categorizados para la interfaz Tkinter."""
    def __init__(self, parent):
        # parent es la instancia de InterfazReglaFalsa
        self.parent = parent
        self.top = tk.Toplevel(parent.root)
        self.top.title("Ejemplos - Método de la Secante")
        self.top.transient(parent.root)
        self.top.grab_set()
        self.top.geometry('600x400')

        notebook = ttk.Notebook(self.top)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Definir categorías y ejemplos (ampliables)
        categorias = {
            'Polinomiales': [
                ("x^3 - x - 2", "1.0", "2.0", "0.0001"),
                ("x^2 - 2", "1.0", "2.0", "0.0001"),
                ("x^3 - 6x^2 + 11x - 6", "0.0", "3.0", "1e-6")
            ],
            'Trigonométricas': [
                ("cos(x) - x", "0.0", "1.0", "0.0001"),
                ("sin(x) - 0.5", "0.0", "2.0", "1e-4"),
                ("tan(x) - x", "0.1", "1.4", "1e-4")
            ],
            'Exponenciales/Log': [
                ("exp(x) - 2", "0.0", "1.0", "1e-5"),
                ("ln(x) - 1", "2.0", "3.0", "1e-5")
            ],
            'Radicales/Otros': [
                ("sqrt(x) - 1", "0.5", "2.0", "1e-5"),
                ("1/x - 0.5", "1.0", "3.0", "1e-5")
            ]
        }

        for cat, ejemplos in categorias.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=cat)

            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
            scroll_frame = ttk.Frame(canvas)

            scroll_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            for func, x0, x1, tol in ejemplos:
                btn = ttk.Button(scroll_frame, text=f"{func}  (x0={x0}, x1={x1})",
                                 command=lambda f=func, a=x0, b=x1, t=tol: self._apply_and_close(f, a, b, t))
                btn.pack(fill=tk.X, padx=6, pady=4)

        # Botones inferiores
        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(btn_frame, text="Nuevo (vacío)", command=self._nuevo_vacio).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Cerrar", command=self.top.destroy).pack(side=tk.RIGHT)

    def _apply_and_close(self, func, x0, x1, tol):
        try:
            self.parent.cargar_ejemplo(func, x0, x1, tol)
        finally:
            self.top.destroy()

    def _nuevo_vacio(self):
        self.parent.nuevo_calculo()
        self.top.destroy()

class InterfazReglaFalsa:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Método de la Secante")
        self.root.geometry("1200x700")
        self.root.configure(bg="#F0F0F0")
        
        self.crear_interfaz()
        self.configurar_eventos()
        
    def crear_interfaz(self):
        # Barra de menú (Archivo / Ejemplos / Ayuda)
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self.mostrar_dialog_ejemplos)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        ejemplos_menu = tk.Menu(menubar, tearoff=0)
        ejemplos_menu.add_command(label="Ejemplo 1: x^3 - x - 2 (x0=1, x1=2)",
                                   command=lambda: self.cargar_ejemplo("x^3 - x - 2", "1.0", "2.0", "0.0001"))
        ejemplos_menu.add_command(label="Ejemplo 2: cos(x) - x (x0=0, x1=1)",
                                   command=lambda: self.cargar_ejemplo("cos(x) - x", "0.0", "1.0", "0.0001"))
        ejemplos_menu.add_command(label="Ejemplo 3: x^2 - 2 (x0=1, x1=2)",
                                   command=lambda: self.cargar_ejemplo("x^2 - 2", "1.0", "2.0", "0.0001"))
        menubar.add_cascade(label="Ejemplos", menu=ejemplos_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Ayuda", command=lambda: messagebox.showinfo("Ayuda", "Usa 'Ejemplos' para cargar problemas de demostración."))
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.root.config(menu=menubar)

    def mostrar_dialog_ejemplos(self):
        """Abre el diálogo con ejemplos categorizados."""
        ExampleDialog(self)
        main_frame = tk.Frame(self.root, bg=self.root['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame, padx=20, pady=20, bg=self.root['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = tk.Frame(main_frame, padx=10, pady=20, bg=self.root['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Función
        func_label = tk.Label(left_frame, text="Función f(x):", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        func_label.grid(row=0, column=0, sticky="w", pady=5)
        ToolTip(func_label, "Ingresa la función matemática a evaluar")
        
        self.entry_function = tk.Entry(left_frame, width=40, font=('Arial', 12))
        self.entry_function.grid(row=0, column=1, columnspan=2, pady=5, sticky="ew")
        self.entry_function.insert(0, "x^3 - x - 2")
        ToolTip(self.entry_function, "Escribe tu función usando x como variable")

        self.label_validacion = tk.Label(left_frame, text="", bg=self.root['bg'], font=('Arial', 9))
        self.label_validacion.grid(row=1, column=0, columnspan=3, sticky="w", pady=2)

        # Botones de funciones
        self.crear_botones_funciones(left_frame)

        # Controles de entrada
        self.crear_controles_entrada(left_frame)

        # Área de resultados
        self.crear_area_resultados(left_frame)

        # Gráfico
        tk.Label(right_frame, text="Gráfico de la Función:", bg=self.root['bg'], font=('Arial', 12, 'bold')).pack(pady=(0,5))
        self.canvas_grafico = tk.Canvas(right_frame, width=500, height=400, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas_grafico.pack(fill=tk.BOTH, expand=True)
        ToolTip(self.canvas_grafico, "Gráfica de la función")
        
        self.rango_grafico = None

        left_frame.rowconfigure(10, weight=1)

    def crear_botones_funciones(self, parent):
        func_frame = tk.Frame(parent, bg=self.root['bg'])
        func_frame.grid(row=3, column=0, columnspan=3, pady=10)

        botones_funciones = [
            ('sin x', 'sin(x)'), ('cos x', 'cos(x)'), ('tan x', 'tan(x)'),
            ('exp x', 'exp(x)'), ('ln x', 'ln(x)'), ('√x', 'sqrt(x)'),
            ('x²', 'x^2'), ('x³', 'x^3'), ('π', 'pi')
        ]

        tooltips = {
            'sin(x)': 'Digitar: sin(x)', 'cos(x)': 'Digitar: cos(x)', 'tan(x)': 'Digitar: tan(x)',
            'exp(x)': 'Digitar: exp(x)', 'ln(x)': 'Digitar: ln(x)', 'sqrt(x)': 'Digitar: sqrt(x)',
            'x^2': 'Digitar: x^2', 'x^3': 'Digitar: x^3', 'pi': 'Digitar: pi'
        }
        
        for idx, (texto, valor) in enumerate(botones_funciones):
            btn = tk.Button(func_frame, text=texto, width=4, 
                           command=lambda v=valor: self.insertar_funcion(v))
            btn.grid(row=0, column=idx, padx=1, pady=1)
            ToolTip(btn, tooltips.get(valor, f'Insertar {valor}'))

    def crear_controles_entrada(self, parent):
        # Punto inicial x0
        x0_label = tk.Label(parent, text="Punto inicial x0:", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        x0_label.grid(row=4, column=0, sticky="w", pady=5)
        ToolTip(x0_label, "Primer punto inicial para la secante")
        
        self.entry_x0 = tk.Entry(parent, width=15, font=('Arial', 10))
        self.entry_x0.grid(row=4, column=1, pady=5, sticky="w")
        self.entry_x0.insert(0, "1.0")
        ToolTip(self.entry_x0, "Primer valor inicial para el método")
        
        # Punto inicial x1
        x1_label = tk.Label(parent, text="Punto inicial x1:", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        x1_label.grid(row=5, column=0, sticky="w", pady=5)
        ToolTip(x1_label, "Segundo punto inicial para la secante")
        
        self.entry_x1 = tk.Entry(parent, width=15, font=('Arial', 10))
        self.entry_x1.grid(row=5, column=1, pady=5, sticky="w")
        self.entry_x1.insert(0, "2.0")
        ToolTip(self.entry_x1, "Segundo valor inicial para el método")

        # Error
        error_label = tk.Label(parent, text="Error:", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        error_label.grid(row=6, column=0, sticky="w", pady=5)
        ToolTip(error_label, "Error máximo aceptable en formato decimal")
        
        self.entry_tolerance = tk.Entry(parent, width=15, font=('Arial', 10))
        self.entry_tolerance.grid(row=6, column=1, pady=5, sticky="w")
        self.entry_tolerance.insert(0, "0.0001")
        ToolTip(self.entry_tolerance, "Error relativo en decimal")

        self.max_iterations = 10000

        # Botones
        botones_frame = tk.Frame(parent, bg=self.root['bg'])
        botones_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        self.graficar_button = tk.Button(botones_frame, text="Graficar Ecuación", command=self.graficar_ecuacion,
                                        bg="#2196F3", fg="white", font=('Arial', 10, 'bold'), width=15)
        self.graficar_button.grid(row=0, column=0, padx=5)
        ToolTip(self.graficar_button, "Dibuja la gráfica de tu función")
        
        self.run_button = tk.Button(botones_frame, text="Encontrar Raíz", command=self.ejecutar_metodo,
                                   bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'), width=15)
        self.run_button.grid(row=0, column=1, padx=5)
        ToolTip(self.run_button, "Ejecuta el método de la secante")

    def crear_area_resultados(self, parent):
        result_label = tk.Label(parent, text="Resultados:", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        result_label.grid(row=9, column=0, sticky="w", pady=(10,5))
        ToolTip(result_label, "Aquí se muestran los cálculos paso a paso")

        frame_resultados = tk.Frame(parent)
        frame_resultados.grid(row=10, column=0, columnspan=3, pady=5, sticky="nsew")

        scrollbar_y = tk.Scrollbar(frame_resultados)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.texto_resultados = tk.Text(frame_resultados, width=60, height=12, state=tk.DISABLED, 
                              yscrollcommand=scrollbar_y.set, font=('Courier', 9))
        self.texto_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ToolTip(self.texto_resultados, "Detalle de cada iteración del método numérico")
        scrollbar_y.config(command=self.texto_resultados.yview)

    def configurar_eventos(self):
        self.entry_function.bind("<KeyRelease>", self.validar_y_limpiar)
        self.entry_tolerance.bind("<KeyRelease>", self.validar_y_limpiar)

    def cargar_ejemplo(self, funcion, x0, x1, tol):
        """Carga un ejemplo en los campos de entrada y limpia resultados anteriores."""
        self.entry_function.delete(0, tk.END)
        self.entry_function.insert(0, funcion)
        self.entry_x0.delete(0, tk.END)
        self.entry_x0.insert(0, x0)
        self.entry_x1.delete(0, tk.END)
        self.entry_x1.insert(0, x1)
        self.entry_tolerance.delete(0, tk.END)
        self.entry_tolerance.insert(0, tol)
        self.limpiar_resultados()
        self.validar_y_limpiar()

    def nuevo_calculo(self):
        """Resetea la interfaz a valores por defecto."""
        self.entry_function.delete(0, tk.END)
        self.entry_x0.delete(0, tk.END)
        self.entry_x1.delete(0, tk.END)
        self.entry_tolerance.delete(0, tk.END)
        self.entry_function.insert(0, "x^3 - x - 2")
        self.entry_x0.insert(0, "1.0")
        self.entry_x1.insert(0, "2.0")
        self.entry_tolerance.insert(0, "0.0001")
        self.limpiar_resultados()
        self.limpiar_grafico()
        self.validar_y_limpiar()

    def insertar_funcion(self, funcion):
        cursor_pos = self.entry_function.index(tk.INSERT)
        self.entry_function.insert(cursor_pos, funcion)
        self.entry_function.focus_set()
        self.validar_y_limpiar()

    def limpiar_resultados(self):
        self.texto_resultados.config(state=tk.NORMAL)
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.config(state=tk.DISABLED)
    
    def limpiar_grafico(self):
        self.canvas_grafico.delete("all")
        self.rango_grafico = None

    def validar_y_limpiar(self, event=None):
        self.limpiar_resultados()
        if event and event.widget == self.entry_function:
            self.limpiar_grafico()
        
        func_str = self.entry_function.get().strip()
        if func_str:
            valida, mensaje = validar_ecuacion(func_str)
            if valida:
                self.label_validacion.config(text="✓ Ecuación válida", fg="green")
                self.graficar_button.config(state="normal")
            else:
                self.label_validacion.config(text=f"✗ {mensaje}", fg="red")
                self.graficar_button.config(state="disabled")
        else:
            self.label_validacion.config(text="", fg="black")
            self.graficar_button.config(state="disabled")

    def ejecutar_metodo(self):
        try:
            func_str = self.entry_function.get().strip()
            tol_text = self.entry_tolerance.get().strip()
            x0_text = self.entry_x0.get().strip()
            x1_text = self.entry_x1.get().strip()

            try:
                x0 = float(x0_text)
                x1 = float(x1_text)
                tolerance = float(tol_text)
            except ValueError:
                messagebox.showerror("Error", "Los valores deben ser numéricos.")
                return
            
            if tolerance <= 0 or tolerance > 1:
                messagebox.showerror("Error", "El error debe estar entre 0 y 1 (formato decimal).")
                return
            
            if x0 == x1:
                messagebox.showerror("Error", "x0 y x1 deben ser diferentes.")
                return
            
            max_iter = self.max_iterations

            # Ejecutar método
            exito, resultado, iteraciones_data = ejecutar_metodo_secante(func_str, x0, x1, tolerance, max_iter)
            
            if not exito:
                messagebox.showerror("Error", resultado)
                return

            # Mostrar resultados
            self.mostrar_resultados(iteraciones_data)
            
            # Dibujar gráfico
            self.rango_grafico = dibujar_grafico(self.canvas_grafico, self.entry_function)
            dibujar_punto_raiz(self.canvas_grafico, resultado['raiz'], self.rango_grafico)
            
            # Mostrar mensaje final
            if resultado['convergio']:
                messagebox.showinfo("Resultado", 
                    f"Se encontró la raíz {resultado['raiz']:.10f} en {resultado['iteracion']} iteraciones con error {resultado['error']:.8f}")
            else:
                messagebox.showwarning("Advertencia", 
                    f"Se alcanzó el máximo de iteraciones ({self.max_iterations}). Raíz aproximada: {resultado['raiz']:.10f}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def graficar_ecuacion(self):
        try:
            func_str = self.entry_function.get().strip()
            if not func_str:
                return
                
            valida, mensaje = validar_ecuacion(func_str)
            if not valida:
                messagebox.showerror("Error", f"Ecuación inválida: {mensaje}")
                return
            
            self.limpiar_grafico()
            self.rango_grafico = dibujar_grafico(self.canvas_grafico, self.entry_function)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar: {str(e)}")
    
    def mostrar_resultados(self, iteraciones_data):
        self.texto_resultados.config(state=tk.NORMAL)
        self.texto_resultados.delete("1.0", tk.END)
        
        for datos in iteraciones_data:
            texto = (f"Iteración {datos['iteracion']}:\n"
                     f"  x0 = {datos['x0']:.8f}, x1 = {datos['x1']:.8f}\n"
                     f"  f(x0) = {datos['fx0']:.8e}, f(x1) = {datos['fx1']:.8e}\n"
                     f"  x2 = {datos['x2']:.8f}\n"
                     f"  Error Relativo = {datos['error_rel']:.8f}\n\n")
            self.texto_resultados.insert(tk.END, texto)
            self.texto_resultados.see(tk.END)
            self.root.update()
        
        self.texto_resultados.config(state=tk.DISABLED)

    def ejecutar(self):
        self.validar_y_limpiar()
        self.root.mainloop()

if __name__ == "__main__":
    app = InterfazReglaFalsa()
    app.ejecutar()
