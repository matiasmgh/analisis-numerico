"""
Tabla de sumas para el ajuste lineal por mínimos cuadrados
===========================================================
Sistema de ecuaciones normales:

    a · Σ(x²) + b · Σ(x)  = Σ(x · f(x))
    a · Σ(x)  + b · n      = Σ(f(x))

Variables:
    x    = número de ciclo de carga
    f(x) = capacidad de descarga QD [Ah]
    n    = cantidad de puntos (fase de degradación, ciclos 53–1189)

Genera:
    - Tabla completa en  data/tabla_sumas_lineal.csv
    - Muestra por consola las primeras y últimas filas + totales
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Carga y filtro — fase de degradación
# ---------------------------------------------------------------------------
df = pd.read_csv("../data/dataset.csv")
b = df[df["battery_id"] == "b1c0"].sort_values("cycle")

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
    "i":       range(1, len(x) + 1),
    "x (ciclo)":      x.astype(int),
    "f(x) = QD (Ah)": np.round(fx, 6),
    "x²":             (x ** 2).astype(np.int64),
    "x · f(x)":       np.round(x * fx, 6),
})

# ---------------------------------------------------------------------------
# Totales
# ---------------------------------------------------------------------------
n       = len(x)
sum_x   = x.sum()
sum_fx  = fx.sum()
sum_x2  = (x ** 2).sum()
sum_xfx = (x * fx).sum()

totals = pd.DataFrame([{
    "i":              "Σ",
    "x (ciclo)":      int(sum_x),
    "f(x) = QD (Ah)": round(sum_fx, 6),
    "x²":             int(sum_x2),
    "x · f(x)":       round(sum_xfx, 6),
}])

# ---------------------------------------------------------------------------
# Guardar tabla completa con fila de totales al final
# ---------------------------------------------------------------------------
tabla_completa = pd.concat([tabla, totals], ignore_index=True)
tabla_completa.to_csv("../data/tabla_sumas_lineal.csv", index=False)
print("✓  data/tabla_sumas_lineal.csv  generado\n")

# ---------------------------------------------------------------------------
# Mostrar por consola: primeras 8 filas + separador + últimas 5 + totales
# ---------------------------------------------------------------------------
COL_W = [6, 12, 18, 16, 18]
HEADERS = ["i", "x (ciclo)", "f(x) = QD (Ah)", "x²", "x · f(x)"]
SEP = "  ".join("-" * w for w in COL_W)

def fmt_row(vals):
    parts = []
    for v, w in zip(vals, COL_W):
        parts.append(str(v).rjust(w))
    return "  ".join(parts)

print(fmt_row(HEADERS))
print(SEP)

for _, row in tabla.head(8).iterrows():
    print(fmt_row(row.tolist()))

print("  ".join(("  ·" * 5).split("·")[:5]).replace("·", "···"))  # ellipsis row

for _, row in tabla.tail(5).iterrows():
    print(fmt_row(row.tolist()))

print(SEP)
print(fmt_row(totals.iloc[0].tolist()))

# ---------------------------------------------------------------------------
# Resumen de valores para el sistema de ecuaciones normales
# ---------------------------------------------------------------------------
print(f"""
════════════════════════════════════════
Valores para el sistema de ecuaciones normales
════════════════════════════════════════
  n         = {n}
  Σ x       = {sum_x:,.0f}
  Σ f(x)    = {sum_fx:.6f}
  Σ x²      = {sum_x2:,.0f}
  Σ x·f(x)  = {sum_xfx:.6f}
════════════════════════════════════════
""")
