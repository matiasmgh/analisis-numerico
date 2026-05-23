# Aproximación por mínimos cuadrados — Degradación de baterías de litio

**Materia:** Análisis Numérico  
**Dataset:** Ciclado de baterías de litio-ion (`b1c0`)  
**Variables:** Número de ciclo de carga (n) y capacidad de descarga (QD)

---

## a) Descripción del problema

### Contexto

Las baterías de litio-ion pierden capacidad progresivamente a medida que se las cicla: cada vez que se cargan y descargan, sufren degradación electroquímica interna. La métrica estándar para medir esa degradación es la **capacidad de descarga (QD)**, medida en Ah, que indica cuánta energía puede entregar la batería en cada ciclo.

Contar con un modelo matemático que describa esa caída permite:

- Estimar cuántos ciclos le quedan a una batería antes de ser reemplazada.
- Predecir la capacidad en ciclos futuros no medidos.
- Comparar el envejecimiento entre distintas baterías o políticas de carga.

### Datos

| Parámetro | Valor |
|---|---|
| Batería analizada | `b1c0` |
| Ciclos disponibles | 2 – 1189 |
| Puntos de datos (limpios) | 1 165 |
| QD inicial (ciclo 2) | 1,0707 Ah |
| QD pico (ciclo 53) | 1,0767 Ah |
| QD final (ciclo 1189) | 1,0262 Ah |
| Caída total de capacidad | ~4,7 % |

> **Nota — fase de formación:** durante los primeros ~53 ciclos, la capacidad *sube* levemente. Es un fenómeno conocido como fase de formación del SEI (*Solid Electrolyte Interphase*): la capa protectora del ánodo termina de formarse y estabilizarse. A partir del ciclo 53 comienza la degradación real, que es el fenómeno que se modela en este trabajo.

**Variables del modelo:**

- **Variable independiente (x):** número de ciclo de carga, *n* ∈ [53, 1189]
- **Variable dependiente (y):** capacidad de descarga *QD(n)* [Ah]

Para el ajuste se utilizan los **1 120 puntos de la fase de degradación** (ciclos 53–1189), que presentan una tendencia decreciente clara y continua.

### Valor a estimar

Se desea conocer la capacidad de descarga de la batería en el **ciclo 1 300**, valor que no se encuentra en el dataset. Esto representa una extrapolación de ~110 ciclos más allá del último dato registrado, útil para anticipar cuándo la batería llegará a un umbral de reemplazo.

---

## b) Nube de puntos

La siguiente figura muestra la evolución de QD a lo largo de los 1 165 ciclos disponibles. Se puede observar la fase de formación inicial (subida hasta el ciclo 53) seguida de la degradación continua.

![Nube de puntos](graphs/scatter.png)

> Archivo vectorial de alta calidad: [`graphs/scatter.svg`](graphs/scatter.svg)

---

## c) Ajuste por mínimos cuadrados

Se ajustan tres modelos sobre la fase de degradación (ciclos 53–1189). Para cada uno se detalla el cambio de variables (si aplica), el sistema de ecuaciones normales, su resolución y la función aproximante resultante.

### Modelo 1 — Lineal

$$QD(n) = a \cdot n + b$$

**Ecuaciones normales** (sistema 2×2):

$$\begin{pmatrix} \sum x^2 & \sum x \\ \sum x & n \end{pmatrix} \begin{pmatrix} a \\ b \end{pmatrix} = \begin{pmatrix} \sum x \cdot f(x) \\ \sum f(x) \end{pmatrix}$$

**Sumas calculadas** sobre los 1 120 puntos de la fase de degradación (ciclos 53–1189):

| Símbolo | Valor |
|---|---|
| $n$ | 1 120 |
| $\sum x$ | 697 406 |
| $\sum f(x)$ | 1 179,370970 |
| $\sum x^2$ | 554 612 058 |
| $\sum x \cdot f(x)$ | 729 213,275097 |

**Fórmulas despejadas:**

