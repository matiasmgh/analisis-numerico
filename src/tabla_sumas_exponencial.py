"""
Tabla de sumas para el ajuste exponencial por mínimos cuadrados
================================================================
Modelo:  QD(n) = A · e^(β·n)

Linealización:  Y = ln(QD)  →  Y(n) = β·n + b₀
con  b₀ = ln(A),  β = b₁

Sistema de ecuaciones normales (idéntico al lineal pero sobre Y = ln f(x)):

    b₀ · n     + b₁ · Σx   = Σ ln f(x)
    b₀ · Σx    + b₁ · Σx²  = Σ x · ln f(x)

Resolución directa (Cramer 2×2):

    b₁ = [n · Σx·ln f(x)  −  Σx · Σ ln f(x)] / [n · Σx²  −  (Σx)²]
    b₀ = [Σ ln f(x)  −  b₁ · Σx] / n
    A  = e^b₀

Variables:
    x    = número de ciclo de carga
    f(x) = capacidad de descarga QD [Ah]
    n    = cantidad de puntos (fase de degradación, ciclos 53–1189)

Genera:
    - Tabla completa en  data/tabla_sumas_exponencial.csv
    - Muestra por consola las primeras y últimas filas + totales + resolución
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Carga y filtro — fase de degradación
# ---------------------------------------------------------------------------
df = pd.read_csv("../data/dataset.csv")
b  = df[df["battery_id"] == "b1c0"].sort_values("cycle")

q_low  = b["QD"].quantile(0.01)
q_high = b["QD"].quantile(0.99)
b = b[(b["QD"] >= q_low) & (b["QD"] <= q_high)]

peak_cycle = b.loc[b["QD"].idxmax(), "cycle"]
deg = b[b["cycle"] >= peak_cycle].reset_index(drop=True)

x  = deg["cycle"].values.astype(float)
fx = deg["QD"].values
Y  = np.log(fx)          # cambio de variable: Y = ln(QD)

# ---------------------------------------------------------------------------
# Columnas de la tabla
# ---------------------------------------------------------------------------
tabla = pd.DataFrame({
    "i":                range(1, len(x) + 1),
    "x (ciclo)":        x.astype(int),
    "f(x) = QD (Ah)":   np.round(fx, 6),
    "x²":              (x ** 2).astype(np.int64),
    "ln f(x)":          np.round(Y, 8),
    "x · ln f(x)":      np.round(x * Y, 8),
})

# ---------------------------------------------------------------------------
# Sumas
# ---------------------------------------------------------------------------
n       = len(x)
sum_x   = x.sum()
sum_Y   = Y.sum()
sum_x2  = (x ** 2).sum()
sum_xY  = (x * Y).sum()

totals = pd.DataFrame([{
    "i":                "Σ",
    "x (ciclo)":        int(sum_x),
    "f(x) = QD (Ah)":   round(fx.sum(), 6),    "x²":              int(sum_x2),    "ln f(x)":          round(sum_Y, 8),
    "x · ln f(x)":      round(sum_xY, 8),
}])

# ---------------------------------------------------------------------------
# Guardar CSV
# ---------------------------------------------------------------------------
tabla_completa = pd.concat([tabla, totals], ignore_index=True)
tabla_completa.to_csv("../data/tabla_sumas_exponencial.csv", index=False)
print("✓  data/tabla_sumas_exponencial.csv  generado\n")

# ---------------------------------------------------------------------------
# Mostrar por consola
# ---------------------------------------------------------------------------
COL_W   = [6, 12, 18, 14, 16, 18]
HEADERS = ["i", "x (ciclo)", "f(x) = QD (Ah)", "x²", "ln f(x)", "x · ln f(x)"]
SEP     = "  ".join("-" * w for w in COL_W)

def fmt_row(vals):
    return "  ".join(str(v).rjust(w) for v, w in zip(vals, COL_W))

print(fmt_row(HEADERS))
print(SEP)
for _, row in tabla.head(8).iterrows():
    print(fmt_row(row.tolist()))
print("  ".join(("  ·" * 5).split("·")[:5]).replace("·", "···"))
for _, row in tabla.tail(5).iterrows():
    print(fmt_row(row.tolist()))
print(SEP)
print(fmt_row(totals.iloc[0].tolist()))

# ---------------------------------------------------------------------------
# Resumen de sumas
# ---------------------------------------------------------------------------
print(f"""
════════════════════════════════════════════════════════════
Sumas para el sistema de ecuaciones normales
════════════════════════════════════════════════════════════
  n              = {n}
  Σ x            = {sum_x:,.0f}
  Σ ln f(x)      = {sum_Y:.6f}
  Σ x²           = {sum_x2:,.0f}
  Σ x · ln f(x)  = {sum_xY:.6f}
════════════════════════════════════════════════════════════
""")

# ---------------------------------------------------------------------------
# Sistema de ecuaciones normales con valores
# ---------------------------------------------------------------------------
print("Sistema de ecuaciones normales:")
print(f"  {n}·b₀  +  {sum_x:,.0f}·b₁  =  {sum_Y:.6f}       (1)")
print(f"  {sum_x:,.0f}·b₀  +  {sum_x2:,.0f}·b₁  =  {sum_xY:.6f}  (2)")

# ---------------------------------------------------------------------------
# Resolución: Cramer 2×2
# ---------------------------------------------------------------------------
det   = n * sum_x2 - sum_x ** 2
det_b1 = n * sum_xY - sum_x * sum_Y
det_b0 = sum_Y * sum_x2 - sum_xY * sum_x

b1 = det_b1 / det
b0 = (sum_Y - b1 * sum_x) / n
A  = np.exp(b0)

print(f"""
════════════════════════════════════════════════════════════
Resolución — Regla de Cramer sobre el sistema 2×2
════════════════════════════════════════════════════════════

┌─ Determinante principal ──────────────────────────────────┐
│                                                           │
│  det(A) = n·Σx²  −  (Σx)²                               │
│         = {n}·{sum_x2:,.0f}  −  ({sum_x:,.0f})²          │
│         = {det:,.0f}                                      │
└───────────────────────────────────────────────────────────┘

┌─ Coeficiente b₁ = β ──────────────────────────────────────┐
│                                                           │
│       n·Σx·ln f(x)  −  Σx·Σln f(x)                      │
│  b₁ = ─────────────────────────────                       │
│                  det(A)                                   │
│                                                           │
│     = {n}·({sum_xY:.6f})  −  {sum_x:,.0f}·({sum_Y:.6f})  │
│       ─────────────────────────────────────────────────── │
│                    {det:,.0f}                             │
│                                                           │
│     = {det_b1:.6f} / {det:,.0f}                           │
│     = {b1:.10e}                                           │
└───────────────────────────────────────────────────────────┘

┌─ Coeficiente b₀ → A ──────────────────────────────────────┐
│                                                           │
│       Σln f(x)  −  b₁·Σx                                 │
│  b₀ = ─────────────────────                               │
│               n                                           │
│                                                           │
│     = ({sum_Y:.6f}  −  ({b1:.6e})·{sum_x:,.0f}) / {n}    │
│     = {b0:.10f}                                           │
│                                                           │
│  A  = e^b₀  =  e^({b0:.6f})  =  {A:.10f}                 │
└───────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════
Solución
════════════════════════════════════════════════════════════
  β  = b₁ = {b1:.10e}
  A  = e^b₀ = {A:.10f}

  QD(n) = {A:.6f} · e^({b1:.6e}·n)

  Estimación ciclo 1300:
  QD(1300) = {A * np.exp(b1 * 1300):.6f} Ah
════════════════════════════════════════════════════════════
""")
