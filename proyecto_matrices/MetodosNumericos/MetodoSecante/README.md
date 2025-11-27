# Método de la Secante - Versión PyQt5

## Descripción
Aplicación para resolver ecuaciones no lineales usando el método numérico de la Secante, con una interfaz gráfica moderna inspirada en Microsoft Mathematics.

## Características

### Interfaz PyQt5 (Nueva - Estilo Microsoft Mathematics)
- ✨ Diseño moderno y profesional
- 📊 Gráficos de alta calidad con matplotlib
- 🎯 Botones de funciones con área de scroll
- 📐 Layout responsivo que no se deforma
- 📈 Visualización en tiempo real
- 🔍 Controles de zoom y navegación
- 📋 Resultados detallados paso a paso

### Interfaz Tkinter (Original)
- 🖥️ Interfaz clásica y funcional
- 📊 Gráficos básicos con Canvas
- 🎯 Interacción directa con el gráfico

## Instalación

### Requisitos
```bash
pip install -r requirements.txt
```

### Dependencias
- Python 3.7+
- PyQt5 >= 5.15.0
- matplotlib >= 3.5.0
- numpy >= 1.21.0

### Instalación Rápida (Windows)
```bash
# Ejecutar el instalador automático
install.bat

# O manualmente
pip install PyQt5 matplotlib numpy
```

## Uso

### Ejecutar con interfaz PyQt5 (por defecto)
```bash
python main.py
```

### Ejecutar con interfaz Tkinter
```bash
python main.py --interface tkinter
```

### Opciones de línea de comandos
```bash
python main.py --help
```

## Funciones Soportadas

### Funciones Básicas
- Polinomios: `x^2`, `x^3`, `x^n`
- Aritméticas: `+`, `-`, `*`, `/`

### Funciones Trigonométricas
- `sin(x)`, `cos(x)`, `tan(x)`
- `asin(x)`, `acos(x)`, `atan(x)`
- `sinh(x)`, `cosh(x)`, `tanh(x)`

### Funciones Logarítmicas y Exponenciales
- `exp(x)`, `ln(x)`, `log10(x)`, `log2(x)`
- `logb(x,base)` - logaritmo en base arbitraria

### Funciones de Raíz
- `sqrt(x)` - raíz cuadrada
- `cbrt(x)` - raíz cúbica
- `root(x,n)` - raíz n-ésima

### Constantes
- `pi` - π (3.14159...)
- `e` - número de Euler (2.71828...)

### Otras Funciones
- `abs(x)` - valor absoluto

## Ejemplos de Uso

### Ecuaciones Comunes
1. **Polinómica**: `x^3 - x - 2`
2. **Trigonométrica**: `sin(x) - x/2`
3. **Exponencial**: `exp(x) - 2*x - 1`
4. **Logarítmica**: `ln(x) - 1/x`
5. **Mixta**: `x*sin(x) - 1`

### Pasos para Resolver
1. Ingresa la función en el campo f(x)
2. Haz clic en "Graficar" para visualizar (rango automático inteligente)
3. Observa las raíces aproximadas marcadas en rojo
4. Define los puntos iniciales x0 y x1 (deben ser diferentes)
5. Establece la tolerancia de error (ej: 0.0001)
6. Haz clic en "Encontrar Raíz" para resolver con precisión

## Características de la Interfaz PyQt5

### Panel de Función
- Campo de entrada con validación en tiempo real
- Preview de la ecuación en formato LaTeX renderizado
- 24 botones de funciones matemáticas en área con scroll:
  - **Área fija de 420x130 px** con scroll automático
  - **Botones de tamaño fijo** (65x28 px) que no se deforman
  - **4 filas x 6 columnas** perfectamente organizadas
  - Trigonométricas: sin, cos, tan, asin, acos, atan
  - Hiperbólicas y logaritmos: sinh, cosh, tanh, exp, ln, log10
  - Raíces y potencias: log2, √, ∛, ⁿ√, x², |x|
  - Constantes y especiales: π, e, x³, xⁿ, logb, 1/x

