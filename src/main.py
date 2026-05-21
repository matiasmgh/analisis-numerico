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

