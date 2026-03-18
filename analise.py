# -----------------------------
# Immportando bibliotecas
# -----------------------------

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import matplotlib.cm as cm
from bcb import sgs, currency
import matplotlib.dates as mdates

# -----------------------------
# Configurações de exibição
# -----------------------------
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 180)

# -----------------------------
# Paths / Pastas do projeto
# -----------------------------
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "cotacoes_ibrx11.xlsx"
CHARTS_DIR = PROJECT_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Lendo o arquivo de cotações
# -----------------------------
df = pd.read_excel(DATA_FILE)
print("\nDataFrame principal:")
print(df.to_string())

# -----------------------------
# Gráfico 1 — Boxplot dos pesos
# -----------------------------
plt.figure(figsize=(8, 6))

ax = plt.gca()
ax.spines["left"].set_visible(True)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)

sns.boxplot(y=df["Weight (%)"])
plt.title("")
plt.ylabel("Weight Distribution (%)")
plt.grid(False)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "boxplot_weight_distribution_all.png", dpi=200, bbox_inches="tight")
plt.show()
plt.close()

# -----------------------------
# Seleção da carteira
# -----------------------------
df_selecao_carteira = pd.read_excel(DATA_FILE, sheet_name=1)
print("\nSeleção da carteira:")
print(df_selecao_carteira.to_string())

# -----------------------------
# Contagem por setor
# -----------------------------
contagem_setor = (
    df_selecao_carteira
    .groupby("Sector")["Ticker"]
    .count()
    .sort_values(ascending=True)
)

print("\nContagem por setor:")
print(contagem_setor.to_string())

# -----------------------------
# Visualização de setores
# -----------------------------
fig, ax = plt.subplots(figsize=(12, 8))

ax.barh(contagem_setor.index, contagem_setor.values)

ax.set_title("", loc="left")
ax.xaxis.set_visible(False)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)

for i, value in enumerate(contagem_setor.values):
    ax.text(value, i, f" {value}", va="center")

plt.grid(False)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "setores_barh_contagem.png", dpi=200, bbox_inches="tight")
plt.show()
plt.close()

# -----------------------------
# Tratamento da coluna de Data
# -----------------------------
df_cotacoes = pd.read_excel(DATA_FILE, sheet_name="Cotacoes")
df_cotacoes["Data"] = pd.to_datetime(df_cotacoes["Data"])
df_cotacoes.set_index("Data", inplace=True)
df_cotacoes.sort_index(inplace=True)

print("\nCotações (head):")
print(df_cotacoes.head().to_string())

# -----------------------------
# Retornos simples diários
# -----------------------------
df_returns = df_cotacoes.pct_change()
df_returns = df_returns.iloc[1:, :]

print("\nRetornos diários (head):")
print(df_returns.head().to_string())

# -----------------------------
# Carteira Top 20
# -----------------------------
pesos_series = (
    df_selecao_carteira
    .set_index("Ticker")["Percentual proporcionalizando pra 100"]
)

pesos_series = pesos_series / 100
normalized_weights = pesos_series / pesos_series.sum()

missing_cols = [col for col in normalized_weights.index if col not in df_returns.columns]
if missing_cols:
    raise ValueError(f"As seguintes colunas não estão em df_returns: {missing_cols}")

returns_carteira_components = df_returns[normalized_weights.index]
df_returns["Carteira_20"] = returns_carteira_components.dot(normalized_weights)

print("\nRetorno da Carteira (head):")
print(df_returns[["Carteira_20"]].head().to_string())

# -----------------------------
# Carteira Top 10
# -----------------------------
col_peso = "Percentual proporcionalizando pra 100"
n = 10

w10 = (
    df_selecao_carteira
    .sort_values(col_peso, ascending=False)
    .head(n)
    .set_index("Ticker")[col_peso]
    .div(100)
)
w10 = w10 / w10.sum()

df_carteira_10 = (
    w10.mul(100)
      .rename("Peso (%)")
      .reset_index()
      .sort_values("Peso (%)", ascending=False)
)

df_returns["Carteira_10"] = df_returns[w10.index].dot(w10)

