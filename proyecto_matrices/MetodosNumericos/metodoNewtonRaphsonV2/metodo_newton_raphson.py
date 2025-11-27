import math
from matematicas import preprocesar_funcion, evaluar_funcion

def calcular_derivada_numerica(func_str, x_val, h=1e-8):
    """
    Calcula la derivada numérica usando diferencias finitas.
    Maneja discontinuidades (nan) de forma robusta.
    """
    # Diferencias centrales
    f_plus = evaluar_funcion(func_str, x_val + h)
    f_minus = evaluar_funcion(func_str, x_val - h)
    
    if not math.isnan(f_plus) and not math.isnan(f_minus):
        return (f_plus - f_minus) / (2 * h)
    
    # Si fallan las centrales, probar diferencias hacia adelante
    f_current = evaluar_funcion(func_str, x_val)
    if not math.isnan(f_plus) and not math.isnan(f_current):
        return (f_plus - f_current) / h
        
    # Si fallan ambas, no se puede calcular la derivada
    return float('nan')

def ejecutar_metodo_newton_raphson(func_str, x0, tolerance, max_iter):
    """
    Ejecuta el método de Newton-Raphson
    Retorna: (exito, resultado, iteraciones_data)
    """
    try:
        func_str_proc = preprocesar_funcion(func_str)
        
        tolerance_decimal = tolerance
        xn_old = x0
        iteraciones_data = []
        
        for i in range(max_iter):
            # Evaluar función en xn
            fxn = evaluar_funcion(func_str_proc, xn_old)
            
            if math.isnan(fxn):
                return False, f"Error: La función no está definida en x = {xn_old:.4f} (discontinuidad).", iteraciones_data
            
            # Calcular derivada numérica
            fpxn = calcular_derivada_numerica(func_str_proc, xn_old)
            
            if math.isnan(fpxn):
                return False, f"Error: La derivada no se puede calcular en x = {xn_old:.4f} (posible discontinuidad).", iteraciones_data
            
            if abs(fpxn) < 1e-15:
                return False, "Error: La derivada es cero, el método no puede continuar.", iteraciones_data
            
            # Fórmula de Newton-Raphson: xn = xn-1 - f(xn-1) / f'(xn-1)
            xn = xn_old - fxn / fpxn
            
            # Calcular error relativo
            error_rel_decimal = abs((xn - xn_old) / (xn if xn != 0 else 1)) if i > 0 else float('inf')
            
            # Guardar datos de la iteración
            iteracion_info = {
                'iteracion': i + 1,
                'xn': xn_old,
                'fxn': fxn,
                'fpxn': fpxn,
                'xn_nuevo': xn,
                'error_rel': error_rel_decimal
            }
            iteraciones_data.append(iteracion_info)
            
            # Verificar convergencia
            if abs(fxn) < 1e-12 or (i > 0 and error_rel_decimal < tolerance_decimal):
                return True, {
                    'raiz': xn,
                    'iteracion': i + 1,
                    'error': error_rel_decimal,
                    'convergio': True
                }, iteraciones_data
            
            xn_old = xn
        
        # Máximo de iteraciones alcanzado
        return True, {
            'raiz': xn,
            'iteracion': max_iter,
            'error': error_rel_decimal,
            'convergio': False
        }, iteraciones_data
    
    except Exception as e:
        return False, str(e), []
