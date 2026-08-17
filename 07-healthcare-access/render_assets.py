"""Render reproducible Project 07 documentation and Power BI previews."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
ASSET_DIR = PROJECT_DIR / "assets"
NAVY, TEAL, GOLD, RED, BLUE = "#102A43", "#0F8A7B", "#F4A340", "#E26D5A", "#2B6F92"


def _save(fig, name):
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSET_DIR / name, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {ASSET_DIR / name}")


def render():
    sns.set_theme(style="whitegrid", font_scale=0.9)
    states = pd.read_csv(OUTPUT_DIR / "state_health_access.csv")
    kpis = pd.read_csv(OUTPUT_DIR / "executive_kpis.csv").iloc[0]

    top = states.nlargest(15, "review_priority_score").sort_values("review_priority_score")
    fig, ax = plt.subplots(figsize=(10, 6.4))
    colors = np.where(top["review_priority_band"].eq("Higher review priority"), RED, GOLD)
    ax.barh(top["state"], top["review_priority_score"], color=colors)
    ax.set_title("Healthcare access review-priority screen", loc="left", color=NAVY, weight="bold", fontsize=15)
    ax.set_xlabel("Review priority score (0–100)")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.2); ax.grid(axis="y", visible=False)
    _save(fig, "priority_screen.png")

    plot = states.dropna(subset=["facilities_24x7_per_100k", "imr", "population_lakh"])
    fig, ax = plt.subplots(figsize=(10, 6))
    sizes = 40 + 700 * plot["population_lakh"] / plot["population_lakh"].max()
    ax.scatter(plot["facilities_24x7_per_100k"], plot["imr"], s=sizes, c=TEAL, alpha=0.65, edgecolor="white")
    for row in plot.nlargest(8, "review_priority_score").itertuples():
        ax.annotate(row.state, (row.facilities_24x7_per_100k, row.imr), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.set_title("Reported 24x7 access and infant mortality", loc="left", color=NAVY, weight="bold", fontsize=15)
    ax.set_xlabel("Reported 24x7 facilities per 100K Census-2011 population")
    ax.set_ylabel("Infant mortality rate (SRS 2023)")
    ax.grid(alpha=0.2)
    _save(fig, "access_outcomes.png")

    fig = plt.figure(figsize=(13.5, 7.6), facecolor="#F3F5F7")
    c = fig.add_axes([0, 0, 1, 1]); c.set_axis_off()
    c.add_patch(plt.Rectangle((0, .93), 1, .07, color="#1C1B1F"))
    c.text(.025, .965, "INDIA HEALTHCARE ACCESS & READINESS", color="white", weight="bold", va="center", fontsize=13)
    c.text(.825, .965, "POWER BI COMPANION", color="#D8D5DC", va="center", fontsize=8)
    c.add_patch(plt.Rectangle((.025, .84), .95, .065, facecolor="white", edgecolor="#DDDEE2"))
    for x, title, value in [(.045,"FOCUS GROUP","All"),(.35,"PRIORITY BAND","All"),(.69,"STATUS DATE","31 Dec 2025")]:
        c.text(x,.882,title,color="#727079",fontsize=7); c.text(x,.852,value,color="#242229",fontsize=10,weight="bold")
    cards=[("STATES / UTs",f"{int(kpis['states_and_uts'])}"),("SUB-CENTRES",f"{int(kpis['sub_centres']):,}"),("PHCs",f"{int(kpis['phcs']):,}"),("24x7 FACILITIES",f"{int(kpis['facilities_24x7']):,}"),("HIGHER PRIORITY",f"{int(kpis['higher_priority_states'])}")]
    for i,(title,value) in enumerate(cards):
        x=.025+i*.192; c.add_patch(plt.Rectangle((x,.70),.175,.105,facecolor="white",edgecolor="#DDDEE2")); c.add_patch(plt.Rectangle((x,.70),.175,.008,color="#F2C811")); c.text(x+.014,.775,title,color="#727079",fontsize=7); c.text(x+.014,.728,value,color="#242229",fontsize=17,weight="bold")
    a=fig.add_axes([.055,.12,.42,.50],facecolor="white")
    p=top.tail(10); a.barh(p["state"],p["review_priority_score"],color="#F2C811"); a.set_title("Review-priority screen",loc="left",fontsize=10,weight="bold"); a.set_xlabel("Score",fontsize=8); a.tick_params(labelsize=7); a.grid(axis="x",alpha=.2);a.grid(axis="y",visible=False)
    b=fig.add_axes([.56,.12,.39,.50],facecolor="white")
    b.scatter(plot["facilities_24x7_per_100k"],plot["imr"],s=sizes*.7,c="#5B9BD5",alpha=.7)
    for row in plot.nlargest(6,"review_priority_score").itertuples(): b.annotate(row.state,(row.facilities_24x7_per_100k,row.imr),fontsize=6,xytext=(3,3),textcoords="offset points")
    b.set_title("Access density vs infant mortality",loc="left",fontsize=10,weight="bold");b.set_xlabel("24x7 facilities / 100K",fontsize=8);b.set_ylabel("IMR",fontsize=8);b.tick_params(labelsize=7);b.grid(alpha=.2)
    _save(fig,"power_bi_companion.png")


if __name__ == "__main__":
    render()