### Panel de Parámetros
- Campos para intervalo [a, b] con validación
- Control de tolerancia de error
- Botones de acción con iconos
- Validación automática de entradas

### Panel de Visualización
- Gráfico de alta resolución (800x600 mínimo)
- **Rango inteligente** que encuentra automáticamente los puntos importantes
- **Detección de raíces** con marcadores visuales
- **3000 puntos de resolución** para gráficos suaves
- **Filtrado de valores extremos** para mejor visualización
- Marcadores de intervalo y raíz encontrada
- Renderizado profesional con matplotlib

### Panel de Resultados
- Iteraciones detalladas paso a paso
- Información de convergencia
- Formato profesional con fuente monoespaciada
- Scroll automático

## Pruebas y Validación

### 🎯 Cobertura de Pruebas
- **45 casos de prueba** exhaustivos
- **91.1% tasa de éxito** global
- **27 universidades** americanas validadas
- **4 libros de texto** reconocidos

### 🏆 Fuentes Académicas
- MIT, Stanford, Harvard, Caltech, Princeton, Yale
- UC Berkeley, Cornell, Columbia, Carnegie Mellon
- Georgia Tech, Northwestern, Duke, Brown, Rice
- Burden & Faires, Chapra & Canale, Atkinson, Kincaid & Cheney

### 🔬 Funciones Probadas
- ✅ Trigonométricas: sin, cos, tan, asin, acos, atan
- ✅ Hiperbólicas: sinh, cosh, tanh
- ✅ Exponenciales: exp, exp(-x), exp(f(x))
- ✅ Logarítmicas: ln, log10, log2, logb
- ✅ Raíces: sqrt, cbrt, root(x,n)
- ✅ Combinaciones complejas de 4+ funciones

### 📊 Ejecutar Pruebas
```bash
# Todas las pruebas (45 casos)
ejecutar_todas_pruebas.bat

# Pruebas exhaustivas (30 casos)
python test_exhaustivo.py

# Pruebas complementarias (15 casos)
python test_botones_faltantes.py
```

### 📄 Documentación de Resultados
- `RESUMEN_FINAL_PRUEBAS.md` - Resumen completo con análisis
- `RESULTADOS_PRUEBAS.md` - Resultados detallados por categoría

## Estructura del Proyecto

```
metodoSecanteV1/
├── main.py                      # Punto de entrada principal
├── interfaz_pyqt.py            # Interfaz PyQt5 (nueva)
├── interfaz.py                 # Interfaz Tkinter (original)
├── metodo_secante.py           # Algoritmo numérico
├── matematicas.py              # Funciones matemáticas
├── grafico.py                  # Funciones de graficación (Tkinter)
├── requirements.txt            # Dependencias
├── README.md                   # Este archivo
├── test_exhaustivo.py          # 30 pruebas de universidades
├── test_botones_faltantes.py   # 15 pruebas complementarias
├── ejecutar_todas_pruebas.bat  # Script para ejecutar todas las pruebas
├── RESUMEN_FINAL_PRUEBAS.md    # Resumen completo de resultados
└── RESULTADOS_PRUEBAS.md       # Resultados detallados
```

## Método de la Secante

### Algoritmo
El método de la secante es un método numérico para encontrar raíces de ecuaciones no lineales que:
- No requiere el cálculo de derivadas (a diferencia de Newton-Raphson)
- Usa dos puntos iniciales para aproximar la derivada
- Converge más rápido que el método de bisección

### Fórmula
```
x2 = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
```

### Condiciones
- x0 y x1 deben ser diferentes
- f(x0) y f(x1) deben ser diferentes (para evitar división por cero)
- La función debe ser continua en la región de interés

## Contribuciones
Este proyecto es parte de un sistema de análisis numérico educativo.

## Licencia
Proyecto educativo - Sistema de Análisis Numérico