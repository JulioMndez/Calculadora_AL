# Método de Bisección - Versión PyQt5

## Descripción
Aplicación para resolver ecuaciones no lineales usando el método numérico de Bisección, con una interfaz gráfica moderna inspirada en Microsoft Mathematics.

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
4. Define el intervalo [a, b] donde f(a) y f(b) tienen signos opuestos
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

## Estructura del Proyecto

```
MetodoBiseccionV7/
├── main.py                 # Punto de entrada principal
├── interfaz_pyqt.py       # Interfaz PyQt5 (nueva)
├── interfaz.py            # Interfaz Tkinter (original)
├── metodo_biseccion.py    # Algoritmo numérico
├── matematicas.py         # Funciones matemáticas
├── grafico.py            # Funciones de graficación (Tkinter)
├── requirements.txt       # Dependencias
└── README.md             # Este archivo
```

## Método de Bisección

### Algoritmo
El método de bisección es un método numérico para encontrar raíces de ecuaciones no lineales que divide repetidamente el intervalo a la mitad y selecciona el subintervalo en el que la función cambia de signo.

### Fórmula
```
xr = (a + b) / 2
```

### Condiciones
- f(a) y f(b) deben tener signos opuestos
- La función debe ser continua en el intervalo [a, b]

## Contribuciones
Este proyecto es parte de un sistema de análisis numérico educativo.

## Licencia
Proyecto educativo - Sistema de Análisis Numérico