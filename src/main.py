"""
Nube de puntos + ajuste lineal por mínimos cuadrados
=====================================================
Fase 1 : nube de puntos completa (ciclos 2–1189)
Fase 2 : recta de mínimos cuadrados sobre la fase de degradación (ciclos 53–1189)

Exporta SVG (alta calidad para informes) y PNG (300 dpi) en /graphs.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Estilo Matplotlib
# ---------------------------------------------------------------------------
plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.color": "#cccccc",
        "grid.linewidth": 0.5,
        "grid.alpha": 0.6,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#cccccc",
        "lines.linewidth": 1.4,
    }
)

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
df = pd.read_csv("../data/dataset.csv")

# Una sola batería — 100 ciclos disponibles (ciclos 2–102)
battery_id = df["battery_id"].iloc[0]
sample = df[df["battery_id"] == battery_id].sort_values("cycle")

# Eliminar outliers evidentes (ciclo sin medir y error de medición)
q_low  = sample["QD"].quantile(0.01)
q_high = sample["QD"].quantile(0.99)
sample = sample[(sample["QD"] >= q_low) & (sample["QD"] <= q_high)]

x = sample["cycle"].values
y = sample["QD"].values

print(f"Batería : {battery_id}")
print(f"Ciclos  : {x.min():.0f} – {x.max():.0f}   ({len(x)} puntos)")
print(f"QD      : {y.min():.5f} – {y.max():.5f}  Ah")

# ---------------------------------------------------------------------------
# Nube de puntos
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))

ax.scatter(
    x, y,
    s=18, color="#2166ac", alpha=0.85, linewidths=0,
    label="Datos experimentales",
)

ax.set_xlabel("Ciclo de carga")
ax.set_ylabel("Capacidad de descarga — QD (Ah)")
ax.set_title(f"Degradación de batería: QD vs. ciclo de carga  [{battery_id}]")
ax.legend()
fig.tight_layout()

fig.savefig("../graphs/scatter.svg", bbox_inches="tight")
fig.savefig("../graphs/scatter.png", dpi=300, bbox_inches="tight")
print("\n✓  graphs/scatter.svg  +  scatter.png")

plt.show()

# ---------------------------------------------------------------------------
# Fase 2 — Recta de mínimos cuadrados (ciclos 53–1189)
# ---------------------------------------------------------------------------
peak_cycle = sample["cycle"][sample["QD"].idxmax()]
deg = sample[sample["cycle"] >= peak_cycle]

xd = deg["cycle"].values.astype(float)
yd = deg["QD"].values

n      = len(xd)
sum_x  = xd.sum()
sum_y  = yd.sum()
sum_x2 = (xd ** 2).sum()
sum_xy = (xd * yd).sum()

# Fórmulas despejadas del sistema de ecuaciones normales
a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
b = (sum_y - a * sum_x) / n

print(f"\nRecta de mínimos cuadrados:")
print(f"  a = {a:.6e}")
print(f"  b = {b:.6f}")
print(f"  QD(n) = {a:.6e} · n + {b:.6f}")
print(f"  Estimación ciclo 1300: QD = {a*1300 + b:.6f} Ah")

# Curva de la recta sobre todo el rango de la fase de degradación
n_fit  = np.linspace(xd.min(), xd.max(), 600)
qd_fit = a * n_fit + b

fig2, ax2 = plt.subplots(figsize=(8, 5))

ax2.scatter(
    xd, yd,
    s=18, color="#2166ac", alpha=0.55, linewidths=0,
    zorder=5, label="Datos experimentales (fase degradación)",
)
ax2.plot(
    n_fit, qd_fit,
    color="#d73027", linewidth=1.6,
    label=f"Recta MC:  $QD = {a:.4e}\\,n + {b:.5f}$",
)

ax2.set_xlabel("Ciclo de carga")
ax2.set_ylabel("Capacidad de descarga — QD (Ah)")
ax2.set_title(f"Ajuste lineal por mínimos cuadrados  [{battery_id}]")
ax2.legend()
fig2.tight_layout()

fig2.savefig("../graphs/recta_minimos_cuadrados.svg", bbox_inches="tight")
fig2.savefig("../graphs/recta_minimos_cuadrados.png", dpi=300, bbox_inches="tight")
print("✓  graphs/recta_minimos_cuadrados.svg  +  .png\n")

plt.show()

# ---------------------------------------------------------------------------
# Fase 3 — Parábola de mínimos cuadrados (coeficientes calculados manualmente)
# ---------------------------------------------------------------------------
# Coeficientes calculados por reducción 3×3 → 2×2 + Regla de Cramer (cálculo manual)
a_q = 5.2047e-9
b_q = -4.9391e-5
c_q = 1.08119

print(f"Parábola de mínimos cuadrados (valores computacionales):")
print(f"  a = {a_q:.10e}")
print(f"  b = {b_q:.10e}")
print(f"  c = {c_q:.10f}")
print(f"  QD(n) = {a_q:.6e}·n² + ({b_q:.6e})·n + {c_q:.6f}")
print(f"  Estimación ciclo 1300: QD = {a_q*1300**2 + b_q*1300 + c_q:.6f} Ah")

n_fit_q  = np.linspace(xd.min(), xd.max(), 600)
qd_fit_q = a_q * n_fit_q**2 + b_q * n_fit_q + c_q

fig3, ax3 = plt.subplots(figsize=(8, 5))

ax3.scatter(
    xd, yd,
    s=18, color="#2166ac", alpha=0.55, linewidths=0,
    zorder=5, label="Datos experimentales (fase degradación)",
)
ax3.plot(
    n_fit_q, qd_fit_q,
    color="#1a9641", linewidth=1.6,
    label=(
        f"Parábola MC:\n"
        f"$QD = {a_q:.4e}\\,n^2 + ({b_q:.4e})\\,n + {c_q:.5f}$"
    ),
)

ax3.set_xlabel("Ciclo de carga")
ax3.set_ylabel("Capacidad de descarga — QD (Ah)")
ax3.set_title(f"Ajuste cuadrático por mínimos cuadrados  [{battery_id}]")
ax3.legend()
fig3.tight_layout()

fig3.savefig("../graphs/parabola_minimos_cuadrados.svg", bbox_inches="tight")
fig3.savefig("../graphs/parabola_minimos_cuadrados.png", dpi=300, bbox_inches="tight")
print("✓  graphs/parabola_minimos_cuadrados.svg  +  .png\n")

plt.show()

# ---------------------------------------------------------------------------
# Fase 4 — Exponencial de mínimos cuadrados
# ---------------------------------------------------------------------------
# Linealización: Y = ln(QD), ajuste lineal sobre (n, Y), recuperar A=e^b0, beta=b1
Y_exp  = np.log(yd)
sum_Y  = Y_exp.sum()
sum_xY = (xd * Y_exp).sum()

det   = n * sum_x2 - sum_x ** 2
b1_e  = (n * sum_xY - sum_x * sum_Y) / det
b0_e  = (sum_Y - b1_e * sum_x) / n
A_e   = np.exp(b0_e)
beta  = b1_e

print(f"Exponencial de mínimos cuadrados:")
print(f"  b0 = {b0_e:.10f}  →  A = e^b0 = {A_e:.10f}")
print(f"  b1 = β = {beta:.10e}")
print(f"  QD(n) = {A_e:.6f} · e^({beta:.6e}·n)")
print(f"  Estimación ciclo 1300: QD = {A_e * np.exp(beta * 1300):.6f} Ah")

n_fit_e  = np.linspace(xd.min(), xd.max(), 600)
qd_fit_e = A_e * np.exp(beta * n_fit_e)

fig4, ax4 = plt.subplots(figsize=(8, 5))

ax4.scatter(
    xd, yd,
    s=18, color="#2166ac", alpha=0.55, linewidths=0,
    zorder=5, label="Datos experimentales (fase degradación)",
)
ax4.plot(
    n_fit_e, qd_fit_e,
    color="#7b2d8b", linewidth=1.6,
    label=(
        f"Exponencial MC:\n"
        f"$QD = {A_e:.6f}\\cdot e^{{({beta:.4e})\\,n}}$"
    ),
)

ax4.set_xlabel("Ciclo de carga")
ax4.set_ylabel("Capacidad de descarga — QD (Ah)")
ax4.set_title(f"Ajuste exponencial por mínimos cuadrados  [{battery_id}]")
ax4.legend()
fig4.tight_layout()

fig4.savefig("../graphs/exponencial_minimos_cuadrados.svg", bbox_inches="tight")
fig4.savefig("../graphs/exponencial_minimos_cuadrados.png", dpi=300, bbox_inches="tight")
print("✓  graphs/exponencial_minimos_cuadrados.svg  +  .png\n")

plt.show()

