import tkinter as tk
from tkinter import messagebox, ttk
from matematicas import validar_ecuacion
from grafico import dibujar_grafico, dibujar_punto_raiz
from metodo_regla_falsa import ejecutar_metodo_regla_falsa
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
        
        # Crear tooltip temporal para medir dimensiones
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
        
        # Calcular posición inicial
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty() + self.widget.winfo_height() // 2
        
        # Obtener dimensiones de pantalla
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        # Ajustar si se sale por la derecha
        if x + tooltip_width > screen_width:
            x = self.widget.winfo_rootx() - tooltip_width - 5
        
        # Ajustar si se sale por abajo
        if y + tooltip_height > screen_height:
            y = screen_height - tooltip_height - 10
        
        # Ajustar si se sale por arriba
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

class InterfazReglaFalsa:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Método de la Regla Falsa")
        self.root.geometry("1200x700")
        self.root.configure(bg="#F0F0F0")
        
        self.crear_interfaz()
        self.configurar_eventos()
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.root['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame izquierdo para controles
        left_frame = tk.Frame(main_frame, padx=20, pady=20, bg=self.root['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Frame derecho para gráfico
        right_frame = tk.Frame(main_frame, padx=10, pady=20, bg=self.root['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Función
        func_label = tk.Label(left_frame, text="Función f(x):", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        func_label.grid(row=0, column=0, sticky="w", pady=5)
        ToolTip(func_label, "Ingresa la función matemática a evaluar")
        
        self.entry_function = tk.Entry(left_frame, width=40, font=('Arial', 10))
        self.entry_function.grid(row=0, column=1, columnspan=2, pady=5, sticky="ew")
        self.entry_function.insert(0, "x^3 - x - 2")
        ToolTip(self.entry_function, "Escribe tu función usando x como variable. Ejemplo: x^2 + 3*x - 5")

        # Label de validación
        self.label_validacion = tk.Label(left_frame, text="", bg=self.root['bg'], font=('Arial', 9))
        self.label_validacion.grid(row=1, column=0, columnspan=3, sticky="w", pady=2)

        # Frame para ecuación algebraica con matplotlib
        self.ecuacion_frame = tk.Frame(left_frame, bg="#F5F5F5", relief=tk.FLAT, bd=1)
        self.ecuacion_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        ToolTip(self.ecuacion_frame, "Visualización algebraica de tu función en formato LaTeX")
        
        # Crear figura de matplotlib para LaTeX
        self.fig_ecuacion = Figure(figsize=(5, 0.4), dpi=100, facecolor='#F5F5F5')
        self.ax_ecuacion = self.fig_ecuacion.add_subplot(111)
        self.ax_ecuacion.axis('off')
        self.canvas_ecuacion = FigureCanvasTkAgg(self.fig_ecuacion, master=self.ecuacion_frame)
        self.canvas_ecuacion.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        


        # Botones de funciones matemáticas
        self.crear_botones_funciones(left_frame)

        # Controles de entrada
        self.crear_controles_entrada(left_frame)

        # Área de resultados
        self.crear_area_resultados(left_frame)

        # Gráfico
        tk.Label(right_frame, text="Gráfico de la Función:", bg=self.root['bg'], font=('Arial', 12, 'bold')).pack(pady=(0,5))
        tk.Label(right_frame, text="Haz clic en dos puntos para seleccionar el intervalo [a, b]", 
                bg=self.root['bg'], font=('Arial', 9), fg="gray").pack(pady=(0,10))
        self.canvas_grafico = tk.Canvas(right_frame, width=500, height=400, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas_grafico.pack(fill=tk.BOTH, expand=True)
        ToolTip(self.canvas_grafico, "Gráfica interactiva: haz clic para seleccionar intervalos")
        
        # Variables para interacción con gráfica
        self.valor_a = None
        self.valor_b = None
        self.rango_grafico = None
        self.lineas_intervalo = []  # Para guardar las líneas del intervalo

        # Configurar grid weights
        left_frame.rowconfigure(9, weight=1)

    def crear_botones_funciones(self, parent):
        func_frame = tk.Frame(parent, bg=self.root['bg'])
        func_frame.grid(row=3, column=0, columnspan=3, pady=10)

        # Primera fila de botones
        botones_funciones_1 = [
            ('sin x', 'sin(x)'), ('cos x', 'cos(x)'), ('tan x', 'tan(x)'),
            ('arcsin x', 'asin(x)'), ('arccos x', 'acos(x)'), ('arctan x', 'atan(x)')
        ]

        # Segunda fila de botones
        botones_funciones_2 = [
            ('sinh x', 'sinh(x)'), ('cosh x', 'cosh(x)'), ('tanh x', 'tanh(x)'),
            ('e^x', 'exp(x)'), ('ln x', 'ln(x)'), ('log₁₀ x', 'log10(x)')
        ]

        # Tercera fila de botones
        botones_funciones_3 = [
            ('log₂ x', 'log2(x)'), ('√x', 'sqrt(x)'), ('∛x', 'cbrt(x)'),
            ('ⁿ√x', 'root(x,3)'), ('x²', 'x^2'), ('|x|', 'abs(x)')
        ]
        
        # Cuarta fila de botones
        botones_funciones_4 = [
            ('π', 'pi'), ('e', 'e'), ('x³', 'x^3'), ('xⁿ', 'x^'), ('logₓ x', 'logb(x,10)'), ('1/x', '1/x')
        ]
        


        # Crear botones en filas
        # Tooltips para botones de funciones
        tooltips_funciones = {
            'sin(x)': 'Digitar: sin(x)', 'cos(x)': 'Digitar: cos(x)', 'tan(x)': 'Digitar: tan(x)',
            'asin(x)': 'Digitar: asin(x)', 'acos(x)': 'Digitar: acos(x)', 'atan(x)': 'Digitar: atan(x)',
            'sinh(x)': 'Digitar: sinh(x)', 'cosh(x)': 'Digitar: cosh(x)', 'tanh(x)': 'Digitar: tanh(x)',
            'exp(x)': 'Digitar: exp(x)', 'ln(x)': 'Digitar: ln(x)', 'log10(x)': 'Digitar: log10(x)',
            'log2(x)': 'Digitar: log2(x)', 'sqrt(x)': 'Digitar: sqrt(x)', 'cbrt(x)': 'Digitar: cbrt(x)',
            'root(x,3)': 'Digitar: root(x,n)', 'x^2': 'Digitar: x^2', 'abs(x)': 'Digitar: abs(x)',
            'pi': 'Digitar: pi', 'e': 'Digitar: e', 'x^3': 'Digitar: x^3',
            'x^': 'Digitar: x^n', 'logb(x,10)': 'Digitar: logb(x,b)', '1/x': 'Digitar: 1/x'
        }
        
        for idx, (texto, valor) in enumerate(botones_funciones_1):
            btn = tk.Button(func_frame, text=texto, width=8, 
                           command=lambda v=valor: self.insertar_funcion(v))
            btn.grid(row=0, column=idx, padx=1, pady=1)
            ToolTip(btn, tooltips_funciones.get(valor, f'Insertar {valor}'))

        for idx, (texto, valor) in enumerate(botones_funciones_2):
            btn = tk.Button(func_frame, text=texto, width=8, 
                           command=lambda v=valor: self.insertar_funcion(v))
            btn.grid(row=1, column=idx, padx=1, pady=1)
            ToolTip(btn, tooltips_funciones.get(valor, f'Insertar {valor}'))

        for idx, (texto, valor) in enumerate(botones_funciones_3):
            btn = tk.Button(func_frame, text=texto, width=8, 
                           command=lambda v=valor: self.insertar_funcion(v))
            btn.grid(row=2, column=idx, padx=1, pady=1)
            ToolTip(btn, tooltips_funciones.get(valor, f'Insertar {valor}'))
                      
        for idx, (texto, valor) in enumerate(botones_funciones_4):
            btn = tk.Button(func_frame, text=texto, width=8, 
                           command=lambda v=valor: self.insertar_funcion(v))
            btn.grid(row=3, column=idx, padx=1, pady=1)
            ToolTip(btn, tooltips_funciones.get(valor, f'Insertar {valor}'))

    def crear_controles_entrada(self, parent):
        # Intervalo
        interval_label = tk.Label(parent, text="Intervalo [a, b]:", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        interval_label.grid(row=4, column=0, sticky="w", pady=5)
        ToolTip(interval_label, "Define el intervalo donde buscar la raíz")
        
        self.entry_a = tk.Entry(parent, width=15, font=('Arial', 10))
        self.entry_a.grid(row=4, column=1, pady=5, sticky="w")
        self.entry_a.insert(0, "1")
        ToolTip(self.entry_a, "Valor inicial del intervalo (debe ser menor que b)")

        self.entry_b = tk.Entry(parent, width=15, font=('Arial', 10))
        self.entry_b.grid(row=4, column=2, pady=5, sticky="w")
        self.entry_b.insert(0, "2")
        ToolTip(self.entry_b, "Valor final del intervalo (debe ser mayor que a)")

        # Error
        error_label = tk.Label(parent, text="Error:", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        error_label.grid(row=5, column=0, sticky="w", pady=5)
        ToolTip(error_label, "Error máximo aceptable en formato decimal")
        
        self.entry_tolerance = tk.Entry(parent, width=15, font=('Arial', 10))
        self.entry_tolerance.grid(row=5, column=1, pady=5, sticky="w")
        self.entry_tolerance.insert(0, "0.0001")
        ToolTip(self.entry_tolerance, "Error relativo en decimal (ej: 0.01 = 1%, 0.0001 = 0.01%)")

        # Máximo de iteraciones (oculto, valor fijo)
        self.max_iterations = 10000  # Valor fijo alto

        # Botones
        botones_frame = tk.Frame(parent, bg=self.root['bg'])
        botones_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        self.graficar_button = tk.Button(botones_frame, text="Graficar Ecuación", command=self.graficar_ecuacion,
                                        bg="#2196F3", fg="white", font=('Arial', 10, 'bold'), width=15)
        self.graficar_button.grid(row=0, column=0, padx=5)
        ToolTip(self.graficar_button, "Dibuja la gráfica de tu función")
        
        self.run_button = tk.Button(botones_frame, text="Encontrar Raíz", command=self.ejecutar_metodo,
                                   bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'), width=15)
        self.run_button.grid(row=0, column=1, padx=5)
        ToolTip(self.run_button, "Ejecuta el método de regla falsa para encontrar la raíz")

    def crear_area_resultados(self, parent):
        # Área de resultados
        result_label = tk.Label(parent, text="Resultados:", bg=self.root['bg'], font=('Arial', 10, 'bold'))
        result_label.grid(row=8, column=0, sticky="w", pady=(10,5))
        ToolTip(result_label, "Aquí se muestran los cálculos paso a paso")

        frame_resultados = tk.Frame(parent)
        frame_resultados.grid(row=9, column=0, columnspan=3, pady=5, sticky="nsew")

        scrollbar_y = tk.Scrollbar(frame_resultados)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.texto_resultados = tk.Text(frame_resultados, width=60, height=12, state=tk.DISABLED, 
                              yscrollcommand=scrollbar_y.set, font=('Courier', 9))
        self.texto_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ToolTip(self.texto_resultados, "Detalle de cada iteración del método numérico")
        scrollbar_y.config(command=self.texto_resultados.yview)

    def configurar_eventos(self):
        # Bind eventos
        self.entry_function.bind("<KeyRelease>", self.validar_y_limpiar)
        self.entry_tolerance.bind("<KeyRelease>", self.validar_y_limpiar)
        
        # Bind especial para los intervalos
        self.entry_a.bind("<KeyRelease>", self.actualizar_intervalo_grafico)
        self.entry_b.bind("<KeyRelease>", self.actualizar_intervalo_grafico)
        
        # Bind eventos del canvas
        self.canvas_grafico.bind("<Button-1>", self.click_grafico)

    def insertar_funcion(self, funcion):
        # Insertar en la posición actual del cursor
        cursor_pos = self.entry_function.index(tk.INSERT)
        self.entry_function.insert(cursor_pos, funcion)
        # Mantener el foco en el campo de entrada después de insertar
        self.entry_function.focus_set()
        self.validar_y_limpiar()

    def limpiar_resultados(self):
        self.texto_resultados.config(state=tk.NORMAL)
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.config(state=tk.DISABLED)
    
    def limpiar_grafico(self):
        self.canvas_grafico.delete("all")
        self.rango_grafico = None
        self.valor_a = None
        self.valor_b = None
        self.lineas_intervalo = []

    def validar_y_limpiar(self, event=None):
        self.limpiar_resultados()
        # Solo limpiar gráfica si el evento viene de cambios en la función
        if event and event.widget == self.entry_function:
            self.limpiar_grafico()
        
        # Validar ecuación
        func_str = self.entry_function.get().strip()
        if func_str:
            valida, mensaje = validar_ecuacion(func_str)
            if valida:
                self.label_validacion.config(text="✓ Ecuación válida", fg="green")
                # Mostrar ecuación en formato algebraico
                self.mostrar_ecuacion_algebraica(func_str)
                self.graficar_button.config(state="normal")
            else:
                self.label_validacion.config(text=f"✗ {mensaje}", fg="red")
                self.mostrar_ecuacion_latex("")
                self.graficar_button.config(state="disabled")
        else:
            self.label_validacion.config(text="", fg="black")
            self.mostrar_ecuacion_latex("")
            self.graficar_button.config(state="disabled")
        
        self.validar_botones()
    
    def actualizar_intervalo_grafico(self, event=None):
        """Actualiza las líneas de intervalo cuando se modifican las cajas a y b"""
        self.validar_botones()
        
        # Solo dibujar si hay gráfica y valores válidos
        if not self.rango_grafico:
            return
            
        try:
            a_text = self.entry_a.get().strip()
            b_text = self.entry_b.get().strip()
            
            if not a_text or not b_text:
                return
                
            a = float(a_text)
            b = float(b_text)
            
            # Validar que a < b
            if a >= b:
                return
            
            # Limpiar líneas anteriores
            for linea_id in self.lineas_intervalo:
                self.canvas_grafico.delete(linea_id)
            self.lineas_intervalo = []
            
            # Dibujar nuevas líneas si están en el rango visible
            self.dibujar_lineas_intervalo(a, b)
            
        except ValueError:
            # Si los valores no son numéricos, limpiar líneas
            for linea_id in self.lineas_intervalo:
                self.canvas_grafico.delete(linea_id)
            self.lineas_intervalo = []
    
    def dibujar_lineas_intervalo(self, a, b):
        """Dibuja las líneas de intervalo en la gráfica"""
        if not self.rango_grafico:
            return
            
        width = self.canvas_grafico.winfo_width()
        height = self.canvas_grafico.winfo_height()
        margin = 40
        
        x_min, x_max, y_min, y_max = self.rango_grafico
        
        # Dibujar línea para 'a' si está en el rango visible
        if x_min <= a <= x_max:
            canvas_x_a = margin + (a - x_min) * (width - 2*margin) / (x_max - x_min)
            linea_a = self.canvas_grafico.create_line(canvas_x_a, margin, canvas_x_a, height-margin, 
                                                     fill="red", width=2, dash=(5, 5))
            texto_a = self.canvas_grafico.create_text(canvas_x_a, margin-10, text=f"{a:.2f}", 
                                                     fill="red", font=("Arial", 9, "bold"))
            self.lineas_intervalo.extend([linea_a, texto_a])
        
        # Dibujar línea para 'b' si está en el rango visible
        if x_min <= b <= x_max:
            canvas_x_b = margin + (b - x_min) * (width - 2*margin) / (x_max - x_min)
            linea_b = self.canvas_grafico.create_line(canvas_x_b, margin, canvas_x_b, height-margin, 
                                                     fill="red", width=2, dash=(5, 5))
            texto_b = self.canvas_grafico.create_text(canvas_x_b, margin-10, text=f"{b:.2f}", 
                                                     fill="red", font=("Arial", 9, "bold"))
            self.lineas_intervalo.extend([linea_b, texto_b])
    
    def validar_botones(self):
        """Valida y actualiza el estado de los botones"""
        # Habilitar botón de encontrar raíz solo si todos los campos están llenos
        if all(entry.get().strip() for entry in [self.entry_function, self.entry_a, self.entry_b, self.entry_tolerance]):
            self.run_button.config(state="normal")
        else:
            self.run_button.config(state="disabled")

    def ejecutar_metodo(self):
        try:
            func_str = self.entry_function.get().strip()
            tol_text = self.entry_tolerance.get().strip()
            a_text = self.entry_a.get().strip()
            b_text = self.entry_b.get().strip()

            # Validar entradas
            try:
                a = float(a_text)
                b = float(b_text)
                tolerance = float(tol_text)
            except ValueError:
                messagebox.showerror("Error", "Los valores deben ser numéricos.")
                return
            
            # Validaciones adicionales
            if a >= b:
                messagebox.showerror("Error", "El valor 'a' debe ser menor que 'b'.")
                return
            
            if tolerance <= 0 or tolerance > 1:
                messagebox.showerror("Error", "El error debe estar entre 0 y 1 (formato decimal).")
                return
            
            max_iter = self.max_iterations

            # Ejecutar método
            exito, resultado, iteraciones_data = ejecutar_metodo_regla_falsa(func_str, a, b, tolerance, max_iter)
            
            if not exito:
                messagebox.showerror("Error", resultado)
                return

            # Mostrar resultados
            self.mostrar_resultados(iteraciones_data)
            
            # Dibujar gráfico con zoom en el intervalo [a, b]
            self.rango_grafico = dibujar_grafico(self.canvas_grafico, self.entry_function, intervalo=(a, b))
            dibujar_punto_raiz(self.canvas_grafico, resultado['raiz'], self.rango_grafico)
            
            # Redibujar las líneas del intervalo después de mostrar la raíz
            self.dibujar_lineas_intervalo(a, b)
            
            # Mostrar mensaje final
            if resultado['convergio']:
                messagebox.showinfo("Resultado", 
                    f"Se encontró la raíz {resultado['raiz']:.10f} en el número de iteración {resultado['iteracion']} con un error {resultado['error']:.8f}")
            else:
                messagebox.showwarning("Advertencia", 
                    f"Se alcanzó el máximo de iteraciones ({self.max_iterations}). Raíz aproximada: {resultado['raiz']:.10f}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def click_grafico(self, event):
        """Maneja los clics en la gráfica para seleccionar intervalos"""
        if not self.rango_grafico:
            return
        
        # Convertir coordenadas del canvas a coordenadas matemáticas
        width = self.canvas_grafico.winfo_width()
        height = self.canvas_grafico.winfo_height()
        margin = 40
        
        # Ignorar clics fuera del área de graficación
        if event.x < margin or event.x > width-margin or event.y < margin or event.y > height-margin:
            return
        
        x_min, x_max, y_min, y_max = self.rango_grafico
        
        # Calcular x matemático
        x_math = x_min + (event.x - margin) * (x_max - x_min) / (width - 2*margin)
        
        # Determinar si este valor debe ir en 'a' o 'b' según su posición
        if self.valor_a is None and self.valor_b is None:
            # Primer valor - asignar a 'a'
            self.valor_a = x_math
            self.entry_a.delete(0, tk.END)
            self.entry_a.insert(0, f"{x_math:.4f}")
            
        elif self.valor_a is not None and self.valor_b is None:
            # Ya hay un valor en 'a', determinar dónde va este nuevo valor
            if x_math < self.valor_a:
                # El nuevo valor es menor, va en 'a' y el anterior pasa a 'b'
                self.valor_b = self.valor_a
                self.valor_a = x_math
                self.entry_a.delete(0, tk.END)
                self.entry_a.insert(0, f"{x_math:.4f}")
                self.entry_b.delete(0, tk.END)
                self.entry_b.insert(0, f"{self.valor_b:.4f}")
            else:
                # El nuevo valor es mayor, va en 'b'
                self.valor_b = x_math
                self.entry_b.delete(0, tk.END)
                self.entry_b.insert(0, f"{x_math:.4f}")
                
        else:
            # Ya hay valores en ambos, determinar cuál reemplazar
            if abs(x_math - self.valor_a) < abs(x_math - self.valor_b):
                # Más cerca de 'a', reemplazar 'a'
                self.valor_a = x_math
                self.entry_a.delete(0, tk.END)
                self.entry_a.insert(0, f"{x_math:.4f}")
            else:
                # Más cerca de 'b', reemplazar 'b'
                self.valor_b = x_math
                self.entry_b.delete(0, tk.END)
                self.entry_b.insert(0, f"{x_math:.4f}")
            
            # Asegurar que 'a' sea siempre el menor
            if self.valor_a > self.valor_b:
                self.valor_a, self.valor_b = self.valor_b, self.valor_a
                self.entry_a.delete(0, tk.END)
                self.entry_a.insert(0, f"{self.valor_a:.4f}")
                self.entry_b.delete(0, tk.END)
                self.entry_b.insert(0, f"{self.valor_b:.4f}")
        
        # Redibujar las líneas del intervalo
        self.actualizar_intervalo_grafico()
        
        # Validar botones
        self.validar_botones()
    
    def graficar_ecuacion(self):
        """Grafica la ecuación sin ejecutar el método"""
        try:
            func_str = self.entry_function.get().strip()
            if not func_str:
                return
                
            # Validar ecuación
            valida, mensaje = validar_ecuacion(func_str)
            if not valida:
                messagebox.showerror("Error", f"Ecuación inválida: {mensaje}")
                return
            
            # Limpiar gráfico y selección anterior
            self.limpiar_grafico()
            
            # Dibujar gráfico y guardar el rango
            self.rango_grafico = dibujar_grafico(self.canvas_grafico, self.entry_function)
            
            # Si hay valores en los campos de intervalo, dibujar las líneas
            self.actualizar_intervalo_grafico()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar: {str(e)}")
    
    def convertir_a_latex(self, func_str):
        """Convierte la función a formato LaTeX"""
        import re
        
        latex_str = func_str
        
        # Reemplazar constantes
        latex_str = latex_str.replace('pi', r'\pi')
        latex_str = re.sub(r'\be\b', 'e', latex_str)
        
        # Reemplazar funciones con formato LaTeX
        latex_str = re.sub(r'root\(([^,]+),([^)]+)\)', r'\\sqrt[\2]{\1}', latex_str)
        latex_str = re.sub(r'sqrt\(([^)]+)\)', r'\\sqrt{\1}', latex_str)
        latex_str = re.sub(r'cbrt\(([^)]+)\)', r'\\sqrt[3]{\1}', latex_str)
        
        # Funciones trigonométricas
        latex_str = re.sub(r'\bsin\(', r'\\sin(', latex_str)
        latex_str = re.sub(r'\bcos\(', r'\\cos(', latex_str)
        latex_str = re.sub(r'\btan\(', r'\\tan(', latex_str)
        latex_str = re.sub(r'\basin\(', r'\\arcsin(', latex_str)
        latex_str = re.sub(r'\bacos\(', r'\\arccos(', latex_str)
        latex_str = re.sub(r'\batan\(', r'\\arctan(', latex_str)
        
        # Logaritmos
        latex_str = re.sub(r'\bln\(', r'\\ln(', latex_str)
        latex_str = re.sub(r'\blog10\(', r'\\log_{10}(', latex_str)
        latex_str = re.sub(r'\blog2\(', r'\\log_{2}(', latex_str)
        latex_str = re.sub(r'\blogb\(([^,]+),([^)]+)\)', r'\\log_{\2}(\1)', latex_str)
        
        # Exponenciales - manejar exp() antes de procesar potencias
        latex_str = re.sub(r'\bexp\(([^)]+)\)', r'e^{\1}', latex_str)
        
        # Valor absoluto
        latex_str = re.sub(r'abs\(([^)]+)\)', r'|\1|', latex_str)
        
        # Convertir ^ a formato LaTeX (manejar expresiones complejas)
        # Primero convertir ** a ^
        latex_str = latex_str.replace('**', '^')
        
        # Convertir potencias simples (números)
        latex_str = re.sub(r'\^([0-9]+)', r'^{\1}', latex_str)
        
        # Convertir potencias con variables o expresiones (e^x, x^n, etc)
        latex_str = re.sub(r'\^([a-zA-Z])', r'^{\1}', latex_str)
        
        # Convertir potencias con paréntesis o expresiones complejas
        latex_str = re.sub(r'\^\(([^)]+)\)', r'^{\1}', latex_str)
        
        # Multiplicación implícita y explícita (antes de procesar fracciones complejas)
        latex_str = re.sub(r'(\d)\s*\*\s*x', r'\1x', latex_str)
        # Reemplazar * por \cdot con espacio para evitar unión con siguiente carácter
        latex_str = latex_str.replace('*', r'\cdot ')
        
        # Fracciones con expresiones (después de procesar multiplicación)
        # (expresión)/(expresión)
        latex_str = re.sub(r'\(([^)]+)\)/\(([^)]+)\)', r'\\frac{\1}{\2}', latex_str)
        # (expresión)/número o (expresión)/variable
        latex_str = re.sub(r'\(([^)]+)\)/(\d+)', r'\\frac{\1}{\2}', latex_str)
        latex_str = re.sub(r'\(([^)]+)\)/([a-zA-Z]+)', r'\\frac{\1}{\2}', latex_str)
        # número/(expresión) o variable/(expresión)
        latex_str = re.sub(r'(\d+)/\(([^)]+)\)', r'\\frac{\1}{\2}', latex_str)
        latex_str = re.sub(r'([a-zA-Z]+)/\(([^)]+)\)', r'\\frac{\1}{\2}', latex_str)
        
        # Fracciones - convertir a formato \frac{numerador}{denominador}
        # Fracciones simples: número/número o número/variable
        latex_str = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', latex_str)
        latex_str = re.sub(r'(\d+)/([a-zA-Z])', r'\\frac{\1}{\2}', latex_str)
        latex_str = re.sub(r'([a-zA-Z])/(\d+)', r'\\frac{\1}{\2}', latex_str)
        latex_str = re.sub(r'1/x', r'\\frac{1}{x}', latex_str)
        
        return latex_str
    
    def mostrar_ecuacion_latex(self, func_str):
        """Muestra la ecuación usando renderizado LaTeX de matplotlib"""
        self.ax_ecuacion.clear()
        self.ax_ecuacion.axis('off')
        
        if func_str:
            latex_str = self.convertir_a_latex(func_str)
            latex_completo = f'$f(x) = {latex_str}$'
            
            try:
                self.ax_ecuacion.text(0.5, 0.5, latex_completo, 
                                     fontsize=14, ha='center', va='center',
                                     color='#1565C0', weight='bold')
            except:
                self.ax_ecuacion.text(0.5, 0.5, f'f(x) = {func_str}', 
                                     fontsize=12, ha='center', va='center',
                                     color='#1565C0')
        else:
            self.ax_ecuacion.text(0.5, 0.5, 'f(x) = ', 
                                 fontsize=14, ha='center', va='center',
                                 color='#1565C0')
        
        self.canvas_ecuacion.draw()
    
    def mostrar_ecuacion_algebraica(self, func_str):
        """Muestra la ecuación en formato LaTeX"""
        self.mostrar_ecuacion_latex(func_str)
    
    def _mostrar_ecuacion_algebraica_old(self, func_str):
        """Muestra la ecuación en formato algebraico mejorado"""
        import re
        
        # Formatear la ecuación para mostrarla de manera más legible
        ecuacion_formateada = func_str
        
        # Reemplazar constantes con símbolos Unicode
        ecuacion_formateada = ecuacion_formateada.replace('pi', 'π')
        ecuacion_formateada = re.sub(r'\be\b', 'e', ecuacion_formateada)
        
        # Reemplazar funciones con símbolos matemáticos mejorados
        ecuacion_formateada = ecuacion_formateada.replace('sqrt(', '√(')
        ecuacion_formateada = ecuacion_formateada.replace('cbrt(', '∛(')
        ecuacion_formateada = ecuacion_formateada.replace('abs(', '|')
        ecuacion_formateada = ecuacion_formateada.replace('ln(', 'ln(')
        ecuacion_formateada = ecuacion_formateada.replace('log10(', 'log₁₀(')
        ecuacion_formateada = ecuacion_formateada.replace('log2(', 'log₂(')
        
        # Reemplazar funciones trigonométricas
        ecuacion_formateada = ecuacion_formateada.replace('sin(', 'sin(')
        ecuacion_formateada = ecuacion_formateada.replace('cos(', 'cos(')
        ecuacion_formateada = ecuacion_formateada.replace('tan(', 'tan(')
        ecuacion_formateada = ecuacion_formateada.replace('asin(', 'arcsin(')
        ecuacion_formateada = ecuacion_formateada.replace('acos(', 'arccos(')
        ecuacion_formateada = ecuacion_formateada.replace('atan(', 'arctan(')
        
        # Reemplazar funciones hiperbólicas
        ecuacion_formateada = ecuacion_formateada.replace('sinh(', 'sinh(')
        ecuacion_formateada = ecuacion_formateada.replace('cosh(', 'cosh(')
        ecuacion_formateada = ecuacion_formateada.replace('tanh(', 'tanh(')
        ecuacion_formateada = ecuacion_formateada.replace('asinh(', 'arcsinh(')
        ecuacion_formateada = ecuacion_formateada.replace('acosh(', 'arccosh(')
        ecuacion_formateada = ecuacion_formateada.replace('atanh(', 'arctanh(')
        
        # Manejar exponenciales con mejor formato
        ecuacion_formateada = re.sub(r'exp\(([^)]+)\)', r'e^(\1)', ecuacion_formateada)
        
        # Convertir potencias a superindices Unicode
        superscripts = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', 
                       '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
                       '-': '⁻', '+': '⁺', '(': '⁽', ')': '⁾'}
        
        # Reemplazar potencias simples
        for num, sup in superscripts.items():
            ecuacion_formateada = ecuacion_formateada.replace(f'^{num}', sup)
        
        # Reemplazar ** con ^ para otras potencias
        ecuacion_formateada = ecuacion_formateada.replace('**', '^')
        
        # Reemplazar multiplicación implícita y explícita
        ecuacion_formateada = re.sub(r'(\d)\s*\*\s*x', r'\1x', ecuacion_formateada)
        ecuacion_formateada = re.sub(r'x\s*\*\s*(\d)', r'x\1', ecuacion_formateada)
        ecuacion_formateada = ecuacion_formateada.replace('*', '·')  # Punto medio
        
        # Manejar fracciones simples
        ecuacion_formateada = ecuacion_formateada.replace('1/x', '1/x')
        
        # Cerrar paréntesis de valor absoluto
        if ecuacion_formateada.count('|') % 2 == 1:
            ecuacion_formateada = ecuacion_formateada.replace('|', '|', 1) + '|'
        
        # Formato final con estilo matemático
        self.label_ecuacion.config(text=f"f(x) = {ecuacion_formateada}")
    
    def mostrar_resultados(self, iteraciones_data):
        self.texto_resultados.config(state=tk.NORMAL)
        self.texto_resultados.delete("1.0", tk.END)
        
        for datos in iteraciones_data:
            texto = (f"Iteración {datos['iteracion']}:\n"
                     f"  a = {datos['a']:.8f}, b = {datos['b']:.8f}, xr = {datos['xr']:.8f}\n"
                     f"  f(a) = {datos['fa']:.8e}, f(b) = {datos['fb']:.8e}, f(xr) = {datos['fxr']:.8e}\n"
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