print("\nCarteira 10:")
print(df_carteira_10.to_string(index=False))

# -----------------------------
# Carteira Top 5
# -----------------------------
n = 5

w5 = (
    df_selecao_carteira
    .sort_values(col_peso, ascending=False)
    .head(n)
    .set_index("Ticker")[col_peso]
    .div(100)
)
w5 = w5 / w5.sum()

df_carteira_5 = (
    w5.mul(100)
      .rename("Peso (%)")
      .reset_index()
      .sort_values("Peso (%)", ascending=False)
)

df_returns["Carteira_5"] = df_returns[w5.index].dot(w5)

print("\nCarteira 5:")
print(df_carteira_5.to_string(index=False))

# -----------------------------
# Checando os dados das carteiras geradas
# -----------------------------
print("\nChecagens:")
print("Soma coluna % (df_selecao_carteira):",
      df_selecao_carteira["Percentual proporcionalizando pra 100"].sum())
print("Soma normalized_weights:", normalized_weights.sum())
print("Soma w10:", w10.sum())
print("Soma w5:", w5.sum())
print(df_returns[["Carteira_20", "Carteira_10", "Carteira_5"]].isnull().sum().to_string())

# -----------------------------
# Boxplots — pesos carteiras 20/10/5
# -----------------------------
pesos_carteira20 = df_selecao_carteira["Percentual proporcionalizando pra 100"]
pesos_carteira10 = df_carteira_10["Peso (%)"]
pesos_carteira5 = df_carteira_5["Peso (%)"]

fig, axes = plt.subplots(1, 3, figsize=(15, 6))

sns.boxplot(y=pesos_carteira20, ax=axes[0])
axes[0].set_title("Carteira 20")
axes[0].set_ylabel("Weight Distribution (%)")

sns.boxplot(y=pesos_carteira10, ax=axes[1])
axes[1].set_title("Carteira 10")
axes[1].set_ylabel("")

sns.boxplot(y=pesos_carteira5, ax=axes[2])
axes[2].set_title("Carteira 5")
axes[2].set_ylabel("")

plt.suptitle("", fontsize=14)
plt.grid(False)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "boxplot_weights_20_10_5.png", dpi=200, bbox_inches="tight")
plt.show()
plt.close()

# -----------------------------
# Cálculo de retorno e risco anuais
# -----------------------------
trading_days = 252

annual_returns = (1 + df_returns).prod() ** (trading_days / len(df_returns)) - 1
annual_std = df_returns.std(ddof=1) * np.sqrt(trading_days)

df_annual = pd.DataFrame({
    "Retorno_Anual": annual_returns,
    "Vol_Anual": annual_std
})

print("\nRetorno e risco anuais:")
print(df_annual.to_string())

# -----------------------------
# Selic diária anualizada
# -----------------------------
cdi_annual = sgs.get(
    {"selic": 432},
    start=df_returns.index.min(),
    end=df_returns.index.max()
)["selic"]

cdi_rate_daily = (1 + cdi_annual / 100) ** (1 / trading_days) - 1
cdi_daily_series = cdi_rate_daily.reindex(df_returns.index).ffill()
cdi_daily_series.name = "CDI_SGS_daily"

cdi_cumulative_series = (1 + cdi_daily_series).cumprod() - 1
risk_free_daily = cdi_daily_series

# -----------------------------
# Rentabilidade acumulada
# -----------------------------
cols_plot = ["Carteira_20", "Carteira_10", "Carteira_5", "BRAX11"]
cols_plot = [c for c in cols_plot if c in df_returns.columns]

label_map = {
    "Carteira_20": "Portfolio 20",
    "Carteira_10": "Portfolio 10",
    "Carteira_5": "Portfolio 5",
    "BRAX11": "BRAX11"
}

cumulative_returns = (1 + df_returns[cols_plot]).cumprod() - 1
cdi_cum = cdi_cumulative_series

fig, ax = plt.subplots(figsize=(12, 8))

last_date = cumulative_returns.index[-1]

for col in cols_plot:
    series = cumulative_returns[col]
    label = label_map.get(col, col)

    ax.plot(series.index, series, linewidth=2, label=label)

    final_value = series.iloc[-1]
    ax.text(last_date, final_value, f"  {final_value:.1%}", va="center")

