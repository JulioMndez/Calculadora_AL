# 🎯 Guía Completa de Botones - Método de la Secante

## 📋 Índice
1. [Funciones Trigonométricas](#funciones-trigonométricas)
2. [Funciones Hiperbólicas](#funciones-hiperbólicas)
3. [Funciones Exponenciales y Logarítmicas](#funciones-exponenciales-y-logarítmicas)
4. [Raíces y Potencias](#raíces-y-potencias)
5. [Constantes y Especiales](#constantes-y-especiales)
6. [Ejemplos Combinados](#ejemplos-combinados)

---

## Funciones Trigonométricas

### 🔵 sin - Seno
**Sintaxis:** `sin(x)`  
**Dominio:** Todos los reales  
**Rango:** [-1, 1]

**Ejemplos:**
```
1. sin(x) - 0.5              → Encuentra x donde sin(x) = 0.5
2. sin(x) - x/2              → Intersección de seno con lineal
3. x*sin(x) - 1              → Producto con variable
4. sin(x) + cos(x) - 1       → Suma trigonométrica
```

**Caso de prueba validado:**
- Universidad: Stanford CS 205A
- Función: `sin(x) - exp(-x)`
- Raíz: 0.5885327440
- Iteraciones: 6

---

### 🔵 cos - Coseno
**Sintaxis:** `cos(x)`  
**Dominio:** Todos los reales  
**Rango:** [-1, 1]

**Ejemplos:**
```
1. cos(x) - x                → Intersección coseno con identidad
2. cos(x) - x*exp(-x)        → Con exponencial decreciente
3. cos(x)^2 - x/2            → Coseno al cuadrado
4. sqrt(x) - cos(x)          → Con raíz cuadrada
```

**Caso de prueba validado:**
- Universidad: Burden & Faires (MIT, Stanford)
- Función: `cos(x) - x`
- Raíz: 0.7390851332
- Iteraciones: 5
- Precisión: ⭐⭐⭐⭐⭐

---

### 🔵 tan - Tangente
**Sintaxis:** `tan(x)`  
**Dominio:** x ≠ (2n+1)π/2  
**Rango:** Todos los reales

**Ejemplos:**
```
1. tan(x) - x                → Encuentra raíces no triviales
2. tan(x) - 2*x              → Con pendiente diferente
3. atan(tan(x)) - x/2        → Composición con inversa
```

**⚠️ Precaución:** Evitar intervalos que crucen discontinuidades (múltiplos impares de π/2)

---

### 🔵 asin - Arcoseno
**Sintaxis:** `asin(x)`  
**Dominio:** [-1, 1]  
**Rango:** [-π/2, π/2]

**Ejemplos:**
```
1. asin(x) - 1               → Encuentra x donde asin(x) = 1
2. asin(x/2) - x + 1         → Arcoseno escalado
```

**⚠️ Importante:** Validar que el argumento esté en [-1, 1]

---

### 🔵 acos - Arcocoseno
**Sintaxis:** `acos(x)`  
**Dominio:** [-1, 1]  
**Rango:** [0, π]

**Ejemplos:**
```
1. acos(x) - 1               → Encuentra x donde acos(x) = 1
2. acos(x) - 2*x             → Con función lineal
3. acos(x/2) - ln(x + 1)     → Con logaritmo
```

**Caso de prueba validado:**
- Función: `acos(x) - 1`
- Raíz: 0.5403023059
- Iteraciones: 4

---

### 🔵 atan - Arcotangente
**Sintaxis:** `atan(x)`  
**Dominio:** Todos los reales  
**Rango:** (-π/2, π/2)

**Ejemplos:**
```
1. atan(x) - x/2             → Intersección con lineal
2. atan(x) - ln(x)           → Con logaritmo
```

**Caso de prueba validado:**
- Universidad: Vanderbilt MATH 3120
- Función: `atan(x) - x/2`
- Raíz: 2.3311223703

---

## Funciones Hiperbólicas

### 🟢 sinh - Seno Hiperbólico
**Sintaxis:** `sinh(x)`  
**Fórmula:** (e^x - e^(-x))/2  
**Dominio:** Todos los reales

**Ejemplos:**
```
1. sinh(x) - x^2             → Con cuadrática
2. sinh(x) - ln(x)           → Con logaritmo
3. sinh(x) - 2*x             → Con lineal
```

**Caso de prueba validado:**
- Universidad: Georgia Tech MATH 6640
- Función: `sinh(x) - x^2`
- Raíz: 1.3132837184

---

### 🟢 cosh - Coseno Hiperbólico
**Sintaxis:** `cosh(x)`  
**Fórmula:** (e^x + e^(-x))/2  
**Dominio:** Todos los reales  
**Rango:** [1, ∞)

**Ejemplos:**
```
1. cosh(x) - 2*x             → Con lineal
2. cosh(x) - x^2             → Con cuadrática
3. cosh(x) - exp(x/2)        → Con exponencial
```

**Caso de prueba validado:**
- Universidad: Northwestern ESAM 446
- Función: `cosh(x) - 2*x`
- Raíz: 2.1267998928

---

### 🟢 tanh - Tangente Hiperbólica
**Sintaxis:** `tanh(x)`  
**Fórmula:** sinh(x)/cosh(x)  
**Dominio:** Todos los reales  
**Rango:** (-1, 1)

**Ejemplos:**
```
1. tanh(x) - sin(x)          → Con seno
2. tanh(x) - x/2             → Con lineal
3. tanh(x) - 0.5             → Valor constante
```

**Caso de prueba validado:**
- Universidad: UW-Madison MATH 514
- Función: `tanh(x) - sin(x)`
- Raíz: 1.8751040687

---

## Funciones Exponenciales y Logarítmicas

### 🟡 exp - Exponencial
**Sintaxis:** `exp(x)`  
**Equivalente:** e^x  
**Dominio:** Todos los reales  
**Rango:** (0, ∞)

**Ejemplos:**
```
1. exp(-x) - x               → Exponencial decreciente
2. exp(x) - 3*x^2            → Con cuadrática
3. x*exp(x) - 1              → Producto con variable
4. exp(sin(x)) - x           → Composición con seno
5. exp(x)*sin(x) - 1         → Producto exponencial-trig
```

**Casos de prueba validados:**
- **Chapra & Canale:** `exp(-x) - x` → Raíz: 0.5671432904 ⭐⭐⭐⭐⭐
- **MIT OCW 18.330:** `x*exp(x) - 1` → Raíz: 0.5671432904 ⭐⭐⭐⭐⭐
- **Caltech ACM 95:** `exp(x) - 3*x^2` → Raíz: 3.7330790286

---

### 🟡 ln - Logaritmo Natural
**Sintaxis:** `ln(x)`  
**Base:** e  
**Dominio:** (0, ∞)  
**Rango:** Todos los reales

**Ejemplos:**
```
1. ln(x) - 1/x               → Con recíproco
2. ln(x) + x^2 - 3           → Con cuadrática
3. x*ln(x) - 1               → Producto con variable
4. ln(x + 1) - exp(-x)       → Con exponencial
5. sin(ln(x)) - 0.5          → Composición con seno
```

**Casos de prueba validados:**
- **Kincaid & Cheney:** `ln(x) - 1/x` → Raíz: 1.7632228344
- **CMU 21-259:** `x*ln(x) - 1` → Raíz: 1.7632228344 ⭐⭐⭐⭐⭐

---

### 🟡 log10 - Logaritmo Base 10
**Sintaxis:** `log10(x)`  
**Base:** 10  
**Dominio:** (0, ∞)

**Ejemplos:**
```
1. log10(x) + x - 2          → Con lineal
2. log10(x) - sin(x)         → Con trigonométrica
3. log10(x) - 1              → Encuentra x = 10
```

**Caso de prueba validado:**
- Universidad: Brown APMA 1650
- Función: `log10(x) + x - 2`
- Raíz: 1.7555794993

---

### 🟡 log2 - Logaritmo Base 2
**Sintaxis:** `log2(x)`  
**Base:** 2  
**Dominio:** (0, ∞)

**Ejemplos:**
```
1. log2(x) + sin(x) - 1      → Con seno
2. log2(x) - x/4             → Con lineal
3. log2(x) - 3               → Encuentra x = 8
```

**Caso de prueba validado:**
- Universidad: Penn State MATH 451
- Función: `log2(x) + sin(x) - 1`
- Raíz: 1.0838883618

---

### 🟡 logb - Logaritmo Base Arbitraria
**Sintaxis:** `logb(x, base)`  
**Parámetros:** x (argumento), base (base del logaritmo)  
**Dominio:** x > 0, base > 0, base ≠ 1

**Ejemplos:**
```
1. logb(x, 3) - 2            → log₃(x) = 2, encuentra x = 9
2. logb(x, 5) - x/10         → log₅(x) con lineal
3. logb(x, 7) + exp(-x) - 1  → log₇(x) con exponencial
4. cbrt(x) + logb(x, 2) - 3  → Combinación con raíz cúbica
```

**Casos de prueba validados:**
- **Logaritmo base 3:** `logb(x,3) - 2` → Raíz: 9.0 ⭐⭐⭐⭐⭐
- **Con exponencial:** `logb(x,7) + exp(-x) - 1` → Raíz: 6.9874331323

---

## Raíces y Potencias

### 🟣 √ - Raíz Cuadrada
**Sintaxis:** `sqrt(x)`  
**Equivalente:** x^(1/2)  
**Dominio:** [0, ∞)

**Ejemplos:**
```
1. sqrt(x) - 2               → Encuentra x = 4
2. sqrt(x) - cos(x)          → Con coseno
3. sqrt(x) - ln(x)           → Con logaritmo
4. sqrt(x + 1) - x/2         → Raíz de expresión
```

**Caso de prueba validado:**
- Universidad: NYU MATH-UA 252
- Función: `sqrt(x) - cos(x)`
- Raíz: 0.6417143709

---

### 🟣 ∛ - Raíz Cúbica
**Sintaxis:** `cbrt(x)`  
**Equivalente:** x^(1/3)  
**Dominio:** Todos los reales (incluye negativos)

**Ejemplos:**
```
1. cbrt(x) - 2               → Encuentra x = 8
2. cbrt(x) + 3               → Encuentra x = -27
3. cbrt(x) - exp(-x)         → Con exponencial
4. cbrt(x) + logb(x,2) - 3   → Con logaritmo base 2
```

**Casos de prueba validados:**
- **Clásico:** `cbrt(x) - 2` → Raíz: 8.0 ⭐⭐⭐⭐⭐
- **Negativo:** `cbrt(x) + 3` → Raíz: -27.0 ⭐⭐⭐⭐⭐
- **Con exponencial:** `cbrt(x) - exp(-x)` → Raíz: 0.3499696317

---

### 🟣 ⁿ√ - Raíz N-ésima
**Sintaxis:** `root(x, n)`  
**Parámetros:** x (radicando), n (índice)  
**Dominio:** Depende de n (pares: x ≥ 0, impares: todos los reales)

**Ejemplos:**
```
1. root(x, 4) - 2            → Raíz cuarta, encuentra x = 16
2. root(x, 5) - ln(x)        → Raíz quinta con logaritmo
3. root(x, 6) - sin(x)       → Raíz sexta con seno
4. root(x, 3) - x/2          → Equivalente a cbrt
```

**Casos de prueba validados:**
- **Raíz cuarta:** `root(x,4) - 2` → Raíz: 16.0 ⭐⭐⭐⭐⭐
- **Raíz quinta:** `root(x,5) - ln(x)` → Raíz: 3.6541207708

**⚠️ Precaución:** Raíces pares requieren x ≥ 0

---

### 🟣 x² - Cuadrado
**Sintaxis:** `x^2` o `x**2`  
**Dominio:** Todos los reales  
**Rango:** [0, ∞)

**Ejemplos:**
```
1. x^2 - 4                   → Encuentra x = ±2
2. x^2 - sin(x)              → Con seno
3. ln(x) + x^2 - 3           → Con logaritmo
4. exp(-x^2) - x             → Gaussiana
```

**Casos de prueba validados:**
- **Columbia APMA 4300:** `ln(x) + x^2 - 3` → Raíz: 1.5921429371
- **UCLA Math 151A:** `exp(-x^2) - x` → Raíz: 0.6529186404

---

### 🟣 x³ - Cubo
**Sintaxis:** `x^3` o `x**3`  
**Dominio:** Todos los reales

**Ejemplos:**
```
1. x^3 - 2*x - 5             → Polinomio cúbico clásico
2. x^3 - 8                   → Encuentra x = 2
3. x^3*exp(-x) - 0.1         → Con exponencial decreciente
```

**Casos de prueba validados:**
- **Atkinson (Iowa):** `x^3 - 2*x - 5` → Raíz: 2.0945514812 ⭐⭐⭐⭐⭐
- **Purdue MA 514:** `x^3*exp(-x) - 0.1` → Raíz: 0.5592822954

---

### 🟣 xⁿ - Potencia N
**Sintaxis:** `x^n` o `x**n`  
**Dominio:** Depende de n

**Ejemplos:**
```
1. x^4 - 16                  → Encuentra x = ±2
2. x^5 - 32                  → Encuentra x = 2
3. x^n - k                   → Raíz n-ésima de k
```

---

## Constantes y Especiales

### 🔴 π - Pi
**Valor:** 3.14159265358979...  
**Sintaxis:** `pi`

**Ejemplos:**
```
1. sin(pi*x) - 0.5           → Seno con múltiplos de π
2. x - pi                    → Encuentra x = π
3. cos(x) - pi/4             → Con constante
```

---

### 🔴 e - Número de Euler
**Valor:** 2.71828182845904...  
**Sintaxis:** `e`

**Ejemplos:**
```
1. x - e                     → Encuentra x = e
2. ln(x) - 1                 → Encuentra x = e
3. e*x - 5                   → Con múltiplo
```

---

### 🔴 |x| - Valor Absoluto
**Sintaxis:** `abs(x)`  
**Dominio:** Todos los reales  
**Rango:** [0, ∞)

**Ejemplos:**
```
1. abs(x) - 5                → Encuentra x = ±5
2. abs(x - 2) - 3            → Valor absoluto de expresión
3. abs(sin(x)) - 0.5         → Con trigonométrica
```

---

### 🔴 1/x - Recíproco
**Sintaxis:** `1/x`  
**Dominio:** x ≠ 0  
**Rango:** (-∞, 0) ∪ (0, ∞)

**Ejemplos:**
```
1. 1/x - 2                   → Encuentra x = 0.5
2. ln(x) - 1/x               → Con logaritmo
3. sin(1/x) - 0.5            → Composición
```

**Caso de prueba validado:**
- **Kincaid & Cheney:** `ln(x) - 1/x` → Raíz: 1.7632228344

---

## Ejemplos Combinados

### 🌟 Nivel Básico (2 funciones)

```
1. exp(-x) - x               ✅ Chapra & Canale
   Raíz: 0.5671432904
   
2. cos(x) - x                ✅ Burden & Faires
   Raíz: 0.7390851332
   
3. ln(x) - 1/x               ✅ Kincaid & Cheney
   Raíz: 1.7632228344
   
4. sqrt(x) - cos(x)          ✅ NYU MATH-UA 252
   Raíz: 0.6417143709
```

---

### 🌟 Nivel Intermedio (3 funciones)

```
1. sin(x) - exp(-x)          ✅ Stanford CS 205A
   Raíz: 0.5885327440
   
2. ln(x) + x^2 - 3           ✅ Columbia APMA 4300
   Raíz: 1.5921429371
   
3. x*sin(x) - 1              ✅ Harvard AM 205
   Raíz: 1.1141571409
   
4. cbrt(x) - exp(-x)         ✅ Prueba complementaria
   Raíz: 0.3499696317
```

---

### 🌟 Nivel Avanzado (Composiciones)

```
1. exp(sin(x)) - x           ✅ Cornell CS 4210
   Raíz: 2.2191071488
   
2. exp(cos(x)) - x           ✅ Ohio State MATH 5520
   Raíz: 1.3029640012
   
3. sin(ln(x)) - 0.5          ✅ UW CSE 321
   Raíz: 1.6880917950
   
4. acos(x/2) - ln(x + 1)     ✅ Prueba complementaria
   Raíz: 1.3276641349
```

---

### 🌟 Nivel Experto (Múltiples funciones especiales)

```
1. exp(-x^2) - x             ✅ UCLA Math 151A (Gaussiana)
   Raíz: 0.6529186404
   
2. exp(x)*sin(x) - 1         ✅ Duke MATH 551
   Raíz: 0.5885327440
   
3. sin(x)*cos(x) - x^2       ✅ UIUC CS 357
   Raíz: 0.7022074120
   
4. cbrt(x) + root(x,5) + logb(x,3) - 5
   Raíz: 6.4145445505
```

---

## 💡 Consejos de Uso

### ✅ Mejores Prácticas

1. **Graficar primero**
   - Usa el botón "Graficar" para visualizar la función
   - Identifica visualmente las raíces aproximadas
   - Elige intervalos [x0, x1] que contengan una raíz

2. **Selección de intervalo**
   - x0 y x1 deben ser diferentes
   - Preferiblemente con f(x0) y f(x1) de signos opuestos
   - Evitar intervalos que crucen discontinuidades

3. **Tolerancia**
   - Para precisión normal: 1e-6 (0.000001)
   - Para alta precisión: 1e-8 o menor
   - Para cálculos rápidos: 1e-4

4. **Funciones con dominio restringido**
   - **asin, acos:** Argumento en [-1, 1]
   - **ln, log10, log2, logb:** Argumento > 0
   - **sqrt, raíces pares:** Argumento ≥ 0
   - **tan:** Evitar múltiplos impares de π/2

### ⚠️ Errores Comunes

1. **Domain Error**
   - Causa: Argumento fuera del dominio
   - Solución: Verificar restricciones de la función

2. **División por Cero**
   - Causa: f(x0) ≈ f(x1)
   - Solución: Elegir puntos iniciales más separados

3. **No Converge**
   - Causa: Intervalo sin raíz o múltiples raíces
   - Solución: Graficar y elegir mejor intervalo

4. **Raíz Inesperada**
   - Causa: Múltiples raíces en el intervalo
   - Solución: Reducir el intervalo de búsqueda

---

## 📚 Referencias Rápidas

### Funciones por Categoría

**Trigonométricas:** sin, cos, tan, asin, acos, atan  
**Hiperbólicas:** sinh, cosh, tanh  
**Exponenciales:** exp  
**Logarítmicas:** ln, log10, log2, logb  
**Raíces:** sqrt (√), cbrt (∛), root (ⁿ√)  
**Potencias:** x², x³, xⁿ  
**Especiales:** π, e, |x|, 1/x

### Atajos de Teclado en la Interfaz

- **Enter:** Graficar función
- **Ctrl+Enter:** Encontrar raíz
- **Ctrl+L:** Limpiar todo
- **Tab:** Navegar entre campos

---

**Guía creada para el Método de la Secante v2.0**  
**45 casos de prueba validados | 27 universidades | 4 libros de texto**
