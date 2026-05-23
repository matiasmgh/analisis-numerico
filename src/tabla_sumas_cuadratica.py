"""
Tabla de sumas para el ajuste cuadrático por mínimos cuadrados
===============================================================
Sistema de ecuaciones normales (3×3):

    a·Σ(x⁴) + b·Σ(x³) + c·Σ(x²) = Σ(f(x)·x²)
    a·Σ(x³) + b·Σ(x²) + c·Σ(x)  = Σ(f(x)·x)
    a·Σ(x²) + b·Σ(x)  + c·n      = Σ(f(x))

Variables:
    x    = número de ciclo de carga
    f(x) = capacidad de descarga QD [Ah]
    n    = cantidad de puntos (fase de degradación, ciclos 53–1189)

Genera:
    - Tabla completa en  data/tabla_sumas_cuadratica.csv
    - Muestra por consola las primeras y últimas filas + totales
    - Imprime el sistema de ecuaciones con valores numéricos
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Carga y filtro — fase de degradación (igual que ajuste lineal)
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

# ---------------------------------------------------------------------------
# Columnas de la tabla
# ---------------------------------------------------------------------------
tabla = pd.DataFrame({
    "i":              range(1, len(x) + 1),
    "x":              x.astype(int),
    "f(x)":           np.round(fx, 6),
    "x²":             (x ** 2).astype(np.int64),
    "x³":             (x ** 3).astype(np.int64),
    "x⁴":             (x ** 4).astype(np.int64),
    "x·f(x)":         np.round(x * fx, 6),
    "x²·f(x)":        np.round(x**2 * fx, 4),
})

# ---------------------------------------------------------------------------
# Sumas
# ---------------------------------------------------------------------------
n       = len(x)
sum_x   = x.sum()
sum_fx  = fx.sum()
sum_x2  = (x ** 2).sum()
sum_x3  = (x ** 3).sum()
sum_x4  = (x ** 4).sum()
sum_xfx  = (x * fx).sum()
sum_x2fx = (x**2 * fx).sum()

totals = pd.DataFrame([{
    "i":       "Σ",
    "x":       int(sum_x),
    "f(x)":    round(sum_fx,  6),
    "x²":      int(sum_x2),
    "x³":      int(sum_x3),
    "x⁴":      int(sum_x4),
    "x·f(x)":  round(sum_xfx,  6),
    "x²·f(x)": round(sum_x2fx, 4),
}])

# ---------------------------------------------------------------------------
# Guardar CSV
# ---------------------------------------------------------------------------
tabla_completa = pd.concat([tabla, totals], ignore_index=True)
tabla_completa.to_csv("../data/tabla_sumas_cuadratica.csv", index=False)
print("✓  data/tabla_sumas_cuadratica.csv  generado\n")

# ---------------------------------------------------------------------------
# Mostrar primeras 6 + últimas 4 filas + totales
# ---------------------------------------------------------------------------
COL_W   = [5, 6, 10, 14, 18, 22, 14, 18]
HEADERS = ["i", "x", "f(x)", "x²", "x³", "x⁴", "x·f(x)", "x²·f(x)"]
SEP     = "  ".join("-" * w for w in COL_W)

def fmt_row(vals):
    return "  ".join(str(v).rjust(w) for v, w in zip(vals, COL_W))

print(fmt_row(HEADERS))
print(SEP)
for _, row in tabla.head(6).iterrows():
    print(fmt_row(row.tolist()))
print("  ".join("···".rjust(w) for w in COL_W))
for _, row in tabla.tail(4).iterrows():
    print(fmt_row(row.tolist()))
print(SEP)
print(fmt_row(totals.iloc[0].tolist()))

# ---------------------------------------------------------------------------
# Sistema de ecuaciones con valores numéricos
# ---------------------------------------------------------------------------
print(f"""
════════════════════════════════════════════════════════════
Sumas
════════════════════════════════════════════════════════════
  n          = {n}
  Σ x        = {sum_x:>25,.0f}
  Σ f(x)     = {sum_fx:>25.6f}
  Σ x²       = {sum_x2:>25,.0f}
  Σ x³       = {sum_x3:>25,.0f}
  Σ x⁴       = {sum_x4:>25,.0f}
  Σ x·f(x)   = {sum_xfx:>25.6f}
  Σ x²·f(x)  = {sum_x2fx:>25.6f}