ax.plot(cdi_cum.index, cdi_cum, linestyle="--", linewidth=2, label="SELIC")

final_cdi = cdi_cum.iloc[-1]
ax.text(cdi_cum.index[-1], final_cdi, f"  {final_cdi:.1%}", va="center")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_xlim(left=cumulative_returns.index.min())
ax.set_ylabel("Accumulated Return", fontsize=13)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

ax.grid(False)
ax.legend(frameon=False)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "cumulative_returns_vs_selic.png", dpi=200, bbox_inches="tight")
plt.show()
plt.close()

# -----------------------------
# Métricas: Beta, Sharpe, Treynor, Sortino
# -----------------------------
rf_daily_series = risk_free_daily.reindex(df_returns.index).ffill()

market_col = "BRAX11"
if market_col not in df_returns.columns:
    raise ValueError(f"A coluna '{market_col}' não foi encontrada em df_returns.")

market_returns = df_returns[market_col]

cov_with_market = df_returns.apply(lambda col: col.cov(market_returns))
var_market = market_returns.var()
beta_values = cov_with_market / var_market

excess_daily = df_returns.sub(rf_daily_series, axis=0)

excess_mean_daily = excess_daily.mean()
excess_std_daily = excess_daily.std(ddof=1)

sharpe_ratio = (excess_mean_daily / excess_std_daily) * np.sqrt(trading_days)
sharpe_ratio = sharpe_ratio.replace([np.inf, -np.inf], np.nan)

excess_mean_annual = excess_mean_daily * trading_days

treynor_index = excess_mean_annual / beta_values
treynor_index = treynor_index.replace([np.inf, -np.inf], np.nan)

def downside_deviation_annual_from_excess(excess_returns_series, trading_days=252):
    neg = excess_returns_series[excess_returns_series < 0]
    if len(neg) == 0:
        return np.nan
    return neg.std(ddof=1) * np.sqrt(trading_days)

downside_std_annual = excess_daily.apply(
    lambda col: downside_deviation_annual_from_excess(col, trading_days)
)

sortino_index = excess_mean_annual / downside_std_annual
sortino_index = sortino_index.replace([np.inf, -np.inf], np.nan)

metrics_df = pd.DataFrame({
    "Retorno_Anual": annual_returns,
    "Vol_Anual": annual_std,
    "Beta_BRAX11": beta_values,
    "Sharpe": sharpe_ratio,
    "Treynor": treynor_index,
    "Sortino": sortino_index
})

print("\nMetrics DF:")
print(metrics_df.to_string())

# -----------------------------
# Foco nas métricas da Carteira e do BRAX11
# -----------------------------
ativos_focus = ["Carteira_20", "Carteira_10", "Carteira_5", "BRAX11"]
ativos_focus = [a for a in ativos_focus if a in metrics_df.index]

metrics_focus = metrics_df.loc[ativos_focus]

print("\nMetrics Focus:")
print(metrics_focus.to_string())

# -----------------------------
# Scatter: retorno vs vol (cor = Sharpe)
# -----------------------------
fig, ax = plt.subplots(figsize=(12, 8))

scatter = ax.scatter(
    metrics_df["Vol_Anual"],
    metrics_df["Retorno_Anual"],
    c=metrics_df["Sharpe"],
    cmap="Blues",
    s=90,
    alpha=0.9,
    edgecolor="white",
    linewidth=0.8,
    zorder=3
)

cbar = plt.colorbar(scatter, pad=0.02)
cbar.set_label("Sharpe Ratio", fontsize=11)
cbar.outline.set_visible(False)

destaques = ["Carteira_20", "Carteira_10", "Carteira_5", "BRAX11"]
mask = metrics_df.index.isin(destaques)

ax.scatter(
    metrics_df.loc[mask, "Vol_Anual"],
    metrics_df.loc[mask, "Retorno_Anual"],
    s=260,
    facecolors="none",
    edgecolors="black",
    linewidths=1.2,
    alpha=0.65,
    zorder=4
)

