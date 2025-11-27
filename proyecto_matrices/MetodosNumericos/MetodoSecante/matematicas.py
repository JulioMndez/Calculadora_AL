import re
import math

def limpiar_caracteres_unicode(func_str: str) -> str:
    """Limpia caracteres Unicode problemáticos"""
    # Reemplazar caracteres Unicode comunes
    replacements = {
        '−': '-',  # U+2212 (minus sign) -> ASCII hyphen
        '–': '-',  # U+2013 (en dash)
        '—': '-',  # U+2014 (em dash)
        '×': '*',  # U+00D7 (multiplication sign)
        '÷': '/',  # U+00F7 (division sign)
        '²': '^2', # U+00B2 (superscript 2)
        '³': '^3', # U+00B3 (superscript 3)
        '√': 'sqrt', # U+221A (square root)
        'π': 'pi', # U+03C0 (pi)
        '∞': 'inf', # U+221E (infinity)
    }
    
    for unicode_char, ascii_char in replacements.items():
        func_str = func_str.replace(unicode_char, ascii_char)
    
    return func_str

def preprocesar_funcion(func_str: str) -> str:
    """Preprocesa la función para convertir notación matemática"""
    # Limpiar caracteres Unicode primero
    func_str = limpiar_caracteres_unicode(func_str)
    
    func_str = func_str.replace('^', '**')
    
    # Multiplicación implícita: número con constantes y variable (orden importante)
    # Primero: número con pi seguido de x (2pix -> 2*pi*x)
    func_str = re.sub(r'(\d)(\s*)(pi)(\s*)(x)', r'\1*\3*\5', func_str)
    # Primero: número con e seguido de x (3ex -> 3*e*x) - pero NO exp
    func_str = re.sub(r'(\d)(\s*)(e)(\s*)(x)(?![a-z])', r'\1*\3*\5', func_str)
    
    # Luego: número con constante (2pi -> 2*pi, 2e -> 2*e)
    func_str = re.sub(r'(\d)(\s*)(pi)\b', r'\1*\3', func_str)
    func_str = re.sub(r'(\d)(\s*)(e)\b(?!xp)', r'\1*\3', func_str)
    # Número con variable (2x -> 2*x)
    func_str = re.sub(r'(\d)(\s*)(x)', r'\1*\3', func_str)
    
    # Multiplicación implícita: variable/constante con número
    func_str = re.sub(r'(x)(\s*)(\d)', r'\1*\3', func_str)  # x2 -> x*2
    
    # Multiplicación implícita: constantes con variable
    func_str = re.sub(r'(pi)(\s*)(x)', r'\1*\3', func_str)  # pix -> pi*x
    # ex -> e*x SOLO si NO está precedido por 'e' (para evitar exp)
    func_str = re.sub(r'(?<!e)\b(e)(\s*)(x)(?![a-z])', r'\1*\3', func_str)  # ex -> e*x pero no exp
    
    # Multiplicación implícita: número/variable/constante con paréntesis
    # IMPORTANTE: solo si el dígito NO está precedido por letras O dígitos (para evitar log10, log2, etc.)
    func_str = re.sub(r'(?<![a-z0-9])(\d+)(\s*)\(', r'\1*(', func_str)  # 2( -> 2*( (pero no log10()
    func_str = re.sub(r'\b(x)(\s*)\(', r'\1*(', func_str)  # x( -> x*(
    func_str = re.sub(r'(pi)(\s*)\(', r'\1*(', func_str)  # pi( -> pi*(
    func_str = re.sub(r'\b(e)(\s*)\(', r'\1*(', func_str)  # e( -> e*(
    
    # Multiplicación implícita: paréntesis con paréntesis/variable
    func_str = re.sub(r'\)(\s*)\(', r')*(', func_str)  # )( -> )*(
    func_str = re.sub(r'\)(\s*)(x)', r')*\2', func_str)  # )x -> )*x
    func_str = re.sub(r'\)(\s*)([a-z]+)\(', r')*\2(', func_str)  # )sin( -> )*sin(
    
    # Multiplicación implícita: número/variable/constante con función
    # IMPORTANTE: usar \b antes para asegurar que no estamos en medio de una palabra
    func_str = re.sub(r'(\d)(\s*)([a-z]+)\(', r'\1*\3(', func_str)  # 2sin( -> 2*sin(
    func_str = re.sub(r'\b(x)(\s*)([a-z]+)\(', r'\1*\3(', func_str)  # xsin( -> x*sin( (pero no exp)
    func_str = re.sub(r'(pi)(\s*)([a-z]+)\(', r'\1*\3(', func_str)  # pisin( -> pi*sin(
    # esin( -> e*sin( pero NO exp(
    func_str = re.sub(r'\b(e)(\s*)(?!xp)([a-z]+)\(', r'\1*\3(', func_str)
    return func_str