$$a = \frac{n \cdot \sum x \cdot f(x) - \sum x \cdot \sum f(x)}{n \cdot \sum x^2 - \left(\sum x\right)^2} = \frac{1120 \cdot 729213{,}2751 - 697406 \cdot 1179{,}3710}{1120 \cdot 554612058 - (697406)^2} = \frac{-5781522{,}6}{134790376124}$$

$$b = \frac{\sum f(x) - a \cdot \sum x}{n} = \frac{1179{,}3710 - (-4{,}2893 \times 10^{-5}) \cdot 697406}{1120} = \frac{1209{,}2848}{1120}$$

**Resultado:**

$$\boxed{QD(n) = -4{,}2893 \times 10^{-5} \cdot n + 1{,}07972}$$

![Recta de mínimos cuadrados](graphs/recta_minimos_cuadrados.png)

---

### Modelo 2 — Parábola de mínimos cuadrados

$$QD(n) = a \cdot n^2 + b \cdot n + c$$

**Ecuaciones normales** (sistema 3×3):

$$\begin{pmatrix} \sum x^4 & \sum x^3 & \sum x^2 \\ \sum x^3 & \sum x^2 & \sum x \\ \sum x^2 & \sum x & n \end{pmatrix} \begin{pmatrix} a \\ b \\ c \end{pmatrix} = \begin{pmatrix} \sum x^2 f(x) \\ \sum x\,f(x) \\ \sum f(x) \end{pmatrix}$$

**Sumas calculadas** sobre los 1 120 puntos de la fase de degradación:

| Símbolo | Valor |
|---|---|
| $n$ | 1 120 |
| $\sum x$ | 697 406 |
| $\sum f(x)$ | 1 179,370970 |
| $\sum x^2$ | 554 612 058 |
| $\sum x^3$ | 495 627 251 390 |
| $\sum x^4$ | 472 505 647 098 402 |
| $\sum x \cdot f(x)$ | 729 213,275097 |
| $\sum x^2 \cdot f(x)$ | 577 619 185,265241 |

**Sistema con valores numéricos:**

$$4{,}7251\times10^{14}\,a \ + \ 4{,}9563\times10^{11}\,b \ + \ 5{,}5461\times10^{8}\,c \ = \ 5{,}7762\times10^{8}$$
$$4{,}9563\times10^{11}\,a \ + \ 5{,}5461\times10^{8}\,b \ + \ 6{,}9741\times10^{5}\,c \ = \ 7{,}2921\times10^{5}$$
$$5{,}5461\times10^{8}\,a \ + \ 6{,}9741\times10^{5}\,b \ + \ 1120\,c \ = \ 1179{,}3710$$

---

**Resolución: reducción a sistema 2×2 + Regla de Cramer**

La idea es eliminar la incógnita $c$ de las tres ecuaciones usando la tercera (la más simple), reduciendo el sistema 3×3 a uno 2×2 que se resuelve con la misma técnica que el modelo lineal.

**Paso 1 — Despejar $c$ de la ecuación 3:**

$$c = \frac{\sum f(x) - \sum x^2 \cdot a - \sum x \cdot b}{n}$$

**Paso 2 — Sustituir en la ecuación 2** y multiplicar todo por $n$ para eliminar el denominador:

$$a \underbrace{\left[n\sum x^3 - \sum x^2 \sum x\right]}_{\alpha} + b\underbrace{\left[n\sum x^2 - \left(\sum x\right)^2\right]}_{\beta} = \underbrace{n\sum x\,f(x) - \sum f(x)\sum x}_{\gamma}$$

$$\alpha = 1120 \cdot 495\,627\,251\,390 - 554\,612\,058 \cdot 697\,406 = 168\,312\,744\,635\,252$$

$$\beta = 1120 \cdot 554\,612\,058 - (697\,406)^2 = 134\,790\,376\,124$$

$$\gamma = 1120 \cdot 729\,213{,}2751 - 1179{,}3710 \cdot 697\,406 = -5\,781\,522{,}3157$$

