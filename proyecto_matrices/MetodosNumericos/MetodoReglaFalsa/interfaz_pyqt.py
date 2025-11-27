#!/usr/bin/env python3
"""
Interfaz PyQt5 para el Método de la Regla Falsa
Diseño inspirado en Microsoft Mathematics
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from matematicas import validar_ecuacion, preprocesar_funcion, evaluar_funcion
from metodo_regla_falsa import ejecutar_metodo_regla_falsa

class IterationsTableDialog(QDialog):
    """Ventana emergente para mostrar la tabla de iteraciones"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tabla de Iteraciones - Método de la Regla Falsa")
        self.setModal(True)
        self.resize(800, 400)
        
        layout = QVBoxLayout(self)
        
        # Tabla de iteraciones
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Iter", "a", "b", "xr", "f(a)", "f(b)", "f(xr)", "Error"])
        self.table.setFont(QFont("Consolas", 10))
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fefefe;
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #ccc;
                alternate-background-color: #f5f5dc;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #ccc;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 3px;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def populate_table(self, iterations):
        """Llena la tabla con los datos de iteraciones"""
        self.table.setRowCount(len(iterations))
        
        for i, data in enumerate(iterations):
            self.table.setItem(i, 0, QTableWidgetItem(str(data['iteracion'])))
            self.table.setItem(i, 1, QTableWidgetItem(f"{data['a']:.6f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{data['b']:.6f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{data['xr']:.6f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{data['fa']:.4e}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{data['fb']:.4e}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{data['fxr']:.4e}"))
            self.table.setItem(i, 7, QTableWidgetItem(f"{data['error_rel']:.6f}"))
        
        self.table.resizeColumnsToContents()