for i, ticker in enumerate(metrics_df.index):
    x = metrics_df.loc[ticker, "Vol_Anual"]
    y = metrics_df.loc[ticker, "Retorno_Anual"]

    offset = 0.002 if i % 2 == 0 else -0.002

    ax.text(
        x + 0.0025,
        y + offset,
        ticker,
        fontsize=10,
        alpha=0.85
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.8)
ax.spines["bottom"].set_linewidth(0.8)

ax.set_xlabel("Annual Volatility", fontsize=13)
ax.set_ylabel("Annual Return", fontsize=13)

ax.tick_params(axis="both", labelsize=11)
ax.grid(alpha=0.15)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "scatter_return_vol_sharpe.png", dpi=200, bbox_inches="tight")
plt.show()
plt.close()

# -----------------------------
# Gráfico de barras – Sharpe, Treynor, Sortino
# -----------------------------
indices_to_plot = ["Sharpe", "Treynor", "Sortino"]
metrics_plot = metrics_focus[indices_to_plot].T

metrics_plot.columns = ["Portfolio 20", "Portfolio 10", "Portfolio 5", "BRAX11"]

fig, ax = plt.subplots(figsize=(12, 8))

num_series = metrics_plot.shape[1]
cmap = cm.get_cmap("Blues")
colors = [cmap(0.35 + i * (0.5 / (num_series - 1))) for i in range(num_series)]

bars = metrics_plot.plot(
    kind="bar",
    ax=ax,
    width=0.75,
    fontsize=14,
    color=colors,
    edgecolor="white"
)