$$\Rightarrow \text{ecuación (A):} \quad \alpha\,a + \beta\,b = \gamma$$

**Paso 3 — Sustituir en la ecuación 1** y multiplicar por $n$:

$$a \underbrace{\left[n\sum x^4 - \left(\sum x^2\right)^2\right]}_{\alpha'} + b \underbrace{\left[n\sum x^3 - \sum x\sum x^2\right]}_{\beta' = \alpha} = \underbrace{n\sum x^2 f(x) - \sum f(x)\sum x^2}_{\gamma'}$$

$$\alpha' = 1120 \cdot 472\,505\,647\,098\,402 - (554\,612\,058)^2 = 2{,}2161\times10^{17}$$

$$\beta' = \alpha = 168\,312\,744\,635\,252 \quad \text{(por simetría de la matriz normal)}$$

$$\gamma' = 1120 \cdot 577\,619\,185{,}2652 - 1179{,}3710 \cdot 554\,612\,058 = -7\,159\,873\,098{,}2412$$

$$\Rightarrow \text{ecuación (B):} \quad \alpha'\,a + \alpha\,b = \gamma'$$

**Paso 4 — Sistema 2×2 resultante:**

$$\begin{pmatrix} \alpha & \beta \\ \alpha' & \alpha \end{pmatrix} \begin{pmatrix} a \\ b \end{pmatrix} = \begin{pmatrix} \gamma \\ \gamma' \end{pmatrix}$$

**Paso 5 — Regla de Cramer sobre el sistema 2×2:**

$$\det(A_2) = \alpha^2 - \alpha'\,\beta = -1{,}5420\times10^{27}$$

$$a = \frac{\gamma\,\alpha - \gamma'\,\beta}{\det(A_2)} = \frac{-8{,}0219\times10^{18}}{-1{,}5420\times10^{27}} = 5{,}2024\times10^{-9}$$

$$b = \frac{\alpha\,\gamma' - \alpha'\,\gamma}{\det(A_2)} = \frac{7{,}6156\times10^{22}}{-1{,}5420\times10^{27}} = -4{,}9389\times10^{-5}$$

**Paso 6 — Recuperar $c$ por sustitución directa:**

$$c = \frac{1179{,}3710 - (5{,}2024\times10^{-9})\cdot 554\,612\,058 - (-4{,}9389\times10^{-5})\cdot 697\,406}{1120} = 1{,}08119$$

**Resultado:**

Los cálculos manuales arrojan:

| Coeficiente | Valor manual | Valor computacional |
|---|---|---|
| $a$ | $5{,}2047\times10^{-9}$ | $5{,}2024\times10^{-9}$ |
| $b$ | $-4{,}9391\times10^{-5}$ | $-4{,}9389\times10^{-5}$ |
| $c$ | $1{,}08119$ | $1{,}08119$ |

> Los tres coeficientes coinciden en sus primeras cifras significativas. La diferencia en $a$ y $b$ es menor al 0,05 %, lo que confirma que la resolución manual es correcta. Para el ajuste definitivo se adoptan los coeficientes computacionales de mayor precisión.

$$\boxed{QD(n) = 5{,}2024\times10^{-9}\cdot n^2 \ - \ 4{,}9389\times10^{-5}\cdot n \ + \ 1{,}08119}$$

$$QD(1300) = 5{,}2024\times10^{-9}\cdot 1300^2 - 4{,}9389\times10^{-5}\cdot 1300 + 1{,}08119 \approx 1{,}0258 \text{ Ah}$$

![Parábola de mínimos cuadrados](graphs/parabola_minimos_cuadrados.png)

---

### Modelo 3 — Exponencial *(no polinómico)*

$$QD(n) = A \cdot e^{\beta \cdot n}$$

**Linealización:** se aplica logaritmo natural a ambos miembros:

$$\ln(QD) = \ln(A) + \beta \cdot n$$

Con el cambio de variable $Y = \ln(QD)$, $b_0 = \ln(A)$, $b_1 = \beta$, el modelo se convierte en uno lineal:

$$Y(n) = b_1 \cdot n + b_0$$

Se aplican las ecuaciones normales del modelo lineal sobre las parejas $(n_i,\ \ln(QD_i))$. Las sumas necesarias son las mismas que en el modelo lineal, reemplazando $f(x_i)$ por $\ln(QD_i)$:

**Sumas calculadas** sobre los 1 120 puntos de la fase de degradación:

| Símbolo | Valor |
|---|---|
| $n$ | 1 120 |
| $\sum x$ | 697 406 |
| $\sum \ln f(x)$ | 57,739676 |
| $\sum x^2$ | 554 612 058 |
| $\sum x \cdot \ln f(x)$ | 31 052,794272 |

**Sistema con valores numéricos:**

$$1120\,b_0 \ + \ 697{,}406\,b_1 \ = \ 57{,}739676$$
$$697{,}406\,b_0 \ + \ 554{,}612{,}058\,b_1 \ = \ 31{,}052{,}794272$$

**Resolución — Regla de Cramer sobre el sistema 2×2:**

$$\det(A) = n\cdot\sum x^2 - (\sum x)^2 = 1120\cdot554{,}612{,}058 - (697{,}406)^2 = 134{,}790{,}376{,}124$$

$$b_1 = \frac{n\cdot\sum x\ln f(x) - \sum x\cdot\sum \ln f(x)}{\det(A)} = \frac{-5{,}488{,}866{,}982}{134{,}790{,}376{,}124} = -4{,}0722\times10^{-5}$$

$$b_0 = \frac{\sum \ln f(x) - b_1\cdot\sum x}{n} = \frac{57{,}7397 - (-4{,}0722\times10^{-5})\cdot697{,}406}{1120} = 0{,}07691$$

$$A = e^{b_0} = e^{0{,}07691} = 1{,}07994$$

**Comparación con el cálculo manual:**

| Coeficiente | Valor manual | Valor computacional |
|---|---|---|
| $b_0$ | 0,07691 | 0,07691 |
| $A = e^{b_0}$ | 1,07994 | 1,079945 |
| $\beta = b_1$ | $-4{,}0722\times10^{-5}$ | $-4{,}0722\times10^{-5}$ |

> Los valores manuales coinciden con los computacionales en todas las cifras significativas obtenidas.

**Resultado:**

$$\boxed{QD(n) = 1{,}07994 \cdot e^{-4{,}0722\times10^{-5}\cdot n}}$$

$$QD(1300) = 1{,}07994 \cdot e^{-4{,}0722\times10^{-5}\cdot 1300} \approx 1{,}0243 \text{ Ah}$$

![Exponencial de mínimos cuadrados](graphs/exponencial_minimos_cuadrados.png)

---

### Comparación gráfica

*(Se generará en la siguiente etapa del trabajo.)*

![Aproximaciones](graphs/approximations.png)

---

## d) Comparación y elección del mejor modelo

La comparación se realizará usando el **coeficiente de determinación R²**:

$$R^2 = 1 - \frac{\sum (QD_i - \hat{QD}_i)^2}{\sum (QD_i - \overline{QD})^2}$$

Un R² más cercano a 1 indica mejor ajuste. Se evaluará además si la curva elegida tiene sentido físico para extrapolar al ciclo 1 300.

*(Resultados y análisis se completarán una vez calculados los coeficientes.)*

---

## Estructura del proyecto

```
analisis-numerico/
├── data/
│   └── dataset.csv       # Dataset de ciclado de baterías
├── graphs/
│   ├── scatter.svg / .png          # Nube de puntos
│   └── approximations.svg / .png   # Curvas de ajuste
├── src/
│   └── main.py           # Script principal (scatter + ajustes)
├── requirements.txt
└── README.md
```

## Ejecución

```bash
# Activar entorno virtual
source venv/bin/activate

# Generar gráficos
cd src
python main.py
```