class MathCanvas(FigureCanvas):
    """Canvas personalizado para gráficos matemáticos"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_facecolor('#fafafa')
        
        # Hacer el canvas focusable para recibir eventos de teclado
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Variables para pan (arrastrar)
        self.press = None
        self.current_func = None
        self.root_positions = []  # Almacenar posiciones de raíces
        self.tooltip_annotation = None
        self.alt_pressed = False  # Estado de la tecla ALT
        
        # Conectar eventos de mouse
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('motion_notify_event', self.on_motion)
        self.mpl_connect('scroll_event', self.on_scroll)
    
    def on_press(self, event):
        """Inicia el arrastre"""
        if event.inaxes != self.ax:
            return
        self.press = (event.xdata, event.ydata)
        # Dar foco al canvas para recibir eventos de teclado
        self.setFocus()
    
    def on_motion(self, event):
        """Maneja el arrastre del gráfico y tooltips"""
        if event.inaxes != self.ax:
            return
        
        # Si está arrastrando
        if self.press is not None:
            dx = event.xdata - self.press[0]
            dy = event.ydata - self.press[1]
            
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            
            self.draw_idle()
        else:
            # Mostrar tooltip solo si ALT está presionado y está cerca de una raíz
            if self.alt_pressed:
                self.show_root_tooltip(event)
            else:
                # Ocultar tooltip si ALT no está presionado
                if self.tooltip_annotation:
                    self.tooltip_annotation.set_visible(False)
                    self.draw_idle()
    
    def on_release(self, event):
        """Termina el arrastre"""
        self.press = None
        self.draw_idle()
    
    def on_scroll(self, event):
        """Maneja el zoom con rueda del mouse"""
        if event.inaxes != self.ax:
            return
        
        scale_factor = 1.1 if event.step < 0 else 1/1.1
        
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        x_center = event.xdata
        y_center = event.ydata
        
        x_range = (xlim[1] - xlim[0]) * scale_factor
        y_range = (ylim[1] - ylim[0]) * scale_factor
        
        self.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
        self.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
        
        self.draw_idle()
    
    def keyPressEvent(self, event):
        """Maneja eventos de tecla presionada"""
        if event.key() == Qt.Key_Alt:
            self.alt_pressed = True
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Maneja eventos de tecla liberada"""
        if event.key() == Qt.Key_Alt:
            self.alt_pressed = False
            # Ocultar tooltip al soltar ALT
            if self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
                self.draw_idle()
        super().keyReleaseEvent(event)
    
    def show_root_tooltip(self, event):
        """Muestra tooltip cuando el mouse está cerca de una raíz"""
        if not self.root_positions or event.xdata is None or event.ydata is None:
            if self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
                self.draw_idle()
            return
        
        # Buscar raíz más cercana
        closest_root = None
        min_distance = float('inf')
        tolerance = 0.5  # Tolerancia en unidades del gráfico
        
        for root_x in self.root_positions:
            distance = abs(event.xdata - root_x)
            if distance < tolerance and distance < min_distance:
                min_distance = distance
                closest_root = root_x
        
        if closest_root is not None:
            # Mostrar tooltip
            if self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
            
            self.tooltip_annotation = self.ax.annotate(
                f'x ≈ {closest_root:.3f}',
                xy=(closest_root, 0), xytext=(15, 20),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.5, edgecolor='none'),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='orange', alpha=0.5),
                fontsize=8, color='darkblue'
            )
            self.draw_idle()
        else:
            # Ocultar tooltip
            if self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
                self.draw_idle()
    
    def detect_roots_for_tooltips(self, x, y):
        """Detecta raíces para tooltips sin marcarlas visualmente"""
        crossings = []
        
        for i in range(1, len(y)):
            if not (np.isnan(y[i-1]) or np.isnan(y[i])):
                if y[i-1] * y[i] < 0:  # Cambio de signo
                    # Interpolación lineal para encontrar el cruce
                    x_cross = x[i-1] - y[i-1] * (x[i] - x[i-1]) / (y[i] - y[i-1])
                    crossings.append(x_cross)
        
        # Guardar todas las raíces para tooltips
        self.root_positions = crossings[:10]  # Hasta 10 raíces
        
    def plot_function(self, func_str, x_range=(-10, 10), interval=None, show_roots=False):
        """Grafica una función matemática con rango inteligente"""
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)
        self.ax.set_facecolor('#fafafa')
        
        try:
            func_str_proc = preprocesar_funcion(func_str)
            
            if interval:
                a, b = interval
                margin = max(abs(b - a) * 1.5, 5)
                x_min, x_max = a - margin, b + margin
            else:
                # Encontrar rango óptimo automáticamente
                x_min, x_max = self.find_optimal_range(func_str_proc)
                
            # Usar número fijo de puntos para mejor rendimiento
            num_points = 1500
            x = np.linspace(x_min, x_max, num_points)
            
            # Guardar función actual para redibujado
            self.current_func = func_str_proc
            y = []
            
            for xi in x:
                try:
                    yi = evaluar_funcion(func_str_proc, xi)
                    if abs(yi) < 1e8:  # Filtrar valores extremos
                        y.append(yi)
                    else:
                        y.append(np.nan)
                except:
                    y.append(np.nan)
            
            y = np.array(y)
            
            # Configurar límites Y inteligentes
            valid_y = y[~np.isnan(y)]
            if len(valid_y) > 0:
                # Para funciones polinómicas, usar rango completo para mostrar comportamiento
                if any(char in func_str for char in ['^3', '^4', '^5']) or '**3' in func_str or '**4' in func_str:
                    # Función polinómica de grado alto - mostrar rango amplio
                    y_sorted = np.sort(valid_y)
                    n = len(y_sorted)
                    
                    # Para funciones cúbicas, usar rango Y limitado
                    y_min = np.min(valid_y)
                    y_max = np.max(valid_y)
                    
                    # Limitar rango Y a -20, 20
                    y_min = max(y_min, -20)
                    y_max = min(y_max, 20)
                    
                    # Asegurar que el rango no sea demasiado pequeño
                    if y_max - y_min < 10:
                        y_center = (y_max + y_min) / 2
                        y_min = max(y_center - 10, -20)
                        y_max = min(y_center + 10, 20)
                    
                    self.ax.set_ylim(y_min, y_max)
                else:
                    # Otras funciones - usar percentiles estándar
                    y_min = np.percentile(valid_y, 10)
                    y_max = np.percentile(valid_y, 90)
                    y_range = y_max - y_min
                    
                    if y_range < 1e-10:  # Función constante
                        y_center = np.mean(valid_y)
                        self.ax.set_ylim(y_center - 1, y_center + 1)
                    else:
                        margin = y_range * 0.2
                        self.ax.set_ylim(y_min - margin, y_max + margin)
            
            # Graficar función
            self.ax.plot(x, y, 'b-', linewidth=1.5, label=f'f(x) = {func_str}')
            
            # Ejes de referencia
            self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.6, linewidth=1)
            self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.6, linewidth=1)
            
            # Detectar raíces para tooltips (siempre)
            self.detect_roots_for_tooltips(x, y)
            
            # Solo marcar raíces si se solicita explícitamente
            if show_roots:
                self.mark_zero_crossings(x, y, interval)
            
            if interval:
                self.ax.axvline(x=interval[0], color='r', linestyle='--', alpha=0.7, label=f'a = {interval[0]:.4f}')
                self.ax.axvline(x=interval[1], color='r', linestyle='--', alpha=0.7, label=f'b = {interval[1]:.4f}')
            
            self.ax.set_xlabel('x', fontsize=11)
            self.ax.set_ylabel('f(x)', fontsize=11)
            self.ax.legend(fontsize=10)
            self.ax.set_title(f'Gráfico de f(x) = {func_str}', fontsize=12, pad=15)
            
            # Configurar ejes y grid con cuadrícula de 1 en 1
            self.ax.tick_params(axis='both', which='major', labelsize=10)
            
            # Configurar ticks solo si el rango es razonable
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            
            import matplotlib.ticker as ticker
            
            # Solo aplicar grid de 1 en 1 si el rango es menor a 50 unidades
            if x_range <= 50:
                self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
            if y_range <= 50:
                self.ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
            
            # Grid principal
            self.ax.grid(True, which='major', alpha=0.4, linewidth=0.8, color='gray')
            
            # Ajustar límites para funciones cúbicas sin cambiar aspecto de la línea
            if any(char in func_str for char in ['^3', '**3']):
                # Limitar rango Y a -20, 20 para funciones cúbicas
                ylim = self.ax.get_ylim()
                
                # Aplicar límites de -20 a 20
                y_min = max(ylim[0], -20)
                y_max = min(ylim[1], 20)
                
                self.ax.set_ylim(y_min, y_max)
                
                # Mantener aspecto automático para preservar forma de la línea
                self.ax.set_aspect('auto')
            
            self.draw_idle()
            
        except Exception as e:
            self.ax.text(0.5, 0.5, f'Error al graficar: {str(e)}', transform=self.ax.transAxes, 
                        ha='center', va='center', fontsize=12, color='red')
            self.draw_idle()
    
    def find_optimal_range(self, func_str_proc):
        """Encuentra el rango óptimo para mostrar la función"""
        from matematicas import preprocesar_funcion
        
        # Rangos de prueba adaptados al tipo de función
        original_func = preprocesar_funcion(func_str_proc) if hasattr(self, 'original_func_str') else func_str_proc
        
        # Para funciones polinómicas cúbicas o superiores, usar rango amplio por defecto
        if any(pattern in str(original_func) for pattern in ['^3', '**3', '^4', '**4']):
            # Rango amplio para funciones cúbicas
            test_ranges = [(-10, 10), (-8, 8), (-12, 12), (-6, 6)]
        else:
            test_ranges = [(-10, 10), (-15, 15), (-8, 8), (-20, 20)]
        
        best_range = (-5, 5)
        max_score = 0
        
        for x_min, x_max in test_ranges:
            x_test = np.linspace(x_min, x_max, 200)
            y_test = []
            crossings = 0
            variation = 0
            
            for xi in x_test:
                try:
                    yi = evaluar_funcion(func_str_proc, xi)
                    if abs(yi) < 1e8:
                        y_test.append(yi)
                    else:
                        y_test.append(np.nan)
                except:
                    y_test.append(np.nan)
            
            # Contar cambios de signo y variación
            valid_y = [y for y in y_test if not np.isnan(y)]
            if len(valid_y) > 10:
                for i in range(1, len(y_test)):
                    if not (np.isnan(y_test[i-1]) or np.isnan(y_test[i])):
                        if y_test[i-1] * y_test[i] < 0:
                            crossings += 1
                
                # Medir variación para capturar comportamiento interesante
                if len(valid_y) > 1:
                    variation = np.std(valid_y)
                
                # Puntaje basado en cruces y variación
                score = crossings * 100 + min(variation, 50)
                
                if score > max_score:
                    max_score = score
                    best_range = (x_min, x_max)
        
        return best_range
    
    def mark_zero_crossings(self, x, y, interval=None):
        """Marca las intersecciones aproximadas con el eje X"""
        crossings = []
        
        for i in range(1, len(y)):
            if not (np.isnan(y[i-1]) or np.isnan(y[i])):
                if y[i-1] * y[i] < 0:  # Cambio de signo
                    # Interpolación lineal para encontrar el cruce
                    x_cross = x[i-1] - y[i-1] * (x[i] - x[i-1]) / (y[i] - y[i-1])
                    
                    # Si hay intervalo especificado, solo mostrar raíces dentro del intervalo
                    if interval is None or (interval[0] <= x_cross <= interval[1]):
                        crossings.append(x_cross)
        
        # Guardar posiciones para tooltips
        self.root_positions = crossings[:5]
        
        # Marcar hasta 5 cruces para no saturar el gráfico
        for i, x_cross in enumerate(crossings[:5]):
            self.ax.plot(x_cross, 0, 'go', markersize=6, 
                        label=f'Raíz ≈ {x_cross:.3f}' if i == 0 else '')
            self.ax.annotate(f'{x_cross:.3f}', (x_cross, 0), 
                           xytext=(5, 10), textcoords='offset points',
                           fontsize=9, color='green',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    
    def mark_root(self, root_x):
        """Marca la raíz en el gráfico"""
        # Solo agregar label si no hay otras raíces ya marcadas
        existing_labels = [t.get_text() for t in self.ax.get_legend().get_texts()] if self.ax.get_legend() else []
        has_root_label = any('Raíz' in label for label in existing_labels)
        
        label = None if has_root_label else f'Raíz: {root_x:.6f}'
        self.ax.plot(root_x, 0, 'go', markersize=8, label=label)
        self.ax.legend()
        self.draw()

class FunctionButtonsWidget(QWidget):
    """Widget con botones de funciones matemáticas"""
    function_inserted = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # Widget contenedor que se adapta al tamaño
        container = QWidget()
        
        # Layout que se adapta al ancho disponible
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Calcular tamaño necesario para mostrar todos los botones
        button_width = 65
        button_height = 26
        buttons_per_row = 6
        num_rows = 4
        spacing = 2
        margins = 10
        
        # Tamaño mínimo del contenedor
        min_width = (button_width * buttons_per_row) + (spacing * (buttons_per_row - 1)) + margins
        min_height = (button_height * num_rows) + (spacing * (num_rows - 1)) + margins
        
        container.setMinimumSize(min_width, min_height)
        
        # Definir botones de funciones (completos como en Tkinter)
        functions = [
            [('sin', 'sin(x)'), ('cos', 'cos(x)'), ('tan', 'tan(x)'), ('asin', 'asin(x)'), ('acos', 'acos(x)'), ('atan', 'atan(x)')],
            [('sinh', 'sinh(x)'), ('cosh', 'cosh(x)'), ('tanh', 'tanh(x)'), ('exp', 'exp(x)'), ('ln', 'ln(x)'), ('log₁₀', 'log10(x)')],
            [('log₂', 'log2(x)'), ('√', 'sqrt(x)'), ('³√', 'cbrt(x)'), ('ⁿ√', 'root(x,3)'), ('x²', 'x^2'), ('|x|', 'abs(x)')],
            [('π', 'pi'), ('e', 'e'), ('x³', 'x^3'), ('xⁿ', 'x^'), ('logₓ', 'logb(x,10)'), ('1/x', '1/x')]
        ]
        
        # Tooltips para botones
        tooltips = {
            'sin(x)': 'Digitar: sin(x)', 'cos(x)': 'Digitar: cos(x)', 'tan(x)': 'Digitar: tan(x)',
            'asin(x)': 'Digitar: asin(x)', 'acos(x)': 'Digitar: acos(x)', 'atan(x)': 'Digitar: atan(x)',
            'sinh(x)': 'Digitar: sinh(x)', 'cosh(x)': 'Digitar: cosh(x)', 'tanh(x)': 'Digitar: tanh(x)',
            'exp(x)': 'Digitar: exp(x)', 'ln(x)': 'Digitar: ln(x)', 'log10(x)': 'Digitar: log10(x)',
            'log2(x)': 'Digitar: log2(x)', 'sqrt(x)': 'Digitar: sqrt(x)', 'cbrt(x)': 'Digitar: cbrt(x)',
            'root(x,3)': 'Digitar: root(x,n)', 'x^2': 'Digitar: x^2', 'abs(x)': 'Digitar: abs(x)',
            'pi': 'Digitar: pi', 'e': 'Digitar: e', 'x^3': 'Digitar: x^3',
            'x^': 'Digitar: x^n', 'logb(x,10)': 'Digitar: logb(x,b)', '1/x': 'Digitar: 1/x'
        }
        
        # Crear botones en layout adaptativo
        all_buttons = []
        for func_row in functions:
            for text, func in func_row:
                all_buttons.append((text, func))
        
        # Crear filas dinámicas
        current_row = QHBoxLayout()
        current_row.setSpacing(2)
        buttons_in_row = 0
        
        for text, func in all_buttons:
            btn = QPushButton(text)
            btn.setMinimumSize(50, 26)
            btn.setMaximumSize(65, 26)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 2px solid #2196F3;
                    border-radius: 4px;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 11px;
                    font-weight: bold;
                    color: #0D47A1;
                }
                QPushButton:hover {
                    background-color: #E3F2FD;
                    border-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #BBDEFB;
                    border-color: #0D47A1;
                }
            """)
            btn.setToolTip(tooltips.get(func, f'Insertar {func}'))
            btn.clicked.connect(lambda checked, f=func: self.function_inserted.emit(f))
            
            current_row.addWidget(btn)
            buttons_in_row += 1
            
            # Crear nueva fila cada 6 botones
            if buttons_in_row >= 6:
                main_layout.addLayout(current_row)
                current_row = QHBoxLayout()
                current_row.setSpacing(2)
                buttons_in_row = 0
        
        # Añadir última fila si tiene botones
        if buttons_in_row > 0:
            main_layout.addLayout(current_row)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.setLayout(main_layout)

class InterfazReglaFalsaPyQt(QMainWindow):
    """Interfaz principal estilo Microsoft Mathematics"""
    
    def __init__(self):
        super().__init__()
        self.iterations_data = []  # Almacenar datos de iteraciones
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle("Método de la Regla Falsa")
        
        # Obtener dimensiones de pantalla
        screen = QApplication.desktop().screenGeometry()
        
        # Configurar ventana para que se adapte a la pantalla
        self.setMinimumSize(1200, 700)
        self.resize(min(1600, screen.width() - 100), min(900, screen.height() - 100))
        
        # Centrar ventana en pantalla
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal con 3 paneles
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Panel izquierdo (controles) - 30% del ancho
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 3)  # stretch factor 3
        
        # Panel central (pasos detallados) - 35% del ancho
        center_panel = self.create_steps_panel()
        main_layout.addWidget(center_panel, 4)  # stretch factor 4
        
        # Panel derecho (gráfico) - 35% del ancho
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 4)  # stretch factor 4
        
        # Barra de estado
        self.statusBar().showMessage("Listo")
        self.statusBar().setStyleSheet("QStatusBar { color: black; }")
        
        # Crear menú
        self.create_menu()
    
    def show_error_message(self, message):
        """Muestra mensaje de error en rojo oscuro"""
        self.statusBar().setStyleSheet("QStatusBar { color: #8B0000; font-weight: bold; }")
        self.statusBar().showMessage(f"✗ {message}")
    
    def show_success_message(self, message):
        """Muestra mensaje de éxito en verde"""
        self.statusBar().setStyleSheet("QStatusBar { color: #006400; font-weight: bold; }")
        self.statusBar().showMessage(f"✓ {message}")
    
    def show_normal_message(self, message):
        """Muestra mensaje normal en negro"""
        self.statusBar().setStyleSheet("QStatusBar { color: black; }")
        self.statusBar().showMessage(message)
        
    def create_menu(self):
        """Crea el menú principal"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('Archivo')
        
        new_action = QAction('Nuevo', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_calculation)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Salir', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu('Ayuda')
        
        about_action = QAction('Acerca de', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_left_panel(self):
        """Crea el panel izquierdo con controles"""
        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        # Grupo de función
        func_group = QGroupBox("Función Matemática")
        func_layout = QVBoxLayout(func_group)
        
        # Campo de función con LaTeX preview
        self.function_input = QLineEdit("x^3 - x - 2")
        self.function_input.setFont(QFont("Consolas", 14))
        self.function_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        func_layout.addWidget(QLabel("f(x) ="))
        func_layout.addWidget(self.function_input)
        
        # Preview de la ecuación con matplotlib
        self.equation_canvas = FigureCanvas(Figure(figsize=(5, 0.8), facecolor='white'))
        self.equation_ax = self.equation_canvas.figure.add_subplot(111)
        self.equation_ax.axis('off')
        self.equation_canvas.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.equation_canvas.setFixedHeight(60)
        func_layout.addWidget(self.equation_canvas)
        
        # Botones de funciones con scroll adaptativo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(130)
        scroll_area.setMaximumHeight(180)
        # Altura calculada: 4 filas * 26px + 3 espacios * 2px + márgenes = ~120px
        
        self.function_buttons = FunctionButtonsWidget()
        scroll_area.setWidget(self.function_buttons)
        func_layout.addWidget(scroll_area)
        
        layout.addWidget(func_group)
        
        # Grupo de parámetros
        params_group = QGroupBox("Parámetros del Método")
        params_layout = QFormLayout(params_group)
        
        # Intervalo [a, b]
        interval_layout = QHBoxLayout()
        self.a_input = QLineEdit("1")
        self.b_input = QLineEdit("2")
        self.a_input.setFixedWidth(80)
        self.b_input.setFixedWidth(80)
        
        for input_field in [self.a_input, self.b_input]:
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                }
            """)
        
        interval_layout.addWidget(QLabel("a ="))
        interval_layout.addWidget(self.a_input)
        interval_layout.addWidget(QLabel("b ="))
        interval_layout.addWidget(self.b_input)
        interval_layout.addStretch()
        
        params_layout.addRow("Intervalo [a, b]:", interval_layout)
        
        # Tolerancia
        self.tolerance_input = QLineEdit("0.0001")
        self.tolerance_input.setStyleSheet(self.a_input.styleSheet())
        params_layout.addRow("Error máximo:", self.tolerance_input)
        
        layout.addWidget(params_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.plot_btn = QPushButton("📊 Graficar")
        self.solve_btn = QPushButton("🎯 Encontrar Raíz")
        
        self.plot_btn.setFixedHeight(38)
        self.plot_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1976D2;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border-color: #0D47A1;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        self.solve_btn.setFixedHeight(38)
        self.solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #388E3C;
                border-color: #1B5E20;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
        
        buttons_layout.addWidget(self.plot_btn)
        buttons_layout.addWidget(self.solve_btn)
        layout.addLayout(buttons_layout)
        
        # Resumen de resultados (compacto)
        summary_group = QGroupBox("Resumen")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_label = QLabel("Haz clic en 'Encontrar Raíz' para ver resultados")
        self.summary_label.setFont(QFont("Consolas", 10))
        self.summary_label.setStyleSheet("""
            QLabel {
                background-color: #fefefe;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                color: #666;
            }
        """)
        self.summary_label.setWordWrap(True)
        self.summary_label.setMinimumHeight(80)
        summary_layout.addWidget(self.summary_label)
        
        layout.addWidget(summary_group)
        layout.addStretch()
        
        return panel
    
    def create_steps_panel(self):
        """Crea el panel central con pasos detallados del método"""
        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setSpacing(5)
        
        # Título del panel
        title_label = QLabel("Método de la Regla Falsa - Paso a Paso")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Área de texto para mostrar pasos detallados
        self.steps_text = QTextEdit()
        self.steps_text.setFont(QFont("Consolas", 9))
        self.steps_text.setStyleSheet("""
            QTextEdit {
                background-color: #fefefe;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.steps_text.setReadOnly(True)
        self.steps_text.setPlainText("Los pasos detallados del método aparecerán aquí cuando ejecutes 'Encontrar Raíz'.")
        layout.addWidget(self.steps_text, 1)
        
        # Botón para mostrar tabla de iteraciones
        self.show_table_btn = QPushButton("📈 Ver Tabla de Iteraciones")
        self.show_table_btn.setFixedHeight(35)
        self.show_table_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: 2px solid #F57C00;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #F57C00;
                border-color: #E65100;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
            QPushButton:disabled {
                background-color: #ccc;
                border-color: #999;
                color: #666;
            }
        """)
        self.show_table_btn.setEnabled(False)
        self.show_table_btn.clicked.connect(self.show_iterations_table)
        layout.addWidget(self.show_table_btn)
        
        return panel
    
    def create_right_panel(self):
        """Crea el panel derecho con el gráfico"""
        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setSpacing(5)
        
        # Título del gráfico
        title_layout = QHBoxLayout()
        title_label = QLabel("Visualización Gráfica")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Botones de zoom
        zoom_in_btn = QPushButton("🔍+")
        zoom_out_btn = QPushButton("🔍-")
        reset_zoom_btn = QPushButton("🏠")
        
        # Configurar botones con mejor visibilidad
        for btn in [zoom_in_btn, zoom_out_btn, reset_zoom_btn]:
            btn.setFixedSize(28, 25)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 2px solid #2196F3;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E3F2FD;
                    border-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #BBDEFB;
                }
            """)
        
        # Agregar tooltips
        zoom_in_btn.setToolTip("Acercar zoom")
        zoom_out_btn.setToolTip("Alejar zoom")
        reset_zoom_btn.setToolTip("Restablecer vista original")
        
        title_layout.addWidget(zoom_in_btn)
        title_layout.addWidget(zoom_out_btn)
        title_layout.addWidget(reset_zoom_btn)
        title_layout.addSpacing(10)  # Espacio adicional para mostrar todos los botones
        
        # Conectar botones de zoom
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_out_btn.clicked.connect(self.zoom_out)
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        
        layout.addLayout(title_layout)
        
        # Canvas del gráfico
        self.canvas = MathCanvas(self, width=8, height=6, dpi=100)
        self.canvas.setMinimumSize(700, 500)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas, 1)  # stretch factor 1
        
        # Información del gráfico
        info_label = QLabel("Haz clic en 'Graficar' para visualizar la función")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        return panel
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.function_input.textChanged.connect(self.validate_function)
        self.function_buttons.function_inserted.connect(self.insert_function)
        self.plot_btn.clicked.connect(self.plot_function)
        self.solve_btn.clicked.connect(self.solve_equation)
        
        # Validación en tiempo real
        for input_field in [self.a_input, self.b_input, self.tolerance_input]:
            input_field.textChanged.connect(self.validate_inputs)
        
        # Limpiar caracteres Unicode al pegar
        self.function_input.textChanged.connect(self.clean_unicode_input)
        
        # Mostrar ecuación inicial
        self.validate_function()
    
    def clean_unicode_input(self):
        """Limpia caracteres Unicode del campo de entrada"""
        from matematicas import limpiar_caracteres_unicode
        
        current_text = self.function_input.text()
        clean_text = limpiar_caracteres_unicode(current_text)
        
        if clean_text != current_text:
            cursor_pos = self.function_input.cursorPosition()
            self.function_input.blockSignals(True)  # Evitar recursión
            self.function_input.setText(clean_text)
            self.function_input.setCursorPosition(min(cursor_pos, len(clean_text)))
            self.function_input.blockSignals(False)
    
    def validate_function(self):
        """Valida la función ingresada"""
        func_str = self.function_input.text().strip()
        
        # Limpiar resultados anteriores al editar
        self.clear_results()
        
        if func_str:
            valid, message = validar_ecuacion(func_str)
            if valid:
                self.show_equation_preview(func_str, True)
                self.show_success_message("Función válida")
            else:
                self.show_equation_preview(f"Error: {message}", False)
                self.show_error_message(message)
        else:
            self.show_equation_preview("", True)
            self.show_normal_message("Ingresa una función")
    
    def validate_inputs(self):
        """Valida las entradas numéricas"""
        try:
            a = float(self.a_input.text())
            b = float(self.b_input.text())
            tol = float(self.tolerance_input.text())
            
            if a >= b:
                self.show_error_message("a debe ser menor que b")
                return False
            if tol <= 0:
                self.show_error_message("la tolerancia debe ser positiva")
                return False
            
            return True
        except ValueError:
            self.show_error_message("valores numéricos inválidos")
            return False
    
    def insert_function(self, func_text):
        """Inserta una función en el campo de entrada"""
        from matematicas import limpiar_caracteres_unicode
        
        cursor_pos = self.function_input.cursorPosition()
        current_text = self.function_input.text()
        
        # Limpiar caracteres Unicode en el texto a insertar
        func_text_clean = limpiar_caracteres_unicode(func_text)
        
        new_text = current_text[:cursor_pos] + func_text_clean + current_text[cursor_pos:]
        self.function_input.setText(new_text)
        self.function_input.setCursorPosition(cursor_pos + len(func_text_clean))
        self.function_input.setFocus()
    
    def plot_function(self):
        """Grafica la función"""
        func_str = self.function_input.text().strip()
        if not func_str:
            QMessageBox.warning(self, "Error", "Ingresa una funcion valida")
            return
        
        try:
            valid, message = validar_ecuacion(func_str)
            if not valid:
                QMessageBox.warning(self, "Error", f"Funcion invalida: {message}")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error de validacion: {str(e)}")
            return
        
        # Mostrar diálogo de espera
        progress = QProgressDialog("Graficando función...", "Cancelar", 0, 0, self)
        progress.setWindowTitle("Espere...")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(500)
        progress.show()
        QApplication.processEvents()
        
        try:
            # Solo usar intervalo si los valores son válidos y diferentes de los por defecto
            interval = None
            try:
                if self.validate_inputs():
                    a = float(self.a_input.text())
                    b = float(self.b_input.text())
                    # Solo usar intervalo si no son los valores por defecto
                    if not (a == 1 and b == 2):
                        interval = (a, b)
            except:
                pass
            
            # Graficar con vista general amplia (sin mostrar raíces)
            # Siempre usar rango inteligente para vista general
            self.canvas.plot_function(func_str, interval=None, show_roots=False)
            self.show_success_message("Función graficada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al graficar: {str(e)}")
        finally:
            progress.close()
    
    def solve_equation(self):
        """Resuelve la ecuación usando el método de regla falsa"""
        if not self.validate_inputs():
            return
        
        func_str = self.function_input.text().strip()
        try:
            valid, message = validar_ecuacion(func_str)
            if not valid:
                QMessageBox.warning(self, "Error", f"Funcion invalida: {message}")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error de validacion: {str(e)}")
            return
        
        # Mostrar diálogo de espera
        progress = QProgressDialog("Calculando raíz por método de regla falsa...", "Cancelar", 0, 0, self)
        progress.setWindowTitle("Espere...")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(200)
        progress.show()
        QApplication.processEvents()
        
        try:
            a = float(self.a_input.text())
            b = float(self.b_input.text())
            tolerance = float(self.tolerance_input.text())
            max_iter = 10000
            
            # Ejecutar método
            success, result, iterations = ejecutar_metodo_regla_falsa(func_str, a, b, tolerance, max_iter)
            
            if not success:
                QMessageBox.critical(self, "Error", result)
                return
            
            # Mostrar resultados
            self.display_results(iterations, result)
            
            # Graficar con zoom en el intervalo y raíz marcada
            # Usar intervalo específico para mostrar detalle del método
            self.canvas.plot_function(func_str, interval=(a, b), show_roots=True)
            self.canvas.mark_root(result['raiz'])
            
            # Mensaje de éxito
            if result['convergio']:
                QMessageBox.information(self, "Resultado", 
                    f"Raíz encontrada: {result['raiz']:.10f}\n"
                    f"Iteraciones: {result['iteracion']}\n"
                    f"Error: {result['error']:.8f}")
            else:
                QMessageBox.warning(self, "Advertencia", 
                    f"Máximo de iteraciones alcanzado\n"
                    f"Raíz aproximada: {result['raiz']:.10f}")
            
            self.show_success_message(f"Raíz encontrada: {result['raiz']:.6f}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en el cálculo: {str(e)}")
        finally:
            progress.close()
    
    def display_results(self, iterations, result):
        """Muestra los resultados y pasos detallados"""
        # Guardar datos para la ventana emergente
        self.iterations_data = iterations
        
        # Habilitar botón de tabla
        self.show_table_btn.setEnabled(True)
        
        # Mostrar pasos detallados
        self.display_detailed_steps(iterations, result)
        
        # Actualizar resumen
        self.update_summary(result)
    
    def display_detailed_steps(self, iterations, result):
        """Muestra los pasos detallados del método"""
        func_str = self.function_input.text().strip()
        a_initial = float(self.a_input.text())
        b_initial = float(self.b_input.text())
        tolerance = float(self.tolerance_input.text())
        
        steps_text = f"""MÉTODO DE LA REGLA FALSA
{'='*50}

Función: f(x) = {func_str}
Intervalo inicial: [{a_initial}, {b_initial}]
Tolerancia: {tolerance}

FÓRMULA: xr = b - f(b) * (a - b) / (f(a) - f(b))

"""
        
        for i, data in enumerate(iterations):
            steps_text += f"""ITERACIÓN {data['iteracion']}:
{'-'*20}
a = {data['a']:.6f}
b = {data['b']:.6f}
f(a) = {data['fa']:.6e}
f(b) = {data['fb']:.6e}

Cálculo de xr:
xr = {data['b']:.6f} - ({data['fb']:.6e}) * ({data['a']:.6f} - {data['b']:.6f}) / ({data['fa']:.6e} - {data['fb']:.6e})
xr = {data['xr']:.6f}

f(xr) = {data['fxr']:.6e}
"""
            
            if i > 0:
                steps_text += f"Error relativo = {data['error_rel']:.6f}\n"
            
            # Determinar qué intervalo usar para la siguiente iteración
            if i < len(iterations) - 1:
                if data['fa'] * data['fxr'] < 0:
                    steps_text += f"\nf(a)*f(xr) < 0 → Nueva b = {data['xr']:.6f}\n"
                else:
                    steps_text += f"\nf(a)*f(xr) > 0 → Nueva a = {data['xr']:.6f}\n"
            
            steps_text += "\n"
        
        # Resultado final
        if result['convergio']:
            steps_text += f"""CONVERGENCIA ALCANZADA!
{'='*30}
Raíz encontrada: {result['raiz']:.10f}
Iteraciones: {result['iteracion']}
Error final: {result['error']:.8f}
"""
        else:
            steps_text += f"""MÁXIMO DE ITERACIONES ALCANZADO
{'='*35}
Raíz aproximada: {result['raiz']:.10f}
Iteraciones: {result['iteracion']}
Error final: {result['error']:.8f}
"""
        
        self.steps_text.setPlainText(steps_text)
    
    def update_summary(self, result):
        """Actualiza el resumen en el panel izquierdo"""
        if result['convergio']:
            summary = f"""✓ CONVERGENCIA EXITOSA

Raíz: {result['raiz']:.8f}
Iteraciones: {result['iteracion']}
Error: {result['error']:.6f}
Tolerancia: {self.tolerance_input.text()}"""
            self.summary_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 4px;
                    padding: 10px;
                    color: #2e7d32;
                }
            """)
        else:
            summary = f"""⚠ MÁXIMO DE ITERACIONES