════════════════════════════════════════════════════════════
Sistema de ecuaciones normales (valores exactos)
════════════════════════════════════════════════════════════
  {sum_x4}·a  +  {sum_x3}·b  +  {sum_x2}·c  =  {sum_x2fx:.6f}
  {sum_x3}·a  +  {sum_x2}·b  +  {int(sum_x)}·c  =  {sum_xfx:.6f}
  {sum_x2}·a  +  {int(sum_x)}·b  +  {n}·c  =  {sum_fx:.6f}
════════════════════════════════════════════════════════════
""")

# ---------------------------------------------------------------------------
# Resolución por reducción + Cramer 2×2 — paso a paso
# ---------------------------------------------------------------------------
print("\n════════════════════════════════════════════════════════════")
print("Resolución: reducción a sistema 2×2 + Regla de Cramer")
print("════════════════════════════════════════════════════════════")

# --- Paso 1: despejar c de la ecuación 3 ---
print("""
┌─ Paso 1 — Despejar c de la ecuación 3 ──────────────────┐
│                                                          │
│  Σx²·a + Σx·b + n·c = Σf(x)                            │
│                                                          │
│       Σf(x) - Σx²·a - Σx·b                              │
│  c =  ─────────────────────                              │
│                n                                         │
└──────────────────────────────────────────────────────────┘
""")

# --- Paso 2: sustituir c en ecuación 2, multiplicar por n ---
# a·[n·Σx³ - Σx²·Σx] + b·[n·Σx² - (Σx)²] = n·Σxf(x) - Σf(x)·Σx
alpha = n * sum_x3 - sum_x2 * sum_x
beta  = n * sum_x2 - sum_x  ** 2
gamma = n * sum_xfx - sum_fx * sum_x

print("┌─ Paso 2 — Sustituir c en ecuación 2 (× n) ─────────────┐")
print("│                                                          │")
print("│  a·[n·Σx³ - Σx²·Σx]  +  b·[n·Σx² - (Σx)²]            │")
print("│       = n·Σx·f(x) - Σf(x)·Σx                           │")
print("│                                                          │")
print("│  Definimos:                                              │")
print(f"│    α  = n·Σx³ - Σx²·Σx  = {n}·{int(sum_x3):,} - {int(sum_x2):,}·{int(sum_x):,}")
print(f"│       = {alpha:,.0f}")
print(f"│    β  = n·Σx² - (Σx)²   = {n}·{int(sum_x2):,} - ({int(sum_x):,})²")
print(f"│       = {beta:,.0f}")
print(f"│    γ  = n·Σxf(x) - Σf(x)·Σx  = {gamma:,.6f}")
print("│                                                          │")
print("│  → ecuación (A):  α·a + β·b = γ                        │")
print("└──────────────────────────────────────────────────────────┘\n")

# --- Paso 3: sustituir c en ecuación 1, multiplicar por n ---
# a·[n·Σx⁴ - (Σx²)²] + b·[n·Σx³ - Σx·Σx²] = n·Σx²f(x) - Σf(x)·Σx²
alpha2 = n * sum_x4 - sum_x2 ** 2   # coef. de a en ec. (B)
beta2  = alpha                        # = n·Σx³ - Σx·Σx²  (= α, por simetría)
gamma2 = n * sum_x2fx - sum_fx * sum_x2

print("┌─ Paso 3 — Sustituir c en ecuación 1 (× n) ─────────────┐")
print("│                                                          │")
print("│  a·[n·Σx⁴ - (Σx²)²]  +  b·[n·Σx³ - Σx·Σx²]           │")
print("│       = n·Σx²·f(x) - Σf(x)·Σx²                         │")
print("│                                                          │")
print("│  Definimos:                                              │")
print(f"│    α' = n·Σx⁴ - (Σx²)²  = {alpha2:.6e}")
print(f"│    β' = n·Σx³ - Σx·Σx²  = α = {beta2:,.0f}  (simetría)")
print(f"│    γ' = n·Σx²f(x) - Σf(x)·Σx²  = {gamma2:,.6f}")
print("│                                                          │")
print("│  → ecuación (B):  α'·a + α·b = γ'                      │")
print("└──────────────────────────────────────────────────────────┘\n")

# --- Paso 4: sistema 2×2 resultante ---
print("┌─ Paso 4 — Sistema 2×2 en a y b ────────────────────────┐")
print("│                                                          │")
print(f"│   {alpha:.4e}·a  +  {beta:.4e}·b  =  {gamma:.6f}   (A)")
print(f"│   {alpha2:.4e}·a  +  {beta2:.4e}·b  =  {gamma2:.6f}   (B)")
print("│                                                          │")
print("└──────────────────────────────────────────────────────────┘\n")

# --- Paso 5: Regla de Cramer 2×2 ---
det   = alpha * alpha - alpha2 * beta   # |α  β | = α² - α'·β
#                                         |α' α |
det_a = gamma * alpha - gamma2 * beta   # |γ  β |
#                                         |γ' α |
det_b = alpha * gamma2 - alpha2 * gamma # |α  γ |
#                                         |α' γ'|

a_coef = det_a / det
b_coef = det_b / det

print("┌─ Paso 5 — Regla de Cramer sobre el sistema 2×2 ────────┐")
print("│                                                          │")
print(f"│  det(A₂) = α² - α'·β                                   │")
print(f"│          = ({alpha:.4e})² - ({alpha2:.4e})·({beta:.4e})")
print(f"│          = {det:.6e}")
print("│                                                          │")
print(f"│  det(Aₐ) = γ·α - γ'·β  =  {det_a:.6e}")
print(f"│  det(A_b) = α·γ' - α'·γ =  {det_b:.6e}")
print("│                                                          │")
print(f"│  a = det(Aₐ) / det(A₂) = {a_coef:.10e}")
print(f"│  b = det(A_b) / det(A₂) = {b_coef:.10e}")
print("└──────────────────────────────────────────────────────────┘\n")

# --- Paso 6: recuperar c ---
c_coef = (sum_fx - a_coef * sum_x2 - b_coef * sum_x) / n

print("┌─ Paso 6 — Recuperar c ──────────────────────────────────┐")
print("│                                                          │")
print(f"│       Σf(x) - a·Σx² - b·Σx                             │")
print(f"│  c =  ─────────────────────                             │")
print(f"│                n                                         │")
print(f"│                                                          │")
print(f"│    = ({sum_fx:.6f} - ({a_coef:.6e})·{int(sum_x2):,}")
print(f"│        - ({b_coef:.6e})·{int(sum_x):,}) / {n}")
print(f"│    = {c_coef:.10f}")
print("└──────────────────────────────────────────────────────────┘")

print(f"""
════════════════════════════════════════════════════════════
Solución
════════════════════════════════════════════════════════════
  a = {a_coef:.10e}
  b = {b_coef:.10e}
  c = {c_coef:.10f}

  QD(n) = ({a_coef:.6e})·n²  +  ({b_coef:.6e})·n  +  {c_coef:.6f}

  Estimación ciclo 1300:
  QD(1300) = {a_coef*1300**2 + b_coef*1300 + c_coef:.6f} Ah
════════════════════════════════════════════════════════════
""")
