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
from metodo_secante import ejecutar_metodo_secante

class IterationsTableDialog(QDialog):
    """Ventana emergente para mostrar la tabla de iteraciones"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tabla de Iteraciones - Método de la Secante")
        self.setModal(True)
        self.resize(800, 400)
        
        layout = QVBoxLayout(self)
        
        # Tabla de iteraciones
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Iter", "x0", "x1", "f(x0)", "f(x1)", "x2", "Error"])
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
            self.table.setItem(i, 1, QTableWidgetItem(f"{data['x0']:.6f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{data['x1']:.6f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{data['fx0']:.4e}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{data['fx1']:.4e}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{data['x2']:.6f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{data['error_rel']:.6f}"))
        
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
        
        # Variables para pan (arrastrar) y zoom por selección
        self.press = None
        self.current_func = None
        self.root_positions = []  # Almacenar posiciones de raíces
        self.tooltip_annotation = None
        self.alt_pressed = False  # Estado de la tecla ALT
        self.ctrl_pressed = False  # Estado de la tecla CTRL para zoom por selección
        self.zoom_selector = None  # Selector de área para zoom
        
        # Conectar eventos de mouse
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('motion_notify_event', self.on_motion)
        self.mpl_connect('scroll_event', self.on_scroll)
        
        # Importar RectangleSelector para zoom por área
        from matplotlib.widgets import RectangleSelector
        self.setup_zoom_selector()
    
    def on_press(self, event):
        """Inicia el arrastre o zoom por selección"""
        if event.inaxes != self.ax:
            return
        
        # Si CTRL está presionado, activar zoom por selección
        if self.ctrl_pressed:
            return  # Dejar que RectangleSelector maneje el evento
        
        # Si no, usar pan normal
        self.press = (event.xdata, event.ydata)
        # Dar foco al canvas para recibir eventos de teclado
        self.setFocus()
    
    def on_motion(self, event):
        """Maneja el arrastre del gráfico, zoom por selección y tooltips"""
        if event.inaxes != self.ax:
            return
        
        # Si CTRL está presionado, dejar que RectangleSelector maneje el evento
        if self.ctrl_pressed:
            return
        
        # Si está arrastrando (pan)
        if self.press is not None:
            dx = event.xdata - self.press[0]
            dy = event.ydata - self.press[1]
            
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            new_xlim = (xlim[0] - dx, xlim[1] - dx)
            new_ylim = (ylim[0] - dy, ylim[1] - dy)
            
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            
            # Extender función si es necesario durante el pan
            self.extend_function_if_needed(new_xlim)
            
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
        # Limpiar cualquier rectángulo de zoom residual
        if self.zoom_selector and not self.ctrl_pressed:
            self.zoom_selector.set_visible(False)
            self.zoom_selector.update()
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
        
        new_xlim = (x_center - x_range/2, x_center + x_range/2)
        
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
        
        # Actualizar ticks adaptativos después del zoom
        self.setup_adaptive_ticks()
        
        # Extender función si es necesario durante el zoom
        self.extend_function_if_needed(new_xlim)
        
        self.draw_idle()
    
    def setup_zoom_selector(self):
        """Configura el selector de área para zoom"""
        from matplotlib.widgets import RectangleSelector
        
        self.zoom_selector = RectangleSelector(
            self.ax, self.on_zoom_select,
            useblit=True,
            button=[1],  # Solo botón izquierdo
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=False
        )
        self.zoom_selector.set_active(False)  # Desactivado por defecto
    
    def setup_adaptive_ticks(self):
        """Configura ticks adaptativos: ~10 en X, ~20 en Y"""
        import matplotlib.ticker as ticker
        import math
        
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        
        def get_nice_interval(range_val, target_ticks):
            """Calcula un intervalo 'bonito' para el número objetivo de ticks"""
            if range_val <= 0 or range_val < 1e-10:
                return 1
            
            # Calcular intervalo crudo
            raw_interval = range_val / target_ticks
            
            if raw_interval <= 0:
                return 1
            
            # Encontrar la potencia de 10 más cercana
            magnitude = 10 ** math.floor(math.log10(raw_interval))
            
            # Normalizar al rango [1, 10)
            normalized = raw_interval / magnitude
            
            # Elegir el valor "bonito" más cercano: 1, 2, 5, o 10
            if normalized <= 1.5:
                nice = 1
            elif normalized <= 3:
                nice = 2
            elif normalized <= 7:
                nice = 5
            else:
                nice = 10
            
            return nice * magnitude
        
        # Calcular intervalos: 10 ticks en X, 6 ticks en Y
        # Más ticks en X para evitar achatamiento, menos en Y para no saturar
        x_interval = get_nice_interval(x_range, 10)
        y_interval = get_nice_interval(y_range, 6)
        
        # Validar que los intervalos sean razonables
        if x_interval > 0 and not math.isnan(x_interval) and not math.isinf(x_interval):
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(x_interval))
        else:
            self.ax.xaxis.set_major_locator(ticker.AutoLocator())
        
        if y_interval > 0 and not math.isnan(y_interval) and not math.isinf(y_interval):
            self.ax.yaxis.set_major_locator(ticker.MultipleLocator(y_interval))
        else:
            self.ax.yaxis.set_major_locator(ticker.AutoLocator())
        
        # Asegurar que los ticks sean visibles
        self.ax.tick_params(axis='both', which='major', labelsize=10, length=6, width=1)
        
        # Forzar que se muestren los labels del eje Y
        self.ax.yaxis.set_tick_params(labelleft=True)
        for label in self.ax.yaxis.get_ticklabels():
            label.set_visible(True)
    
    def extend_function_if_needed(self, new_xlim):
        """Extiende la función si el pan se sale del rango calculado"""
        if not hasattr(self, 'current_func') or not self.current_func:
            return
        
        # Obtener rango actual de la función
        function_line = None
        for line in self.ax.lines:
            if line.get_label().startswith('f(x) ='):
                function_line = line
                break
        
        if function_line is None:
            return
        
        current_x = function_line.get_xdata()
        if len(current_x) == 0:
            return
        
        current_x_min, current_x_max = np.min(current_x), np.max(current_x)
        new_x_min, new_x_max = new_xlim
        
        # Verificar si necesita extensión
        extend_left = new_x_min < current_x_min
        extend_right = new_x_max > current_x_max
        
        if extend_left or extend_right:
            # Calcular nuevo rango extendido
            x_range = current_x_max - current_x_min
            extension = x_range * 0.5  # Extender 50% en cada dirección
            
            if extend_left:
                new_calc_min = current_x_min - extension
            else:
                new_calc_min = current_x_min
            
            if extend_right:
                new_calc_max = current_x_max + extension
            else:
                new_calc_max = current_x_max
            
            # Recalcular función en el rango extendido
            try:
                num_points = len(current_x)
                x_new = np.linspace(new_calc_min, new_calc_max, num_points)
                y_new = []
                
                for xi in x_new:
                    try:
                        yi = evaluar_funcion(self.current_func, xi)
                        if abs(yi) < 1e8:
                            y_new.append(yi)
                        else:
                            y_new.append(np.nan)
                    except:
                        y_new.append(np.nan)
                
                # Actualizar la línea de la función
                function_line.set_data(x_new, y_new)
                
                # Actualizar raíces para tooltips
                self.detect_roots_for_tooltips(x_new, np.array(y_new))
                
            except Exception:
                pass  # Ignorar errores de extensión
    
    def on_zoom_select(self, eclick, erelease):
        """Maneja la selección de área para zoom"""
        if not self.ctrl_pressed:
            return
        
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        if x1 is None or x2 is None or y1 is None or y2 is None:
            return
        
        # Asegurar que x1 < x2 y y1 < y2
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        
        # Evitar límites idénticos que causan warnings
        if abs(x_max - x_min) < 1e-10:
            x_center = (x_max + x_min) / 2
            x_min, x_max = x_center - 0.1, x_center + 0.1
        
        if abs(y_max - y_min) < 1e-10:
            y_center = (y_max + y_min) / 2
            y_min, y_max = y_center - 0.1, y_center + 0.1
        
        # Aplicar zoom al área seleccionada
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        
        # Actualizar ticks adaptativos después del zoom
        self.setup_adaptive_ticks()
        
        # Limpiar el rectángulo de selección
        if self.zoom_selector:
            self.zoom_selector.set_active(False)
            self.zoom_selector.set_active(True)
        
        self.draw_idle()
    
    def keyPressEvent(self, event):
        """Maneja eventos de tecla presionada"""
        if event.key() == Qt.Key_Alt:
            self.alt_pressed = True
        elif event.key() == Qt.Key_Control:
            self.ctrl_pressed = True
            if self.zoom_selector:
                self.zoom_selector.set_active(True)
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Maneja eventos de tecla liberada"""
        if event.key() == Qt.Key_Alt:
            self.alt_pressed = False
            # Ocultar tooltip al soltar ALT
            if self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
                self.draw_idle()
        elif event.key() == Qt.Key_Control:
            self.ctrl_pressed = False
            if self.zoom_selector:
                self.zoom_selector.set_active(False)
                # Limpiar el rectángulo de selección
                self.zoom_selector.update()
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
            # Guardar función original para detección
            self.original_func_str = func_str
            func_str_proc = preprocesar_funcion(func_str)
            
            if interval:
                a, b = interval
                # Asegurar que el intervalo sea válido
                if a >= b:
                    # Intervalo inválido, usar rango por defecto
                    x_min, x_max = -10, 10
                else:
                    x_min, x_max = a, b
            else:
                # Encontrar rango óptimo automáticamente
                x_min, x_max = self.find_optimal_range(func_str_proc)
                
            # Usar número alto de puntos para curvas suaves
            num_points = 3000
            x = np.linspace(x_min, x_max, num_points)
            
            # Guardar función actual para redibujado
            self.current_func = func_str_proc
            y = []
            
            # Detectar si es función con crecimiento extremo (como x^x^e)
            has_extreme_growth = any(pattern in func_str_proc for pattern in ['^x', '**x', 'x^x', 'x**x'])
            
            for xi in x:
                try:
                    yi = evaluar_funcion(func_str_proc, xi)
                    # Solo filtrar valores infinitos o NaN, no valores grandes
                    if np.isnan(yi) or np.isinf(yi):
                        y.append(np.nan)
                    elif has_extreme_growth and abs(yi) > 1e6:
                        y.append(np.nan)
                    else:
                        y.append(yi)
                except:
                    y.append(np.nan)
            
            y = np.array(y)
            
            # Configurar límites Y inteligentes
            valid_y = y[~np.isnan(y)]
            if len(valid_y) > 0:
                # Calcular rango completo de Y para el intervalo X actual
                y_min_full = np.min(valid_y)
                y_max_full = np.max(valid_y)
                y_range_full = y_max_full - y_min_full
                
                # Si el rango es muy pequeño, expandir
                if y_range_full < 0.1:
                    y_center = (y_max_full + y_min_full) / 2
                    y_min_full = y_center - 1
                    y_max_full = y_center + 1
                    y_range_full = 2
                
                # Agregar margen para que la función se vea completa
                margin_y = y_range_full * 0.15  # 15% de margen
                y_min_adj = y_min_full - margin_y
                y_max_adj = y_max_full + margin_y
                
                # Solo aplicar ajustes si NO hay intervalo específico (botón Graficar)
                if interval is None:
                    # Asegurar que se muestren los 4 cuadrantes si es posible
                    if abs(y_min_adj) < 2 and abs(y_max_adj) < 2:
                        y_min_adj = min(y_min_adj, -2)
                        y_max_adj = max(y_max_adj, 2)
                    
                    # Limitar valores Y muy grandes para evitar escalas extremas
                    # SOLO cuando se grafica sin intervalo específico
                    if y_max_adj > 50:
                        y_max_adj = 50
                    if y_min_adj < -50:
                        y_min_adj = -50
                
                # Aplicar límites Y
                self.ax.set_ylim(y_min_adj, y_max_adj)
            
            # Graficar función
            self.ax.plot(x, y, 'b-', linewidth=1.5, label=f'f(x) = {func_str}')
            
            # Ejes de referencia (más gruesos que el grid)
            self.ax.axhline(y=0, color='#2E4057', linestyle='-', alpha=0.9, linewidth=1.8, zorder=2)
            self.ax.axvline(x=0, color='#2E4057', linestyle='-', alpha=0.9, linewidth=1.8, zorder=2)
            
            # Detectar raíces para tooltips (siempre)
            self.detect_roots_for_tooltips(x, y)
            
            # Solo marcar raíces si se solicita explícitamente
            if show_roots:
                self.mark_zero_crossings(x, y, interval)
            
            
            # Asegurar que siempre se vean los ejes del sistema cartesiano en X
            # SOLO si no hay intervalo específico (botón Graficar)
            if interval is None:
                current_xlim = self.ax.get_xlim()
                if current_xlim[0] > -1:
                    self.ax.set_xlim(left=-2)
                if current_xlim[1] < 1:
                    self.ax.set_xlim(right=2)
            
            self.ax.set_xlabel('x', fontsize=11)
            self.ax.set_ylabel('f(x)', fontsize=11)
            self.ax.legend(fontsize=10)
            self.ax.set_title(f'Gráfico de f(x) = {func_str}', fontsize=12, pad=15)
            
            # Configurar ejes y grid adaptativos
            self.setup_adaptive_ticks()
            
            # Ajustar aspecto para evitar achatamiento
            # Mantener aspecto automático (no forzar proporción 1:1)
            self.ax.set_aspect('auto')
            
            # Forzar redibujado del canvas
            self.fig.tight_layout()
            self.draw()
            
            # Grid principal (más sutil que los ejes)
            self.ax.grid(True, which='major', alpha=0.4, linewidth=0.5, color='gray', zorder=1)
            
            # Ajustar límites para funciones cúbicas SOLO si no hay intervalo específico
            if interval is None and any(char in func_str for char in ['^3', '**3']):
                # Limitar rango Y a -20, 20 para funciones cúbicas en vista general
                ylim = self.ax.get_ylim()
                
                # Aplicar límites de -20 a 20
                y_min = max(ylim[0], -20)
                y_max = min(ylim[1], 20)
                
                self.ax.set_ylim(y_min, y_max)
                
                # Mantener aspecto automático para preservar forma de la línea
                self.ax.set_aspect('auto')
                
                # Reconfigurar ticks después de cambiar límites
                self.setup_adaptive_ticks()
            
        except Exception as e:
            self.ax.text(0.5, 0.5, f'Error al graficar: {str(e)}', transform=self.ax.transAxes, 
                        ha='center', va='center', fontsize=12, color='red')
            self.draw_idle()
    
    def find_optimal_range(self, func_str_proc):
        """Encuentra el rango óptimo para mostrar la función"""
        from matematicas import preprocesar_funcion
        
        original_func = preprocesar_funcion(func_str_proc) if hasattr(self, 'original_func_str') else func_str_proc
        
        has_extreme_growth = any(pattern in str(original_func) for pattern in ['^x', '**x', 'x^x', 'x**x'])
        
        if has_extreme_growth:
            test_ranges = [(0.1, 2), (0.5, 1.5), (1, 2.5), (0.1, 1.5)]
        elif any(log_func in str(original_func) for log_func in ['ln(', 'log10(', 'log2(', 'logb(']):
            test_ranges = [(0.1, 10), (0.01, 50), (0.1, 100), (1, 200), (0.5, 30)]
        elif 'sqrt(' in str(original_func) or 'cbrt(' in str(original_func):
            test_ranges = [(0, 10), (0, 15), (0, 20), (-2, 10)]
        elif any(pattern in str(original_func) for pattern in ['^3', '**3', '^4', '**4']):
            test_ranges = [(-10, 10), (-8, 8), (-12, 12), (-6, 6)]
        else:
            test_ranges = [(-10, 10), (-15, 15), (-8, 8), (-20, 20)]
        
        best_range = (-5, 5)
        max_score = 0
        y_limit = 1e6 if has_extreme_growth else 1e8
        
        for x_min, x_max in test_ranges:
            x_test = np.linspace(x_min, x_max, 200)
            y_test = []
            crossings = 0
            variation = 0
            
            for xi in x_test:
                try:
                    yi = evaluar_funcion(func_str_proc, xi)
                    if abs(yi) < y_limit:
                        y_test.append(yi)
                    else:
                        y_test.append(np.nan)
                except:
                    y_test.append(np.nan)
            
            valid_y = [y for y in y_test if not np.isnan(y)]
            if len(valid_y) > 10:
                for i in range(1, len(y_test)):
                    if not (np.isnan(y_test[i-1]) or np.isnan(y_test[i])):
                        if y_test[i-1] * y_test[i] < 0:
                            crossings += 1
                
                if len(valid_y) > 1:
                    variation = np.std(valid_y)
                
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
        button_width = 40
        button_height = 26
        buttons_per_row = 6
        num_rows = 5
        spacing = 2
        margins = 10
        
        # Tamaño fijo del contenedor
        fixed_width = (button_width * buttons_per_row) + (spacing * (buttons_per_row - 1)) + margins
        fixed_height = (button_height * num_rows) + (spacing * (num_rows - 1)) + margins
        
        container.setFixedSize(fixed_width, fixed_height)
        
        # Definir botones de funciones (completos como en Tkinter)
        functions = [
            [('sin', 'sin(x)'), ('cos', 'cos(x)'), ('tan', 'tan(x)'), ('csc', 'csc(x)'), ('sec', 'sec(x)'), ('cot', 'cot(x)')],
            [('asin', 'asin(x)'), ('acos', 'acos(x)'), ('atan', 'atan(x)'), ('sinh', 'sinh(x)'), ('cosh', 'cosh(x)'), ('tanh', 'tanh(x)')],
            [('exp', 'exp(x)'), ('ln', 'ln(x)'), ('log₁₀', 'log10(x)'), ('log₂', 'log2(x)'), ('√', 'sqrt(x)'), ('³√', 'cbrt(x)')],
            [('ⁿ√', 'root(x,3)'), ('x²', 'x^2'), ('|x|', 'abs(x)'), ('π', 'pi'), ('e', 'e'), ('x³', 'x^3')],
            [('xⁿ', 'x^'), ('logₓ', 'logb(x,10)'), ('1/x', '1/x'), ('', ''), ('', ''), ('', '')]
        ]
        
        # Tooltips para botones
        tooltips = {
            'sin(x)': 'Digitar: sin(x)', 'cos(x)': 'Digitar: cos(x)', 'tan(x)': 'Digitar: tan(x)',
            'csc(x)': 'Digitar: csc(x) - Cosecante', 'sec(x)': 'Digitar: sec(x) - Secante', 'cot(x)': 'Digitar: cot(x) - Cotangente',
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
            if text:  # Solo crear botón si hay texto
                btn = QPushButton(text)
                btn.setFixedSize(40, 26)  # Tamaño fijo para todos los botones
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
            else:
                # Añadir espaciador invisible del mismo tamaño
                spacer = QWidget()
                spacer.setFixedSize(40, 26)
                current_row.addWidget(spacer)
            
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
        self.setWindowTitle("Método de la Secante")
        
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
        
        # Panel izquierdo (controles) - 35% del ancho
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 4)  # stretch factor 4
        
        # Panel central (pasos detallados) - 35% del ancho
        center_panel = self.create_steps_panel()
        main_layout.addWidget(center_panel, 4)  # stretch factor 4
        
        # Panel derecho (gráfico) - 30% del ancho
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)  # stretch factor 3
        
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
        new_action.triggered.connect(self.show_examples_dialog)
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

        # Menú Ejemplos
        ejemplos_menu = menubar.addMenu('Ejemplos')

        ejemplo1 = QAction('Ejemplo 1: x^3 - x - 2 (x0=1, x1=2)', self)
        ejemplo1.triggered.connect(lambda: self.load_example('x^3 - x - 2', '1.0', '2.0', '0.0001'))
        ejemplos_menu.addAction(ejemplo1)

        ejemplo2 = QAction('Ejemplo 2: cos(x) - x (x0=0, x1=1)', self)
        ejemplo2.triggered.connect(lambda: self.load_example('cos(x) - x', '0.0', '1.0', '0.0001'))
        ejemplos_menu.addAction(ejemplo2)

        ejemplo3 = QAction('Ejemplo 3: x^2 - 2 (x0=1, x1=2)', self)
        ejemplo3.triggered.connect(lambda: self.load_example('x^2 - 2', '1.0', '2.0', '0.0001'))
        ejemplos_menu.addAction(ejemplo3)
    
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
        self.function_input.setFont(QFont("Consolas", 16))
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
        
        # Botones de funciones con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setMinimumHeight(160)
        scroll_area.setMaximumHeight(210)
        
        self.function_buttons = FunctionButtonsWidget()
        scroll_area.setWidget(self.function_buttons)
        func_layout.addWidget(scroll_area)
        
        layout.addWidget(func_group)
        
        # Grupo de parámetros
        params_group = QGroupBox("Parámetros del Método")
        params_layout = QFormLayout(params_group)
        
        # Punto inicial x0
        self.x0_input = QLineEdit("1.0")
        self.x0_input.setFixedWidth(80)
        self.x0_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
        
        # Punto inicial x1
        self.x1_input = QLineEdit("2.0")
        self.x1_input.setFixedWidth(80)
        self.x1_input.setStyleSheet(self.x0_input.styleSheet())
        
        params_layout.addRow("Punto inicial x0:", self.x0_input)
        params_layout.addRow("Punto inicial x1:", self.x1_input)
        
        # Tolerancia
        self.tolerance_input = QLineEdit("0.0001")
        self.tolerance_input.setStyleSheet(self.x0_input.styleSheet())
        params_layout.addRow("Error máximo:", self.tolerance_input)
        
        layout.addWidget(params_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.plot_btn = QPushButton("📊 Graficar")
        self.solve_btn = QPushButton("🎯 Encontrar Raíz (Secante)")
        
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
        title_label = QLabel("Método de la Secante - Paso a Paso")
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
        info_label = QLabel("Haz clic en 'Graficar' para visualizar la función\n"
                           "Controles: Arrastrar=Pan | Rueda=Zoom | Ctrl+Arrastrar=Zoom por área")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        layout.addWidget(info_label)
        
        return panel
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.function_input.textChanged.connect(self.validate_function)
        self.function_buttons.function_inserted.connect(self.insert_function)
        self.plot_btn.clicked.connect(self.plot_function)
        self.solve_btn.clicked.connect(self.solve_equation)
        
        # Validación en tiempo real
        for input_field in [self.x0_input, self.x1_input, self.tolerance_input]:
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
        """Valida las entradas numéricas (tolerante durante edición)"""
        x0_text = self.x0_input.text().strip()
        x1_text = self.x1_input.text().strip()
        tol_text = self.tolerance_input.text().strip()
        
        # Permitir valores parciales durante la edición
        if not x0_text or not x1_text or not tol_text:
            return False
        
        # Permitir signos negativos y puntos decimales durante la edición
        if x0_text in ['-', '.', '-.'] or x1_text in ['-', '.', '-.'] or tol_text in ['.']:
            return False
        
        try:
            x0 = float(x0_text)
            x1 = float(x1_text)
            tol = float(tol_text)
            
            if tol <= 0:
                self.show_error_message("la tolerancia debe ser positiva")
                return False
            
            if x0 == x1:
                self.show_error_message("x0 y x1 deben ser diferentes")
                return False
            
            # Si todo es válido, mostrar mensaje de éxito
            self.show_success_message("Parámetros válidos")
            return True
        except ValueError:
            # No mostrar error durante la edición
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
            # Graficar con vista general amplia (sin mostrar raíces)
            # Usar None para que encuentre el rango óptimo automáticamente
            self.canvas.plot_function(func_str, interval=None, show_roots=False)
            self.show_success_message("Función graficada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al graficar: {str(e)}")
        finally:
            progress.close()
    
    def solve_equation(self):
        """Resuelve la ecuación usando el método de Newton-Raphson"""
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
        progress = QProgressDialog("Calculando raíz por método de la secante...", "Cancelar", 0, 0, self)
        progress.setWindowTitle("Espere...")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(200)
        progress.show()
        QApplication.processEvents()
        
        try:
            x0 = float(self.x0_input.text())
            x1 = float(self.x1_input.text())
            tolerance = float(self.tolerance_input.text())
            max_iter = 10000
            
            # Ejecutar método
            success, result, iterations = ejecutar_metodo_secante(func_str, x0, x1, tolerance, max_iter)
            
            if not success:
                QMessageBox.critical(self, "Error", result)
                return
            
            # Mostrar resultados
            self.display_results(iterations, result)
            
            # Graficar con zoom alrededor de la raíz
            raiz = result['raiz']
            
            # Calcular intervalo X alrededor de la raíz (inicialmente pequeño)
            if abs(raiz) > 50:
                # Raíz lejana: usar rango pequeño
                margen_x = 3
            else:
                # Raíz cercana: usar margen muy pequeño
                margen_x = 2
            
            # Ajustar margen X iterativamente para mantener rango Y razonable
            import numpy as np
            from matematicas import preprocesar_funcion, evaluar_funcion
            func_proc = preprocesar_funcion(func_str)
            
            # Intentar diferentes márgenes X hasta encontrar uno con rango Y razonable
            target_y_range = 20  # Objetivo: rango Y de ~20 unidades
            margenes_prueba = [0.1, 0.2, 0.5, 1, 1.5, 2, 3, 5]
            
            mejor_margen = margen_x
            mejor_y_range = float('inf')
            
            for margen_prueba in margenes_prueba:
                x_test = np.linspace(raiz - margen_prueba, raiz + margen_prueba, 50)
                y_test = []
                for xi in x_test:
                    try:
                        yi = evaluar_funcion(func_proc, xi)
                        # No filtrar valores, solo verificar que sean finitos
                        if not np.isnan(yi) and not np.isinf(yi):
                            y_test.append(yi)
                    except:
                        pass
                
                if len(y_test) > 0:
                    y_range = max(y_test) - min(y_test)
                    # Buscar el margen que dé un rango Y más cercano a 20
                    if abs(y_range - target_y_range) < abs(mejor_y_range - target_y_range):
                        mejor_margen = margen_prueba
                        mejor_y_range = y_range
                    
                    # Si encontramos un rango Y razonable, usar ese
                    if 15 <= y_range <= 30:
                        margen_x = margen_prueba
                        break
            else:
                # Si no encontramos uno perfecto, usar el mejor
                margen_x = mejor_margen
            
            intervalo = (raiz - margen_x, raiz + margen_x)
            self.canvas.plot_function(func_str, interval=intervalo, show_roots=True)
            self.canvas.mark_root(result['raiz'])
            
            # Mensaje de éxito
            if result['convergio']:
                mensaje = f"Raíz encontrada: {result['raiz']:.10f}\n" \
                         f"Iteraciones: {result['iteracion']}\n" \
                         f"Error: {result['error']:.8f}"
                
                # Advertir si la raíz está muy lejos
                if abs(result['raiz']) > 100:
                    mensaje += f"\n\n⚠ ADVERTENCIA: La raíz encontrada está muy alejada del origen.\n" \
                              f"Considera usar puntos iniciales más cercanos a la raíz deseada."
                
                QMessageBox.information(self, "Resultado", mensaje)
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
        x0_initial = float(self.x0_input.text())
        x1_initial = float(self.x1_input.text())
        tolerance = float(self.tolerance_input.text())
        
        steps_text = f"""MÉTODO DE LA SECANTE
{'='*50}

Función: f(x) = {func_str}
Puntos iniciales: x0 = {x0_initial}, x1 = {x1_initial}
Tolerancia: {tolerance}

FÓRMULA: x2 = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))

"""
        
        for i, data in enumerate(iterations):
            steps_text += f"""ITERACIÓN {data['iteracion']}:
{'-'*20}
x0 = {data['x0']:.6f}
x1 = {data['x1']:.6f}
f(x0) = {data['fx0']:.6e}
f(x1) = {data['fx1']:.6e}

Cálculo de x2:
x2 = {data['x1']:.6f} - ({data['fx1']:.6e}) * ({data['x1']:.6f} - {data['x0']:.6f}) / ({data['fx1']:.6e} - {data['fx0']:.6e})
x2 = {data['x2']:.6f}
"""
            
            steps_text += f"Error relativo = {data['error_rel']:.6f}\n"
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
        self.x0_input.setText("1.0")
        self.x1_input.setText("2.0")
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
                # Usar formato simple que es más robusto
                formatted_text = self.format_function_text(text)
                self.equation_ax.text(0.5, 0.5, f'f(x) = {formatted_text}', 
                                     fontsize=11, ha='center', va='center',
                                     color='#1565C0', weight='bold',
                                     transform=self.equation_ax.transAxes)
            except Exception as e:
                # Si falla, mostrar el texto original
                self.equation_ax.text(0.5, 0.5, f'f(x) = {text}', 
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
            
            # Proteger constantes temporalmente
            latex = latex.replace('pi', '___PI___')
            latex = re.sub(r'\be\b(?!xp)', '___E___', latex)
            
            # Procesar exp()
            def process_exp(text):
                while r'\bexp\(' in text or 'exp(' in text:
                    match = re.search(r'\bexp\(', text)
                    if not match:
                        break
                    start = match.end()
                    count = 1
                    i = start
                    while i < len(text) and count > 0:
                        if text[i] == '(':
                            count += 1
                        elif text[i] == ')':
                            count -= 1
                        i += 1
                    if count == 0:
                        content = text[start:i-1]
                        text = text[:match.start()] + f'___E___^{{{content}}}' + text[i:]
                    else:
                        break
                return text
            
            latex = process_exp(latex)
            
            # Funciones trigonométricas e hiperbólicas
            latex = re.sub(r'asin\(', r'\\arcsin\\left(', latex)
            latex = re.sub(r'acos\(', r'\\arccos\\left(', latex)
            latex = re.sub(r'atan\(', r'\\arctan\\left(', latex)
            latex = re.sub(r'sinh\(', r'\\sinh\\left(', latex)
            latex = re.sub(r'cosh\(', r'\\cosh\\left(', latex)
            latex = re.sub(r'tanh\(', r'\\tanh\\left(', latex)
            latex = re.sub(r'sin\(', r'\\sin\\left(', latex)
            latex = re.sub(r'cos\(', r'\\cos\\left(', latex)
            latex = re.sub(r'tan\(', r'\\tan\\left(', latex)
            
            # Cerrar paréntesis de funciones - procesar cada función por separado
            for func in ['sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan', 'sinh', 'cosh', 'tanh', 'ln', 'log', 'sqrt']:
                pattern = func + r'\\left\(([^)]+)\)'
                latex = re.sub(pattern, func + r'\\left(\1\\right)', latex)
            
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
            
            # Fracciones
            latex = re.sub(r'\(([^)]+)\)/\(([^)]+)\)', r'\\frac{\1}{\2}', latex)
            latex = re.sub(r'\(([0-9]+)/([^)]+)\)', r'\\frac{\1}{\2}', latex)
            latex = re.sub(r'([0-9]+)/\(([^)]+)\)', r'\\frac{\1}{\2}', latex)
            latex = re.sub(r'\(([^)]+)\)/([0-9]+)', r'\\frac{\1}{\2}', latex)
            latex = re.sub(r'([0-9]+)/x\b', r'\\frac{\1}{x}', latex)
            
            # Multiplicación
            latex = re.sub(r'(\d)\s*\*\s*x', r'\1x', latex)
            latex = re.sub(r'(\d)\s*x', r'\1x', latex)
            
            # Restaurar constantes
            latex = latex.replace('___PI___', r'\pi')
            latex = latex.replace('___E___', 'e')
            
            # Espacios entre constantes y variables
            latex = re.sub(r'(\\pi)([a-z])', r'\1 \2', latex)
            latex = re.sub(r'\b(e)([a-z])', r'\1 \2', latex)
            
            # Procesar * después de restaurar constantes
            latex = latex.replace('*', r' \\cdot ')
            
            return latex
            
        except Exception as e:
            # Si hay error, devolver texto original
            return func_str.replace('$', '')
    
    def zoom_in(self):
        """Acerca el zoom del gráfico (igual que rueda del mouse)"""
        xlim = self.canvas.ax.get_xlim()
        ylim = self.canvas.ax.get_ylim()
        
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        # Usar el mismo factor que la rueda del mouse
        scale_factor = 1/1.1
        
        x_range = (xlim[1] - xlim[0]) * scale_factor
        y_range = (ylim[1] - ylim[0]) * scale_factor
        
        new_xlim = (x_center - x_range/2, x_center + x_range/2)
        
        self.canvas.ax.set_xlim(new_xlim)
        self.canvas.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
        
        # Actualizar ticks adaptativos
        self.canvas.setup_adaptive_ticks()
        
        # Extender función si es necesario durante el zoom
        self.canvas.extend_function_if_needed(new_xlim)
        
        self.canvas.draw_idle()
    
    def zoom_out(self):
        """Aleja el zoom del gráfico (igual que rueda del mouse)"""
        xlim = self.canvas.ax.get_xlim()
        ylim = self.canvas.ax.get_ylim()
        
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        # Usar el mismo factor que la rueda del mouse
        scale_factor = 1.1
        
        x_range = (xlim[1] - xlim[0]) * scale_factor
        y_range = (ylim[1] - ylim[0]) * scale_factor
        
        new_xlim = (x_center - x_range/2, x_center + x_range/2)
        
        self.canvas.ax.set_xlim(new_xlim)
        self.canvas.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
        
        # Actualizar ticks adaptativos
        self.canvas.setup_adaptive_ticks()
        
        # Extender función si es necesario durante el zoom
        self.canvas.extend_function_if_needed(new_xlim)
        
        self.canvas.draw_idle()
    
    def reset_zoom(self):
        """Restablece el zoom del gráfico"""
        func_str = self.function_input.text().strip()
        if func_str:
            self.plot_function()
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        QMessageBox.about(self, "Acerca de", 
            "Método de la Secante v2.0\n\n"
            "Interfaz gráfica moderna\n"
            "Desarrollado con PyQt5\n\n"
            "Sistema de Análisis Numérico")

    def show_examples_dialog(self):
        """Muestra un diálogo con ejemplos categorizados y permite cargar uno."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ejemplos - Método de la Secante")
        dialog.resize(700, 450)

        layout = QVBoxLayout(dialog)
        tabs = QTabWidget()

        categorias = {
            'Polinomiales': [
                ("x^3 - x - 2", "1.0", "2.0", "0.0001"),
                ("x^2 - 2", "1.0", "2.0", "0.0001"),
                ("x^3 - 6*x^2 + 11*x - 6", "0.0", "3.0", "1e-6")
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
            page = QWidget()
            v = QVBoxLayout(page)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            content = QWidget()
            content_layout = QVBoxLayout(content)

            for func, x0, x1, tol in ejemplos:
                btn = QPushButton(f"{func}  (x0={x0}, x1={x1})")
                btn.clicked.connect(lambda checked, f=func, a=x0, b=x1, t=tol: (self.load_example(f, a, b, t), dialog.accept()))
                content_layout.addWidget(btn)

            content_layout.addStretch()
            scroll.setWidget(content)
            v.addWidget(scroll)
            tabs.addTab(page, cat)

        layout.addWidget(tabs)

        footer = QHBoxLayout()
        empty_btn = QPushButton("Nuevo (vacío)")
        empty_btn.clicked.connect(lambda: (self.new_calculation(), dialog.accept()))
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.reject)
        footer.addWidget(empty_btn)
        footer.addStretch()
        footer.addWidget(close_btn)
        layout.addLayout(footer)

        dialog.exec_()

    def load_example(self, func_str, x0, x1, tol):
        """Carga un ejemplo en los campos de entrada (no ejecuta automáticamente)."""
        try:
            self.function_input.setText(func_str)
            self.x0_input.setText(x0)
            self.x1_input.setText(x1)
            self.tolerance_input.setText(tol)
            self.clear_results()
            self.validate_function()
            self.show_normal_message(f"Ejemplo cargado: {func_str}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el ejemplo: {e}")

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