Raíz aprox: {result['raiz']:.8f}
Iteraciones: {result['iteracion']}
Error: {result['error']:.6f}
Tolerancia: {self.tolerance_input.text()}"""
            self.summary_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3e0;
                    border: 1px solid #ff9800;
                    border-radius: 4px;
                    padding: 10px;
                    color: #e65100;
                }
            """)
        
        self.summary_label.setText(summary)
    
    def show_iterations_table(self):
        """Muestra la ventana emergente con la tabla de iteraciones"""
        if not self.iterations_data:
            return
        
        dialog = IterationsTableDialog(self)
        dialog.populate_table(self.iterations_data)
        dialog.exec_()
    
    def clear_results(self):
        """Limpia los resultados del cálculo anterior"""
        if self.iterations_data:  # Solo limpiar si hay datos
            self.iterations_data = []
            self.show_table_btn.setEnabled(False)
            self.steps_text.setPlainText("Los pasos detallados del método aparecerán aquí cuando ejecutes 'Encontrar Raíz'.")
            self.summary_label.setText("Haz clic en 'Encontrar Raíz' para ver resultados")
            self.summary_label.setStyleSheet("""
                QLabel {
                    background-color: #fefefe;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 10px;
                    color: #666;
                }
            """)
            # Limpiar gráfico
            self.canvas.ax.clear()
            self.canvas.ax.grid(True, alpha=0.3)
            self.canvas.ax.set_facecolor('#fafafa')
            self.canvas.draw()
    
    def new_calculation(self):
        """Inicia un nuevo cálculo"""
        self.function_input.setText("")
        self.a_input.setText("1")
        self.b_input.setText("2")
        self.tolerance_input.setText("0.0001")
        self.clear_results()
        self.canvas.ax.clear()
        self.canvas.ax.grid(True, alpha=0.3)
        self.canvas.ax.set_facecolor('#fafafa')
        self.canvas.draw()
        self.show_normal_message("Nuevo cálculo iniciado")
    
    def show_equation_preview(self, text, is_valid):
        """Muestra el preview de la ecuación con LaTeX"""
        self.equation_ax.clear()
        self.equation_ax.axis('off')
        
        if text and is_valid:
            try:
                # Convertir a LaTeX y renderizar
                latex_text = self.convert_to_latex(text)
                self.equation_ax.text(0.5, 0.5, f'$f(x) = {latex_text}$', 
                                     fontsize=12, ha='center', va='center',
                                     color='#1565C0',
                                     transform=self.equation_ax.transAxes)
            except Exception:
                # Si falla LaTeX, usar formato simple
                formatted_text = self.format_function_text(text)
                self.equation_ax.text(0.5, 0.5, f'f(x) = {formatted_text}', 
                                     fontsize=11, ha='center', va='center',
                                     color='#1565C0', weight='bold',
                                     transform=self.equation_ax.transAxes)
        elif text and not is_valid:
            self.equation_ax.text(0.5, 0.5, text, 
                                 fontsize=10, ha='center', va='center',
                                 color='red',
                                 transform=self.equation_ax.transAxes)
        
        try:
            self.equation_canvas.draw()
        except Exception:
            pass  # Ignorar errores de renderizado
    
    def format_function_text(self, func_str):
        """Formatea el texto de la función para notación matemática"""
        import re
        
        formatted = func_str
        
        # Convertir ** a ^ primero
        formatted = formatted.replace('**', '^')
        
        # IMPORTANTE: No procesar exp() aquí, se maneja en convert_to_latex
        
        # Constantes matemáticas (pero NO reemplazar 'e' dentro de funciones)
        formatted = formatted.replace('pi', 'π')
        # Solo reemplazar 'e' si no está dentro de funciones
        formatted = re.sub(r'\be\b(?!xp)', 'e', formatted)
        
        # Funciones logaritmos con subíndices
        def format_logb(match):
            arg = match.group(1)
            base = match.group(2)
            subscripts = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
                         '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}
            base_sub = ''.join(subscripts.get(c, c) for c in base)
            return f'log{base_sub}({arg})'
        
        formatted = re.sub(r'logb\(([^,]+),([^)]+)\)', format_logb, formatted)
        formatted = formatted.replace('log10(', 'log₁₀(')
        formatted = formatted.replace('log2(', 'log₂(')
        formatted = formatted.replace('ln(', 'ln(')
        
        # Raíces
        formatted = formatted.replace('sqrt(', '√(')
        formatted = formatted.replace('cbrt(', '³√(')
        
        # Función para convertir números a superíndices en root
        def to_superscript(match):
            x_part = match.group(1)
            n_part = match.group(2)
            superscript_map = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
            n_super = ''.join(superscript_map.get(c, c) for c in str(n_part))
            return f'{n_super}√({x_part})'
        
        formatted = re.sub(r'root\(([^,]+),([^)]+)\)', to_superscript, formatted)
        
        # Funciones trigonométricas
        formatted = formatted.replace('asin(', 'arcsin(')
        formatted = formatted.replace('acos(', 'arccos(')
        formatted = formatted.replace('atan(', 'arctan(')
        
        # Valor absoluto
        formatted = re.sub(r'abs\(([^)]+)\)', r'|\1|', formatted)
        
        # Potencias con superíndices
        superscripts = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
        }
        
        # Convertir potencias simples (números) a superíndices
        for num, sup in superscripts.items():
            formatted = formatted.replace(f'^{num}', sup)
        
        # Para potencias complejas, usar notación ^{...}
        formatted = re.sub(r'\^\(([^)]+)\)', r'^{\1}', formatted)
        
        # Multiplicación implícita y explícita
        formatted = re.sub(r'(\d)\s*\*\s*x', r'\1x', formatted)
        formatted = re.sub(r'(\d)\s*x', r'\1x', formatted)
        formatted = re.sub(r'\)\s*\(', r')(', formatted)
        formatted = re.sub(r'\)\s*x', r')x', formatted)
        formatted = re.sub(r'x\s*\(', r'x(', formatted)
        formatted = formatted.replace('*', '·')
        
        # Fracciones simples
        formatted = formatted.replace('1/x', '¹/ₓ')
        
        return formatted
    
    def convert_to_latex(self, func_str):
        """Convierte función a LaTeX de forma segura"""
        import re
        
        try:
            latex = func_str
            
            # Limpiar caracteres problemáticos
            latex = latex.replace('$', '')
            
            # Potencias - procesar ** primero
            latex = latex.replace('**', '^')
            
            # Proteger constantes temporalmente para procesarlas al final
            latex = latex.replace('pi', '___PI___')
            latex = re.sub(r'\be\b(?!xp)', '___E___', latex)
            
            # Función recursiva para procesar exp() con contenido anidado
            def process_exp(text):
                # Buscar exp() de adentro hacia afuera
                while r'\bexp\(' in text or 'exp(' in text:
                    # Encontrar exp( y su paréntesis de cierre correspondiente
                    match = re.search(r'\bexp\(', text)
                    if not match:
                        break
                    
                    start = match.end()
                    count = 1
                    i = start
                    
                    # Encontrar el paréntesis de cierre correspondiente
                    while i < len(text) and count > 0:
                        if text[i] == '(':
                            count += 1
                        elif text[i] == ')':
                            count -= 1
                        i += 1
                    
                    if count == 0:
                        # Extraer el contenido
                        content = text[start:i-1]
                        # Reemplazar exp(...) con e^{...}
                        text = text[:match.start()] + f'___E___^{{{content}}}' + text[i:]
                    else:
                        break
                
                return text
            
            latex = process_exp(latex)
            
            # Funciones trigonométricas e hiperbólicas ANTES de procesar multiplicación
            # Esto permite capturar 2cosh, 2sin, etc.
            latex = re.sub(r'asin\(', r'\\arcsin\\left(', latex)
            latex = re.sub(r'acos\(', r'\\arccos\\left(', latex)
            latex = re.sub(r'atan\(', r'\\arctan\\left(', latex)
            latex = re.sub(r'sinh\(', r'\\sinh\\left(', latex)
            latex = re.sub(r'cosh\(', r'\\cosh\\left(', latex)
            latex = re.sub(r'tanh\(', r'\\tanh\\left(', latex)
            latex = re.sub(r'sin\(', r'\\sin\\left(', latex)
            latex = re.sub(r'cos\(', r'\\cos\\left(', latex)
            latex = re.sub(r'tan\(', r'\\tan\\left(', latex)
            
            # Cerrar paréntesis de funciones
            latex = re.sub(r'\\left\(([^()]+)\)', r'\\left(\1\\right)', latex)
            
            # Raíces
            latex = re.sub(r'root\(([^,]+),([^)]+)\)', r'\\sqrt[\2]{\1}', latex)
            latex = re.sub(r'sqrt\(([^)]+)\)', r'\\sqrt{\1}', latex)
            latex = re.sub(r'cbrt\(([^)]+)\)', r'\\sqrt[3]{\1}', latex)
            
            # Logaritmos
            latex = re.sub(r'logb\(([^,]+),([^)]+)\)', r'\\log_{\2}\\left(\1\\right)', latex)
            latex = re.sub(r'log10\(([^)]+)\)', r'\\log_{10}\\left(\1\\right)', latex)
            latex = re.sub(r'log2\(([^)]+)\)', r'\\log_{2}\\left(\1\\right)', latex)
            latex = re.sub(r'\bln\(([^)]+)\)', r'\\ln\\left(\1\\right)', latex)
            
            # Valor absoluto
            latex = re.sub(r'abs\(([^)]+)\)', r'\\left|\1\\right|', latex)
            
            # Potencias con paréntesis
            latex = re.sub(r'\^\(([^)]+)\)', r'^{\1}', latex)
            
            # Potencias simples
            latex = re.sub(r'\^([a-zA-Z0-9]+)', r'^{\1}', latex)
            
            # Fracciones (procesar de más específico a más general)
            latex = re.sub(r'\(([^)]+)\)/\(([^)]+)\)', r'\\frac{\1}{\2}', latex)
            latex = re.sub(r'\(([0-9]+)/([^)]+)\)', r'\\frac{\1}{\2}', latex)  # (1/x) -> frac
            latex = re.sub(r'([0-9]+)/\(([^)]+)\)', r'\\frac{\1}{\2}', latex)
            latex = re.sub(r'\(([^)]+)\)/([0-9]+)', r'\\frac{\1}{\2}', latex)
            latex = re.sub(r'([0-9]+)/x\b', r'\\frac{\1}{x}', latex)  # 1/x -> frac
            
            # Multiplicación (mantener * con constantes protegidas)
            latex = re.sub(r'(\d)\s*\*\s*x', r'\1x', latex)
            latex = re.sub(r'(\d)\s*x', r'\1x', latex)
            
            # Restaurar constantes ANTES de procesar *
            latex = latex.replace('___PI___', r'\pi')
            latex = latex.replace('___E___', 'e')
            
            # Agregar espacios entre constantes y variables
            latex = re.sub(r'(\\pi)([a-z])', r'\1 \2', latex)  # \pix -> \pi x
            latex = re.sub(r'\b(e)([a-z])', r'\1 \2', latex)  # ex -> e x
            
            # Procesar * después de restaurar constantes con espacios
            latex = latex.replace('*', r' \\cdot ')
            
            return latex
            
        except Exception as e:
            # Si hay error, devolver texto original
            return func_str.replace('$', '')
    
    def zoom_in(self):
        """Acerca el zoom del gráfico y redibuja con más puntos"""
        xlim = self.canvas.ax.get_xlim()
        ylim = self.canvas.ax.get_ylim()
        
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        x_range = (xlim[1] - xlim[0]) * 0.7
        y_range = (ylim[1] - ylim[0]) * 0.7
        
        # Redibujar función con nuevo rango
        func_str = self.function_input.text().strip()
        if func_str and self.canvas.current_func:
            new_interval = (x_center - x_range/2, x_center + x_range/2)
            self.canvas.plot_function(func_str, interval=new_interval, show_roots=False)
        else:
            self.canvas.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.canvas.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            self.canvas.draw()
    
    def zoom_out(self):
        """Aleja el zoom del gráfico y redibuja con más puntos"""
        xlim = self.canvas.ax.get_xlim()
        ylim = self.canvas.ax.get_ylim()
        
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        x_range = (xlim[1] - xlim[0]) * 1.4
        y_range = (ylim[1] - ylim[0]) * 1.4
        
        # Redibujar función con nuevo rango
        func_str = self.function_input.text().strip()
        if func_str and self.canvas.current_func:
            new_interval = (x_center - x_range/2, x_center + x_range/2)
            self.canvas.plot_function(func_str, interval=new_interval, show_roots=False)
        else:
            self.canvas.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.canvas.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            self.canvas.draw()
    
    def reset_zoom(self):
        """Restablece el zoom del gráfico"""
        func_str = self.function_input.text().strip()
        if func_str:
            self.plot_function()
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        QMessageBox.about(self, "Acerca de", 
            "Método de la Regla Falsa v2.0\n\n"
            "Interfaz gráfica moderna\n"
            "Desarrollado con PyQt5\n\n"
            "Sistema de Análisis Numérico")

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    
    # Configurar tema claro
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = InterfazReglaFalsaPyQt()
    window.showMaximized()  # Mostrar maximizada desde el inicio
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()