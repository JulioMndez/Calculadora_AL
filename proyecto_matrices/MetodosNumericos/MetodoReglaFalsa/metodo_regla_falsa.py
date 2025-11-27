from matematicas import preprocesar_funcion, evaluar_funcion

def ejecutar_metodo_regla_falsa(func_str, a, b, tolerance, max_iter):
    """
    Ejecuta el método de regla falsa
    Retorna: (exito, resultado, iteraciones_data)
    """
    try:
        func_str_proc = preprocesar_funcion(func_str)

        # Evaluar función en los extremos
        fa = evaluar_funcion(func_str_proc, a)
        fb = evaluar_funcion(func_str_proc, b)

        if fa * fb >= 0:
            return False, "f(a) y f(b) deben tener signos opuestos.", []

        # El error ya viene en formato decimal
        tolerance_decimal = tolerance

        xr_old = a
        iteraciones_data = []
        
        for i in range(max_iter):
            # Verificar división por cero
            if abs(fa - fb) < 1e-15:
                return False, "Error: fa y fb son muy similares, división por cero.", []
            
            # Fórmula de la regla falsa
            xr = b - (fb * (a - b)) / (fa - fb)
            fxr = evaluar_funcion(func_str_proc, xr)
            
            # Calcular error relativo en formato decimal
            error_rel_decimal = abs((xr - xr_old) / (xr if xr != 0 else 1)) if i > 0 else float('inf')

            # Guardar datos de la iteración
            iteracion_info = {
                'iteracion': i + 1,
                'a': a,
                'b': b,
                'xr': xr,
                'fa': fa,
                'fb': fb,
                'fxr': fxr,
                'error_rel': error_rel_decimal  # Mostrar en decimal
            }
            iteraciones_data.append(iteracion_info)

            # Verificar convergencia
            if abs(fxr) < 1e-12 or (i > 0 and error_rel_decimal < tolerance_decimal):
                return True, {
                    'raiz': xr,
                    'iteracion': i + 1,
                    'error': error_rel_decimal,  # Devolver en decimal
                    'convergio': True
                }, iteraciones_data

            # Actualizar intervalo
            if fa * fxr < 0:
                b, fb = xr, fxr
            else:
                a, fa = xr, fxr

            xr_old = xr

        # Máximo de iteraciones alcanzado
        return True, {
            'raiz': xr,
            'iteracion': max_iter,
            'error': error_rel_decimal,  # Devolver en decimal
            'convergio': False
        }, iteraciones_data

    except Exception as e:
        return False, str(e), []