def evaluar_funcion(func_str, x_val):
    """Evalúa la función de forma segura"""
    try:
        import re
        
        # Procesar raíces y logaritmos especiales PRIMERO (antes de reemplazar funciones)
        # Usar función especial para raíz cúbica que maneja negativos correctamente
        def cbrt_real(x):
            """Raíz cúbica que maneja negativos correctamente"""
            if x >= 0:
                return x ** (1/3)
            else:
                return -((-x) ** (1/3))
        
        # Reemplazar cbrt con llamada a función personalizada
        func_str = re.sub(r'cbrt\(', r'cbrt_real(', func_str)
        # root(x,n) = x^(1/n) - el primer parámetro es x, el segundo es n
        func_str = re.sub(r'root\(([^,]+),([^)]+)\)', r'((\1)**(1/(\2)))', func_str)
        func_str = re.sub(r'logb\((.*?),(.*?)\)', r'(math.log(\1)/math.log(\2))', func_str)
        
        # Reemplazar constantes antes de funciones
        func_str = func_str.replace('pi', 'math.pi')
        # Reemplazar 'e' solo si no es parte de 'exp'
        func_str = re.sub(r'\be\b', 'math.e', func_str)
        
        # Reemplazar funciones trigonométricas usando regex para evitar conflictos
        func_str = re.sub(r'\basin\(', 'math.asin(', func_str)
        func_str = re.sub(r'\bacos\(', 'math.acos(', func_str)
        func_str = re.sub(r'\batan\(', 'math.atan(', func_str)
        func_str = re.sub(r'\bsin\(', 'math.sin(', func_str)
        func_str = re.sub(r'\bcos\(', 'math.cos(', func_str)
        func_str = re.sub(r'\btan\(', 'math.tan(', func_str)
        # Reemplazar funciones hiperbólicas e inversas
        func_str = re.sub(r'\basinh\(', 'math.asinh(', func_str)
        func_str = re.sub(r'\bacosh\(', 'math.acosh(', func_str)
        func_str = re.sub(r'\batanh\(', 'math.atanh(', func_str)
        func_str = re.sub(r'\bsinh\(', 'math.sinh(', func_str)
        func_str = re.sub(r'\bcosh\(', 'math.cosh(', func_str)
        func_str = re.sub(r'\btanh\(', 'math.tanh(', func_str)
        # Funciones trigonométricas recíprocas
        func_str = re.sub(r'\bcsc\(', 'csc_func(', func_str)
        func_str = re.sub(r'\bsec\(', 'sec_func(', func_str)
        func_str = re.sub(r'\bcot\(', 'cot_func(', func_str)
        func_str = re.sub(r'\bexp\(', 'math.exp(', func_str)
        func_str = re.sub(r'\bln\(', 'math.log(', func_str)
        func_str = re.sub(r'\blog10\(', 'math.log10(', func_str)
        func_str = re.sub(r'\blog2\(', 'math.log2(', func_str)
        func_str = re.sub(r'\bsqrt\(', 'math.sqrt(', func_str)
        func_str = re.sub(r'\bfloor\(', 'math.floor(', func_str)
        func_str = re.sub(r'\bceil\(', 'math.ceil(', func_str)
        
        func_str = func_str.replace('abs(', 'abs(')
        
        # Reemplazar x por el valor (solo x como variable, no dentro de exp, etc.)
        func_str = re.sub(r'\bx\b', str(x_val), func_str)
        
        # Funciones trigonométricas recíprocas
        def csc_func(x):
            """Cosecante: csc(x) = 1/sin(x)"""
            sin_val = math.sin(x)
            if abs(sin_val) < 1e-15:
                raise ValueError("Cosecante indefinida (sin(x) = 0)")
            return 1 / sin_val
        
        def sec_func(x):
            """Secante: sec(x) = 1/cos(x)"""
            cos_val = math.cos(x)
            if abs(cos_val) < 1e-15:
                raise ValueError("Secante indefinida (cos(x) = 0)")
            return 1 / cos_val
        
        def cot_func(x):
            """Cotangente: cot(x) = cos(x)/sin(x)"""
            sin_val = math.sin(x)
            if abs(sin_val) < 1e-15:
                raise ValueError("Cotangente indefinida (sin(x) = 0)")
            return math.cos(x) / sin_val
        
        # Evaluar de forma segura
        allowed_names = {
            "__builtins__": {},
            "math": math,
            "abs": abs,
            "cbrt_real": cbrt_real,
            "csc_func": csc_func,
            "sec_func": sec_func,
            "cot_func": cot_func
        }
        return eval(func_str, allowed_names)
    except Exception as e:
        raise ValueError(f"Error al evaluar la función: {e}")

def validar_ecuacion(func_str):
    """Valida si la ecuación es correcta"""
    try:
        # Validar profundidad de anidamiento (máximo 10 niveles)
        max_depth = 10
        depth = 0
        max_found = 0
        
        for char in func_str:
            if char == '(':
                depth += 1
                max_found = max(max_found, depth)
            elif char == ')':
                depth -= 1
        
        if max_found > max_depth:
            return False, f"Anidamiento excesivo ({max_found} niveles). Máximo permitido: {max_depth}"
        
        if depth != 0:
            return False, "Paréntesis desbalanceados"
        
        func_str_proc = preprocesar_funcion(func_str)
        # Probar evaluación con x=1
        evaluar_funcion(func_str_proc, 1)
        return True, "Ecuación válida"
    except Exception as e:
        return False, str(e)