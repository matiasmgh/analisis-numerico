"""
Muestra reducida — 15 puntos equidistantes de la fase de degradación
=====================================================================
Genera todos los archivos necesarios para el análisis con muestra reducida:

  data/muestra.csv                        — 15 puntos seleccionados
  data/tabla_sumas_lineal_muestra.csv     — tabla de sumas modelo lineal
  data/tabla_sumas_cuadratica_muestra.csv — tabla de sumas modelo cuadrático
  data/tabla_sumas_exponencial_muestra.csv— tabla de sumas modelo exponencial
  graphs/scatter_muestra.svg/png          — nube de puntos reducida
  graphs/recta_muestra.svg/png            — ajuste lineal
  graphs/parabola_muestra.svg/png         — ajuste cuadrático
  graphs/exponencial_muestra.svg/png      — ajuste exponencial
  graphs/comparacion_muestra.svg/png      — los tres modelos superpuestos
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Estilo Matplotlib
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.grid": True, "grid.color": "#cccccc",
    "grid.linewidth": 0.5, "grid.alpha": 0.6,
    "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 11, "axes.labelsize": 12, "axes.titlesize": 13,
    "xtick.labelsize": 10, "ytick.labelsize": 10,
    "legend.fontsize": 10, "legend.framealpha": 0.9, "legend.edgecolor": "#cccccc",
    "lines.linewidth": 1.4,
})

# ---------------------------------------------------------------------------
# Carga y filtro — idéntico al script principal
# ---------------------------------------------------------------------------
df = pd.read_csv("../data/dataset.csv")
sample = df[df["battery_id"] == df["battery_id"].iloc[0]].sort_values("cycle")
q_low  = sample["QD"].quantile(0.01)
q_high = sample["QD"].quantile(0.99)
sample = sample[(sample["QD"] >= q_low) & (sample["QD"] <= q_high)]
peak_cycle = sample["cycle"][sample["QD"].idxmax()]
deg = sample[sample["cycle"] >= peak_cycle].reset_index(drop=True)
battery_id = df["battery_id"].iloc[0]

x_all = deg["cycle"].values.astype(float)
y_all = deg["QD"].values

# ---------------------------------------------------------------------------
# Selección de 15 puntos equidistantes (datos reales del dataset)
# ---------------------------------------------------------------------------
N_PUNTOS = 15
targets  = np.linspace(x_all.min(), x_all.max(), N_PUNTOS)
indices  = [int(np.argmin(np.abs(x_all - t))) for t in targets]
indices  = sorted(set(indices))

x = x_all[indices]
y = y_all[indices]
n = len(x)

print(f"Batería   : {battery_id}")
print(f"Fase degrad.: ciclos {x_all.min():.0f}–{x_all.max():.0f}  ({len(x_all)} puntos totales)")
print(f"Muestra   : {n} puntos equidistantes\n")
print(f"{'i':>4}  {'ciclo':>7}  {'QD (Ah)':>12}")
print("  " + "-" * 28)
for i, (xi, yi) in enumerate(zip(x, y), 1):
    print(f"  {i:2d}  {xi:7.0f}  {yi:12.6f}")

# ---------------------------------------------------------------------------
# Guardar muestra
# ---------------------------------------------------------------------------
muestra_df = pd.DataFrame({"i": range(1, n+1),
                            "ciclo": x.astype(int),
                            "QD (Ah)": np.round(y, 6)})
muestra_df.to_csv("../data/muestra.csv", index=False)
print("\n✓  data/muestra.csv")

# ---------------------------------------------------------------------------
# Sumas comunes a los tres modelos
# ---------------------------------------------------------------------------
sx   = x.sum()
sy   = y.sum()
sx2  = (x**2).sum()
sxy  = (x * y).sum()
sx3  = (x**3).sum()
sx4  = (x**4).sum()
sx2y = (x**2 * y).sum()
Y    = np.log(y)
sY   = Y.sum()
sxY  = (x * Y).sum()

# ---------------------------------------------------------------------------
# MODELO 1 — Recta de mínimos cuadrados
# ---------------------------------------------------------------------------
det_l = n*sx2 - sx**2
a_l   = (n*sxy  - sx*sy)  / det_l
b_l   = (sy - a_l*sx) / n

print(f"\n{'='*60}")
print("MODELO 1 — Lineal")
print(f"{'='*60}")
print(f"  n   = {n}")
print(f"  Σx  = {sx:.0f}")
print(f"  Σy  = {sy:.6f}")
print(f"  Σx² = {sx2:.0f}")
print(f"  Σxy = {sxy:.6f}")
print(f"  det = n·Σx² − (Σx)² = {n}·{sx2:.0f} − {sx:.0f}² = {det_l:.0f}")
print(f"  a   = {a_l:.10e}")
print(f"  b   = {b_l:.10f}")
print(f"  QD(1300) = {a_l*1300 + b_l:.6f} Ah")

# Tabla de sumas lineal
t_lin = pd.DataFrame({
    "i":             range(1, n+1),
    "x (ciclo)":     x.astype(int),
    "f(x) = QD (Ah)":np.round(y, 6),
    "x²":            (x**2).astype(np.int64),
    "x · f(x)":      np.round(x*y, 6),
})
tot_lin = pd.DataFrame([{"i": "Σ", "x (ciclo)": int(sx),
                          "f(x) = QD (Ah)": round(sy, 6),
                          "x²": int(sx2), "x · f(x)": round(sxy, 6)}])
pd.concat([t_lin, tot_lin]).to_csv("../data/tabla_sumas_lineal_muestra.csv", index=False)
print("✓  data/tabla_sumas_lineal_muestra.csv")

# ---------------------------------------------------------------------------
# MODELO 2 — Parábola de mínimos cuadrados
# ---------------------------------------------------------------------------
alpha  = n*sx3  - sx2*sx
beta   = n*sx2  - sx**2          # = det_l
gamma  = n*sxy  - sy*sx
alphap = n*sx4  - sx2**2
gammap = n*sx2y - sy*sx2
det2   = alpha**2 - alphap*beta
det_a  = gamma*alpha  - gammap*beta
det_b  = alpha*gammap - alphap*gamma
a_q    = det_a / det2
b_q    = det_b / det2
c_q    = (sy - a_q*sx2 - b_q*sx) / n

print(f"\n{'='*60}")
print("MODELO 2 — Cuadrático")
print(f"{'='*60}")
print(f"  Σx³  = {sx3:.0f}")
print(f"  Σx⁴  = {sx4:.0f}")
print(f"  Σx²y = {sx2y:.6f}")
print(f"  α  = n·Σx³ − Σx²·Σx  = {alpha:.0f}")
print(f"  β  = n·Σx² − (Σx)²   = {beta:.0f}  (= det lineal)")
print(f"  γ  = n·Σxy − Σy·Σx   = {gamma:.6f}")
print(f"  α' = n·Σx⁴ − (Σx²)²  = {alphap:.0f}")
print(f"  γ' = n·Σx²y − Σy·Σx² = {gammap:.6f}")
print(f"  det(A₂) = α² − α'·β  = {det2:.6e}")
print(f"  det(Aₐ) = γ·α − γ'·β = {det_a:.6e}")
print(f"  det(A_b)= α·γ' − α'·γ= {det_b:.6e}")
print(f"  a = {a_q:.10e}")
print(f"  b = {b_q:.10e}")
print(f"  c = {c_q:.10f}")
print(f"  QD(1300) = {a_q*1300**2 + b_q*1300 + c_q:.6f} Ah")

# Tabla de sumas cuadrática
t_cuad = pd.DataFrame({
    "i":              range(1, n+1),
    "x (ciclo)":      x.astype(int),
    "f(x) = QD (Ah)": np.round(y, 6),
    "x²":             (x**2).astype(np.int64),
    "x³":             (x**3).astype(np.int64),
    "x⁴":             (x**4).astype(np.int64),
    "x · f(x)":       np.round(x*y, 6),
    "x² · f(x)":      np.round(x**2*y, 6),
})
tot_cuad = pd.DataFrame([{
    "i": "Σ", "x (ciclo)": int(sx), "f(x) = QD (Ah)": round(sy, 6),
    "x²": int(sx2), "x³": int(sx3), "x⁴": int(sx4),
    "x · f(x)": round(sxy, 6), "x² · f(x)": round(sx2y, 6),
}])
pd.concat([t_cuad, tot_cuad]).to_csv("../data/tabla_sumas_cuadratica_muestra.csv", index=False)
print("✓  data/tabla_sumas_cuadratica_muestra.csv")

# ---------------------------------------------------------------------------
# MODELO 3 — Exponencial de mínimos cuadrados
# ---------------------------------------------------------------------------
det_e = n*sx2  - sx**2           # = det_l = beta
b1_e  = (n*sxY - sx*sY)  / det_e
b0_e  = (sY - b1_e*sx) / n
A_e   = np.exp(b0_e)
beta_e = b1_e

print(f"\n{'='*60}")
print("MODELO 3 — Exponencial")
print(f"{'='*60}")
print(f"  ΣlnY = {sY:.6f}")
print(f"  ΣxlnY= {sxY:.6f}")
print(f"  det  = {det_e:.0f}  (= det lineal)")
print(f"  b0   = {b0_e:.10f}  →  A = {A_e:.10f}")
print(f"  β    = {beta_e:.10e}")
print(f"  QD(1300) = {A_e*np.exp(beta_e*1300):.6f} Ah")

# Tabla de sumas exponencial
t_exp = pd.DataFrame({
    "i":                range(1, n+1),
    "x (ciclo)":        x.astype(int),
    "f(x) = QD (Ah)":   np.round(y, 6),
    "x²":               (x**2).astype(np.int64),
    "ln f(x)":          np.round(Y, 8),
    "x · ln f(x)":      np.round(x*Y, 8),
})
tot_exp = pd.DataFrame([{
    "i": "Σ", "x (ciclo)": int(sx), "f(x) = QD (Ah)": round(sy, 6),
    "x²": int(sx2), "ln f(x)": round(sY, 8), "x · ln f(x)": round(sxY, 8),
}])
pd.concat([t_exp, tot_exp]).to_csv("../data/tabla_sumas_exponencial_muestra.csv", index=False)
print("✓  data/tabla_sumas_exponencial_muestra.csv")

# ---------------------------------------------------------------------------
# R² sobre los 15 puntos
# ---------------------------------------------------------------------------
def r2(yt, yp):
    return 1 - np.sum((yt-yp)**2)/np.sum((yt-yt.mean())**2)

r2_l = r2(y, a_l*x + b_l)
r2_q = r2(y, a_q*x**2 + b_q*x + c_q)
r2_e = r2(y, A_e*np.exp(beta_e*x))
print(f"\n{'='*60}")
print("R² sobre la muestra de 15 puntos")
print(f"{'='*60}")
print(f"  Lineal:      {r2_l:.8f}")
print(f"  Cuadrático:  {r2_q:.8f}")
print(f"  Exponencial: {r2_e:.8f}")

# ---------------------------------------------------------------------------
# Curvas de ajuste para los gráficos
# ---------------------------------------------------------------------------
n_fit  = np.linspace(x.min(), x.max(), 600)
fit_l  = a_l  * n_fit + b_l
fit_q  = a_q  * n_fit**2 + b_q*n_fit + c_q
fit_e  = A_e  * np.exp(beta_e * n_fit)

# ---------------------------------------------------------------------------
# Gráfico 1 — Nube de puntos de la muestra
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x, y, s=55, color="#2166ac", zorder=5,
           label="Muestra (15 puntos)", linewidths=0.5, edgecolors="#134e7a")
ax.set_xlabel("Ciclo de carga")
ax.set_ylabel("Capacidad de descarga — QD (Ah)")
ax.set_title(f"Muestra reducida: QD vs. ciclo  [{battery_id}]")
ax.legend()
fig.tight_layout()
fig.savefig("../graphs/scatter_muestra.svg", bbox_inches="tight")
fig.savefig("../graphs/scatter_muestra.png", dpi=300, bbox_inches="tight")
print("\n✓  graphs/scatter_muestra.svg/png")
plt.close()

# ---------------------------------------------------------------------------
# Gráfico 2 — Ajuste lineal
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x, y, s=55, color="#2166ac", zorder=5, linewidths=0.5,
           edgecolors="#134e7a", label="Muestra (15 puntos)")
ax.plot(n_fit, fit_l, color="#d73027", linewidth=1.6,
        label=f"Recta MC: $QD = {a_l:.4e}\\,n + {b_l:.5f}$")
ax.set_xlabel("Ciclo de carga"); ax.set_ylabel("Capacidad de descarga — QD (Ah)")
ax.set_title(f"Ajuste lineal — muestra reducida  [{battery_id}]")
ax.legend(); fig.tight_layout()
fig.savefig("../graphs/recta_muestra.svg", bbox_inches="tight")
fig.savefig("../graphs/recta_muestra.png", dpi=300, bbox_inches="tight")
print("✓  graphs/recta_muestra.svg/png")
plt.close()

# ---------------------------------------------------------------------------
# Gráfico 3 — Ajuste cuadrático
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x, y, s=55, color="#2166ac", zorder=5, linewidths=0.5,
           edgecolors="#134e7a", label="Muestra (15 puntos)")
ax.plot(n_fit, fit_q, color="#1a9641", linewidth=1.6,
        label=(f"Parábola MC:\n"
               f"$QD = {a_q:.3e}\\,n^2 + ({b_q:.3e})\\,n + {c_q:.5f}$"))
ax.set_xlabel("Ciclo de carga"); ax.set_ylabel("Capacidad de descarga — QD (Ah)")
ax.set_title(f"Ajuste cuadrático — muestra reducida  [{battery_id}]")
ax.legend(); fig.tight_layout()
fig.savefig("../graphs/parabola_muestra.svg", bbox_inches="tight")
fig.savefig("../graphs/parabola_muestra.png", dpi=300, bbox_inches="tight")
print("✓  graphs/parabola_muestra.svg/png")
plt.close()

# ---------------------------------------------------------------------------
# Gráfico 4 — Ajuste exponencial
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x, y, s=55, color="#2166ac", zorder=5, linewidths=0.5,
           edgecolors="#134e7a", label="Muestra (15 puntos)")
ax.plot(n_fit, fit_e, color="#7b2d8b", linewidth=1.6,
        label=(f"Exponencial MC:\n"
               f"$QD = {A_e:.6f}\\cdot e^{{({beta_e:.4e})\\,n}}$"))
ax.set_xlabel("Ciclo de carga"); ax.set_ylabel("Capacidad de descarga — QD (Ah)")
ax.set_title(f"Ajuste exponencial — muestra reducida  [{battery_id}]")
ax.legend(); fig.tight_layout()
fig.savefig("../graphs/exponencial_muestra.svg", bbox_inches="tight")
fig.savefig("../graphs/exponencial_muestra.png", dpi=300, bbox_inches="tight")
print("✓  graphs/exponencial_muestra.svg/png")
plt.close()

# ---------------------------------------------------------------------------
# Gráfico 5 — Comparación de los tres modelos
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.scatter(x, y, s=60, color="#2166ac", zorder=6, linewidths=0.5,
           edgecolors="#134e7a", label="Muestra (15 puntos)", alpha=0.9)
ax.plot(n_fit, fit_l, color="#d73027",  linewidth=1.5, linestyle="-",
        label=f"Lineal  ($R^2={r2_l:.4f}$)")
ax.plot(n_fit, fit_q, color="#1a9641",  linewidth=1.5, linestyle="--",
        label=f"Cuadrático  ($R^2={r2_q:.4f}$)")
ax.plot(n_fit, fit_e, color="#7b2d8b",  linewidth=1.5, linestyle=":",
        label=f"Exponencial  ($R^2={r2_e:.4f}$)")
ax.set_xlabel("Ciclo de carga"); ax.set_ylabel("Capacidad de descarga — QD (Ah)")
ax.set_title(f"Comparación de modelos — muestra reducida  [{battery_id}]")
ax.legend(); fig.tight_layout()
fig.savefig("../graphs/comparacion_muestra.svg", bbox_inches="tight")
fig.savefig("../graphs/comparacion_muestra.png", dpi=300, bbox_inches="tight")
print("✓  graphs/comparacion_muestra.svg/png")
plt.close()

print(f"\n{'='*60}")
print("Resumen de resultados")
print(f"{'='*60}")
print(f"  Lineal:      QD(n) = {a_l:.6e}·n + {b_l:.8f}")
print(f"               QD(1300) = {a_l*1300+b_l:.6f} Ah  |  R² = {r2_l:.6f}")
print(f"  Cuadrático:  QD(n) = {a_q:.6e}·n² + ({b_q:.6e})·n + {c_q:.8f}")
print(f"               QD(1300) = {a_q*1300**2+b_q*1300+c_q:.6f} Ah  |  R² = {r2_q:.6f}")
print(f"  Exponencial: QD(n) = {A_e:.8f}·e^({beta_e:.6e}·n)")
print(f"               QD(1300) = {A_e*np.exp(beta_e*1300):.6f} Ah  |  R² = {r2_e:.6f}")
