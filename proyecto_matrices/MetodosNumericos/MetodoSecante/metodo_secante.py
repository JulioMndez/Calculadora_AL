from matematicas import preprocesar_funcion, evaluar_funcion

def ejecutar_metodo_secante(func_str, x0, x1, tolerance, max_iter):
    """
    Ejecuta el método de la secante
    Retorna: (exito, resultado, iteraciones_data)
    """
    try:
        func_str_proc = preprocesar_funcion(func_str)

        # Evaluar función en los puntos iniciales
        fx0 = evaluar_funcion(func_str_proc, x0)
        fx1 = evaluar_funcion(func_str_proc, x1)

        # El error ya viene en formato decimal
        tolerance_decimal = tolerance

        iteraciones_data = []
        
        for i in range(max_iter):
            # Verificar división por cero
            if abs(fx1 - fx0) < 1e-15:
                return False, "Error: f(x1) y f(x0) son muy similares, división por cero.", []
            
            # Fórmula del método de la secante
            x2 = x1 - (fx1 * (x1 - x0)) / (fx1 - fx0)
            fx2 = evaluar_funcion(func_str_proc, x2)
            
            # Calcular error relativo en formato decimal
            error_rel_decimal = abs((x2 - x1) / (x2 if x2 != 0 else 1)) if i >= 0 else float('inf')

            # Guardar datos de la iteración
            iteracion_info = {
                'iteracion': i + 1,
                'x0': x0,
                'x1': x1,
                'x2': x2,
                'fx0': fx0,
                'fx1': fx1,
                'fx2': fx2,
                'error_rel': error_rel_decimal
            }
            iteraciones_data.append(iteracion_info)

            # Verificar convergencia
            if abs(fx2) < 1e-12 or error_rel_decimal < tolerance_decimal:
                return True, {
                    'raiz': x2,
                    'iteracion': i + 1,
                    'error': error_rel_decimal,
                    'convergio': True
                }, iteraciones_data

            # Actualizar puntos para la siguiente iteración
            x0, fx0 = x1, fx1
            x1, fx1 = x2, fx2

        # Máximo de iteraciones alcanzado
        return True, {
            'raiz': x2,
            'iteracion': max_iter,
            'error': error_rel_decimal,
            'convergio': False
        }, iteraciones_data

    except Exception as e:
        return False, str(e), []