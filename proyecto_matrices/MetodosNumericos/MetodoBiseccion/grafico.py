import tkinter as tk
from matematicas import preprocesar_funcion, evaluar_funcion

def calcular_rango_optimo(func_str_proc):
    """Calcula el rango óptimo para mostrar la función enfocado en raíces y detalles"""
    rangos_x = [(-5, 5), (-10, 10), (-20, 20)]
    
    mejor_rango = None
    mejor_score = -1
    
    for x_min_test, x_max_test in rangos_x:
        y_vals = []
        y_cerca_cero = []  # Valores Y cerca del eje X
        cambios_signo = 0
        y_anterior = None
        
        for i in range(200):
            x = x_min_test + (x_max_test - x_min_test) * i / 199
            try:
                y = evaluar_funcion(func_str_proc, x)
                if abs(y) < 1e10:
                    y_vals.append(y)
                    # Guardar valores cerca del eje X (zona de interés)
                    if abs(y) < 100:  # Zona cercana a raíces
                        y_cerca_cero.append(y)
                    if y_anterior is not None and y_anterior * y < 0:
                        cambios_signo += 1
                    y_anterior = y
            except:
                continue
        
        if len(y_vals) > 20 and cambios_signo > 0:
            # Si hay valores cerca de cero, usar esos para definir el rango Y
            if len(y_cerca_cero) > 10:
                y_min = min(y_cerca_cero)
                y_max = max(y_cerca_cero)
                # Expandir un poco para ver contexto
                y_range = y_max - y_min
                if y_range < 10:  # Si el rango es muy pequeño, expandir más
                    y_margin = 10
                else:
                    y_margin = y_range * 0.5
            else:
                # Usar percentiles para evitar valores extremos
                y_sorted = sorted(y_vals)
                y_min = y_sorted[len(y_sorted)//10]  # Percentil 10
                y_max = y_sorted[9*len(y_sorted)//10]  # Percentil 90
                y_range = y_max - y_min
                y_margin = y_range * 0.2
            
            score = cambios_signo * 100 - (x_max_test - x_min_test)
            
            if score > mejor_score:
                mejor_score = score
                mejor_rango = (x_min_test, x_max_test, y_min - y_margin, y_max + y_margin)
    
    if mejor_rango:
        return mejor_rango[0], mejor_rango[1], mejor_rango[2], mejor_rango[3], []
    
    return -10, 10, -10, 10, []

def dibujar_grafico(canvas_grafico, entry_function, intervalo=None):
    """Dibuja una gráfica simple usando Canvas
    
    Args:
        canvas_grafico: Canvas donde dibujar
        entry_function: Entry con la función
        intervalo: Tupla (a, b) para hacer zoom en ese intervalo, None para rango automático
    """
    try:
        canvas_grafico.delete("all")
        func_str = entry_function.get().strip()
        if not func_str:
            return None
            
        func_str_proc = preprocesar_funcion(func_str)
        
        # Configuración del canvas
        width = canvas_grafico.winfo_width() or 500
        height = canvas_grafico.winfo_height() or 400
        margin = 40
        
        # Si se proporciona intervalo, hacer zoom en [a, b]
        if intervalo:
            a, b = intervalo
            margen_x = (b - a) * 1.0  # 100% de margen (doble del intervalo)
            x_min = a - margen_x
            x_max = b + margen_x
        else:
            # Calcular rango óptimo usando el algoritmo mejorado
            x_min, x_max, y_min, y_max, puntos = calcular_rango_optimo(func_str_proc)
        
        # Calcular rango Y si aún no está definido (caso de intervalo proporcionado)
        if intervalo:
            y_vals = []
            y_cerca_cero = []
            
            for i in range(200):
                x = x_min + (x_max - x_min) * i / 199
                try:
                    y = evaluar_funcion(func_str_proc, x)
                    if abs(y) < 1e10:
                        y_vals.append(y)
                        if abs(y) < 100:
                            y_cerca_cero.append(y)
                except:
                    continue
            
            if y_vals:
                # Usar valores cerca de cero si existen
                if len(y_cerca_cero) > 10:
                    y_min = min(y_cerca_cero)
                    y_max = max(y_cerca_cero)
                    y_range = y_max - y_min
                    y_margin = max(y_range * 0.5, 10) if y_range < 10 else y_range * 0.5
                else:
                    y_sorted = sorted(y_vals)
                    y_min = y_sorted[len(y_sorted)//10]
                    y_max = y_sorted[9*len(y_sorted)//10]
                    y_range = y_max - y_min
                    y_margin = y_range * 0.2
                
                y_min -= y_margin
                y_max += y_margin
            else:
                y_min, y_max = -10, 10
        
        # Calcular puntos con buena resolución
        puntos = []
        num_puntos = 2000
        for i in range(num_puntos):
            x = x_min + (x_max - x_min) * i / (num_puntos - 1)
            try:
                y = evaluar_funcion(func_str_proc, x)
                if abs(y) < 1e10:  # Solo evitar valores infinitos
                    puntos.append((x, y))
            except:
                continue
        
        if not puntos:
            return None
        
        # Dibujar ejes con mejor calidad
        # Eje X
        y_zero = height - margin - (0 - y_min) * (height - 2*margin) / (y_max - y_min)
        canvas_grafico.create_line(margin, y_zero, width-margin, y_zero, 
                                 fill="#424242", width=1, smooth=True)
        
        # Eje Y
        x_zero = margin + (0 - x_min) * (width - 2*margin) / (x_max - x_min)
        canvas_grafico.create_line(x_zero, margin, x_zero, height-margin, 
                                 fill="#424242", width=1, smooth=True)
        
        # Dibujar función
        if len(puntos) > 1:
            for i in range(len(puntos)-1):
                x1, y1 = puntos[i]
                x2, y2 = puntos[i+1]
                
                # Convertir a coordenadas canvas
                canvas_x1 = margin + (x1 - x_min) * (width - 2*margin) / (x_max - x_min)
                canvas_y1 = height - margin - (y1 - y_min) * (height - 2*margin) / (y_max - y_min)
                canvas_x2 = margin + (x2 - x_min) * (width - 2*margin) / (x_max - x_min)
                canvas_y2 = height - margin - (y2 - y_min) * (height - 2*margin) / (y_max - y_min)
                
                # Verificar que ambos puntos estén dentro del área visible
                if (margin <= canvas_y1 <= height-margin or margin <= canvas_y2 <= height-margin):
                    # Evitar discontinuidades grandes (asíntotas)
                    salto_y = abs(canvas_y2 - canvas_y1)
                    if salto_y < height/2:
                        canvas_grafico.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                                 fill="#1565C0", width=2, smooth=True, 
                                                 capstyle=tk.ROUND, joinstyle=tk.ROUND)
        
        # Etiquetas de los ejes
        canvas_grafico.create_text(width-10, y_zero+15, text="x", fill="black")
        canvas_grafico.create_text(x_zero-15, 10, text="y", fill="black")
        
        # Marcas en los ejes (adaptativas al rango)
        step_x = max(1, int((x_max - x_min) / 6))
        step_y = max(1, int((y_max - y_min) / 4))  # Reducido de 8 a 4 marcas
        
        # Marcas en X
        for i in range(int(x_min), int(x_max) + 1, step_x):
            if i != 0 and x_min <= i <= x_max:
                canvas_x = margin + (i - x_min) * (width - 2*margin) / (x_max - x_min)
                canvas_grafico.create_line(canvas_x, y_zero-3, canvas_x, y_zero+3, 
                                          fill="#757575", width=1)
                canvas_grafico.create_text(canvas_x, y_zero+15, text=str(i), 
                                         fill="#424242", font=("Arial", 8))
        
        # Marcas en Y
        for i in range(int(y_min), int(y_max) + 1, step_y):
            if i != 0 and y_min <= i <= y_max:
                canvas_y = height - margin - (i - y_min) * (height - 2*margin) / (y_max - y_min)
                canvas_grafico.create_line(x_zero-3, canvas_y, x_zero+3, canvas_y, 
                                          fill="#757575", width=1)
                canvas_grafico.create_text(x_zero-15, canvas_y, text=str(i), 
                                         fill="#424242", font=("Arial", 8))
        
        # Retornar el rango utilizado
        return (x_min, x_max, y_min, y_max)
        
    except Exception:
        return None

def dibujar_punto_raiz(canvas_grafico, xr, rango_grafico=None):
    """Dibuja un punto en la raíz encontrada"""
    try:
        width = canvas_grafico.winfo_width() or 500
        height = canvas_grafico.winfo_height() or 400
        margin = 40
        
        # Usar el rango proporcionado o valores por defecto
        if rango_grafico:
            x_min, x_max, y_min, y_max = rango_grafico
        else:
            x_min, x_max, y_min, y_max = -10, 10, -10, 10
        
        # Verificar que la raíz esté en el rango visible
        if x_min <= xr <= x_max:
            # Coordenadas del canvas para la raíz
            canvas_x = margin + (xr - x_min) * (width - 2*margin) / (x_max - x_min)
            y_zero = height - margin - (0 - y_min) * (height - 2*margin) / (y_max - y_min)
            
            # Dibujar punto rojo en la raíz
            canvas_grafico.create_oval(canvas_x-5, y_zero-5, canvas_x+5, y_zero+5, fill="red", outline="darkred", width=2)
            canvas_grafico.create_text(canvas_x, y_zero-15, text=f"Raíz: {xr:.4f}", fill="red", font=("Arial", 10, "bold"))
    except:
        pass