ax.spines["left"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(True)

ax.yaxis.set_visible(False)

for container in bars.containers:
    ax.bar_label(
        container,
        fmt="%.3f",
        padding=4,
        fontsize=12,
        weight="bold"
    )

ax.legend(
    title="",
    fontsize=12,
    loc="upper left",
    bbox_to_anchor=(0, 1.10),
    frameon=False
)

ax.text(
    0, 1.18,
    "",
    fontsize=18,
    fontweight="bold",
    ha="left",
    transform=ax.transAxes
)

plt.xlabel("")
plt.xticks(rotation=0, fontsize=14, weight="bold")
plt.grid(False)

plt.tight_layout()
plt.savefig(CHARTS_DIR / "bars_sharpe_treynor_sortino.png", dpi=200, bbox_inches="tight")
plt.show()
plt.close()

# ======================================================
# TESTE DE SIGNIFICÂNCIA: DIFERENÇA DE SHARPE
# CIRCULAR BLOCK BOOTSTRAP
# H0: SR_Portfolio = SR_BRAX11
# ======================================================

def _circular_block_bootstrap_indices(n, block_size, rng):
    idx = np.empty(n, dtype=int)
    pos = 0
    while pos < n:
        start = rng.integers(0, n)
        block = (start + np.arange(block_size)) % n
        take = min(block_size, n - pos)
        idx[pos:pos+take] = block[:take]
        pos += take
    return idx

def sharpe_ratio_calc(excess_returns, days=252):
    x = np.asarray(excess_returns, dtype=float)
    std = np.std(x, ddof=1)
    if std == 0 or np.isnan(std):
        return 0.0
    return (np.mean(x) / std) * np.sqrt(days)

def run_sharpe_test(r_port, r_bench, rf_daily_series, n_boot=20000, block_size=10, days=252, seed=42):
    df_temp = pd.concat([r_port, r_bench, rf_daily_series], axis=1).dropna()
    df_temp.columns = ["port", "bench", "rf"]

    ex_p = df_temp["port"] - df_temp["rf"]
    ex_b = df_temp["bench"] - df_temp["rf"]

    sr_p = sharpe_ratio_calc(ex_p.values, days)
    sr_b = sharpe_ratio_calc(ex_b.values, days)
    delta_obs = sr_p - sr_b

    d = ex_p - ex_b
    ex_p_h0 = ex_b + (d - d.mean())

    rng = np.random.default_rng(seed)
    deltas_star = np.empty(n_boot, dtype=float)
    n = len(df_temp)

    for i in range(n_boot):
        idx = _circular_block_bootstrap_indices(n, block_size, rng)
        sr_p_star = sharpe_ratio_calc(ex_p_h0.values[idx], days)
        sr_b_star = sharpe_ratio_calc(ex_b.values[idx], days)
        deltas_star[i] = sr_p_star - sr_b_star

    p_value = np.mean(np.abs(deltas_star) >= np.abs(delta_obs))
    return sr_p, sr_b, delta_obs, p_value

# -----------------------------
# Teste principal
# -----------------------------
portfolio_cols = ["Carteira_20", "Carteira_10", "Carteira_5"]
benchmark_col = "BRAX11"

results = []
for p in portfolio_cols:
    sp, sb, diff, pval = run_sharpe_test(
        df_returns[p],
        df_returns[benchmark_col],
        rf_daily_series=risk_free_daily,
        n_boot=20000,
        block_size=10,
        days=trading_days,
        seed=42
    )
    results.append({
        "Portfolio": p,
        "SR_Portfolio": sp,
        "SR_Bench": sb,
        "Delta_SR": diff,
        "p_value": pval
    })

df_test_results = pd.DataFrame(results)
print("\nTeste principal — diferença de Sharpe:")
print(df_test_results.to_string(index=False))

# -----------------------------
# ROBUSTEZ: Sensibilidade ao tamanho do bloco
# -----------------------------
block_sizes = [5, 10, 20]

robust_b = []
for p in portfolio_cols:
    for b in block_sizes:
        sp, sb, diff, pval = run_sharpe_test(
            df_returns[p],
            df_returns[benchmark_col],
            rf_daily_series=risk_free_daily,
            n_boot=20000,
            block_size=b,
            days=trading_days,
            seed=42
        )
        robust_b.append({
            "Portfolio": p,
            "b": b,
            "SR_Portfolio": sp,
            "SR_Bench": sb,
            "Delta_SR": diff,
            "p_value": pval
        })

df_robust_b = pd.DataFrame(robust_b).sort_values(["Portfolio", "b"]).reset_index(drop=True)
print("\nRobustez — block size:")
print(df_robust_b.to_string(index=False))

# -----------------------------
# ROBUSTEZ: CDI constante de 8% a.a.
# -----------------------------
CDI_ANUAL_8 = 0.08
trading_days = 252

rf_daily_8 = (1 + CDI_ANUAL_8) ** (1 / trading_days) - 1
risk_free_daily_8 = pd.Series(rf_daily_8, index=df_returns.index, name="CDI_8_daily")

results_cdi8 = []
for p in portfolio_cols:
    sp, sb, diff, pval = run_sharpe_test(
        df_returns[p],
        df_returns[benchmark_col],
        rf_daily_series=risk_free_daily_8,
        n_boot=20000,
        block_size=10,
        days=trading_days,
        seed=42
    )
    results_cdi8.append({
        "Portfolio": p,
        "SR_Portfolio": sp,
        "SR_Bench": sb,
        "Delta_SR": diff,
        "p_value": pval
    })

df_test_results_cdi8 = pd.DataFrame(results_cdi8)
print("\nTeste principal — CDI 8% a.a.:")
print(df_test_results_cdi8.to_string(index=False))

# -----------------------------
# Robustez conjunta: CDI 8% e b ∈ {5,10,20}
# -----------------------------
block_sizes = [5, 10, 20]
robust_cdi8 = []

for p in portfolio_cols:
    for b in block_sizes:
        sp, sb, diff, pval = run_sharpe_test(
            df_returns[p],
            df_returns[benchmark_col],
            rf_daily_series=risk_free_daily_8,
            n_boot=20000,
            block_size=b,
            days=trading_days,
            seed=42
        )
        robust_cdi8.append({
            "Portfolio": p,
            "b": b,
            "SR_Portfolio": sp,
            "SR_Bench": sb,
            "Delta_SR": diff,
            "p_value": pval
        })

df_robust_cdi8 = pd.DataFrame(robust_cdi8).sort_values(["Portfolio", "b"]).reset_index(drop=True)
print("\nRobustez conjunta — CDI 8% e block size:")
print(df_robust_cdi8.to_string(index=False))
