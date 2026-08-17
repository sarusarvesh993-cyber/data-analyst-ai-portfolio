"""Interactive India healthcare access and readiness command center."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_app.healthcare import (
    filter_states,
    load_outputs as load_healthcare_outputs,
    priority_export,
)
from portfolio_app.ui import (
    GOLD, NAVY, PALETTE, PURPLE, TEAL,
    configure_page, inject_global_css, render_footer, render_notice,
    render_page_header, render_section, render_sidebar, style_plotly,
)
from utils.ai_insights import generate_insights

configure_page("Healthcare Access & Readiness", "🏥")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 07 · Public-health operations & DuckDB",
    "India Healthcare Access & Readiness Command Center",
    "Turn official NHM quarterly MIS reports into transparent state-level access, staffing, mapping, outcome, and data-quality review signals.",
    ["National Health Mission", "36 states & UTs", "DuckDB SQL", "Readiness screening", "Power BI companion"],
)
render_notice(
    "navy", "NHM", "Official reports with mixed reference periods",
    "Facility status is reported for 2025-26, but population is Census 2011 and health outcomes use SRS reference periods. Per-capita rates and priority scores are review screens—not current capacity estimates or funding formulas.",
)

PROJECT_DIR = Path(__file__).resolve().parents[1] / "07-healthcare-access"
OUTPUT_DIR = PROJECT_DIR / "outputs"
POWER_BI_DIR = PROJECT_DIR / "power-bi"
SQL_PATH = PROJECT_DIR / "sql" / "01_healthcare_mart.sql"


@st.cache_data
def get_healthcare_outputs() -> dict[str, pd.DataFrame]:
    return load_healthcare_outputs(OUTPUT_DIR)


outputs = get_healthcare_outputs()
kpis = outputs["kpis"].iloc[0]
states = outputs["states"]
regions = outputs["regions"]
quality = outputs["quality"]
dictionary = outputs["dictionary"]
metadata = outputs["metadata"].iloc[0]

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("States & UTs", f"{int(kpis['states_and_uts'])}")
k2.metric("Sub-centres", f"{int(kpis['sub_centres']):,}")
k3.metric("PHCs", f"{int(kpis['phcs']):,}")
k4.metric("CHCs", f"{int(kpis['chcs']):,}")
k5.metric("District hospitals", f"{int(kpis['district_hospitals']):,}")
k6.metric("Reported 24x7 facilities", f"{int(kpis['facilities_24x7']):,}")

render_section(
    "Healthcare workspace", "Separate access signals from source limitations",
    "Every priority view keeps data completeness visible so missing population or outcome values cannot silently become zero need.",
)
overview_tab, explorer_tab, outcomes_tab, priority_tab, methods_tab = st.tabs(
    ["National overview", "State explorer", "Access & outcomes", "Review planner", "Methods & Power BI"]
)

with overview_tab:
    facility_totals = pd.DataFrame(
        {
            "Facility type": ["Sub-centres", "PHCs", "CHCs", "District hospitals", "Reported 24x7 facilities"],
            "Count": [kpis["sub_centres"], kpis["phcs"], kpis["chcs"], kpis["district_hospitals"], kpis["facilities_24x7"]],
        }
    ).sort_values("Count")
    left, right = st.columns([1, 1.25])
    facility_chart = px.bar(
        facility_totals, x="Count", y="Facility type", orientation="h",
        color="Count", color_continuous_scale=[[0, "#BDE9E1"], [1, TEAL]],
        title="Reported public-health facility footprint",
    )
    facility_chart.update_coloraxes(showscale=False)
    style_plotly(facility_chart, height=450, show_legend=False)
    left.plotly_chart(facility_chart, width="stretch")

    region_long = regions.melt(
        id_vars="focus_group", value_vars=["sub_centres", "phcs", "chcs", "district_hospitals"],
        var_name="facility_type", value_name="count",
    )
    region_chart = px.bar(
        region_long, x="focus_group", y="count", color="facility_type", barmode="group",
        title="Facility counts by NHM focus group",
        labels={"focus_group": "Focus group", "count": "Reported facilities", "facility_type": "Facility type"},
        color_discrete_sequence=PALETTE,
    )
    style_plotly(region_chart, height=450)
    right.plotly_chart(region_chart, width="stretch")

    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Median urban mapping", f"{kpis['median_urban_mapping_pct']:.1f}%")
    o2.metric("Median PHC 3-nurse readiness", f"{kpis['median_phc_three_nurse_readiness_pct']:.1f}%")
    o3.metric("Median reported IMR", f"{kpis['median_imr_reporting_states']:.1f}")
    o4.metric("Higher-priority states/UTs", f"{int(kpis['higher_priority_states'])}")

    st.dataframe(
        regions.rename(columns={
            "focus_group": "Focus group", "states_and_uts": "States/UTs",
            "sub_centres": "Sub-centres", "phcs": "PHCs", "chcs": "CHCs",
            "district_hospitals": "District hospitals", "facilities_24x7": "24x7 facilities",
            "median_urban_mapping_pct": "Median mapping %",
            "median_phc_three_nurse_readiness_pct": "Median PHC readiness %",
            "median_imr": "Median IMR", "median_review_priority_score": "Median priority score",
        }),
        hide_index=True, width="stretch",
    )

    highest = states.iloc[0]
    brief = generate_insights(
        {
            "headline": f"The NHM report covers {int(kpis['states_and_uts'])} states/UTs and {int(kpis['facilities_24x7']):,} reported 24x7 facilities.",
            "drivers": [
                f"Median PHC three-nurse readiness is {kpis['median_phc_three_nurse_readiness_pct']:.1f}%",
                f"{highest['state']} has the highest composite review-priority score",
                f"Population-dependent rates are unavailable for {int(kpis['population_missing_or_zero_states'])} states/UTs",
            ],
            "recommendation": "Use the priority screen to sequence validation meetings, then confirm signals with current population, beds, vacancies, travel time, utilization, and district records.",
        }
    )
    with st.expander("AI-assisted programme brief"):
        st.markdown(brief)

with explorer_tab:
    f1, f2, f3 = st.columns(3)
    focus_options = sorted(states["focus_group"].unique())
    band_options = ["Higher review priority", "Moderate review priority", "Lower review priority", "Insufficient data"]
    selected_focus = f1.multiselect("NHM focus groups", focus_options, default=[])
    selected_bands = f2.multiselect("Review-priority bands", band_options, default=[])
    completeness = f3.slider("Minimum data completeness", 0, 100, 0, 5, format="%d%%")
    filtered = filter_states(states, selected_focus, selected_bands, completeness)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Selected states/UTs", f"{len(filtered)}")
    s2.metric("Selected PHCs", f"{int(filtered['phcs'].sum()):,}")
    s3.metric("Selected CHCs", f"{int(filtered['chcs'].sum()):,}")
    s4.metric("Median readiness", f"{filtered['phc_three_nurse_readiness_pct'].median():.1f}%" if len(filtered) else "—")
    s5.metric("Median completeness", f"{filtered['data_completeness_pct'].median():.1f}%" if len(filtered) else "—")

    display = filtered[
        ["state", "focus_group", "sub_centres", "phcs", "chcs", "district_hospitals",
         "facilities_24x7", "facilities_24x7_per_100k", "phc_three_nurse_readiness_pct",
         "urban_facility_mapping_pct", "imr", "u5mr", "review_priority_score",
         "review_priority_band", "data_completeness_pct"]
    ].rename(columns={
        "state": "State / UT", "focus_group": "Focus group", "sub_centres": "Sub-centres",
        "phcs": "PHCs", "chcs": "CHCs", "district_hospitals": "District hospitals",
        "facilities_24x7": "24x7 facilities", "facilities_24x7_per_100k": "24x7 / 100K",
        "phc_three_nurse_readiness_pct": "PHC readiness %", "urban_facility_mapping_pct": "Urban mapping %",
        "imr": "IMR", "u5mr": "U5MR", "review_priority_score": "Priority score",
        "review_priority_band": "Priority band", "data_completeness_pct": "Completeness %",
    })
    st.dataframe(display, hide_index=True, width="stretch", height=560)

with outcomes_tab:
    plot = states.dropna(subset=["facilities_24x7_per_100k", "imr", "population_lakh"])
    access_chart = px.scatter(
        plot, x="facilities_24x7_per_100k", y="imr", size="population_lakh",
        color="focus_group", hover_name="state", size_max=48,
        title="Reported 24x7 access density and infant mortality",
        labels={
            "facilities_24x7_per_100k": "24x7 facilities per 100K Census-2011 population",
            "imr": "Infant mortality rate (SRS 2023)", "focus_group": "Focus group",
        }, color_discrete_sequence=PALETTE,
    )
    style_plotly(access_chart, height=560)
    st.plotly_chart(access_chart, width="stretch")
    correlation = plot[["facilities_24x7_per_100k", "imr"]].corr().iloc[0, 1]
    a1, a2, a3 = st.columns(3)
    a1.metric("States in scatter", f"{len(plot)}")
    a2.metric("Descriptive correlation", f"{correlation:.2f}")
    a3.metric("Population-rate exclusions", f"{int(kpis['population_missing_or_zero_states'])}")
    render_notice(
        "amber", "≠", "Association is not causation",
        "Facility count does not measure beds, staffing quality, travel time, private-sector capacity, utilization, or case mix. The chart uses Census-2011 population and should not support causal claims.",
    )
    readiness = states.sort_values("phc_three_nurse_readiness_pct").dropna(subset=["phc_three_nurse_readiness_pct"])
    readiness_chart = px.bar(
        readiness, x="phc_three_nurse_readiness_pct", y="state", orientation="h",
        color="phc_three_nurse_readiness_pct", color_continuous_scale=[[0, "#F3C2B8"], [.5, GOLD], [1, TEAL]],
        title="Reported PHC three-nurse readiness",
        labels={"phc_three_nurse_readiness_pct": "PHCs with three staff nurses (%)", "state": ""},
    )
    readiness_chart.update_coloraxes(showscale=False)
    style_plotly(readiness_chart, height=780, show_legend=False)
    st.plotly_chart(readiness_chart, width="stretch")

with priority_tab:
    priority = states.dropna(subset=["review_priority_score"]).nlargest(20, "review_priority_score").sort_values("review_priority_score")
    priority_chart = px.bar(
        priority, x="review_priority_score", y="state", orientation="h",
        color="review_priority_band",
        color_discrete_map={"Higher review priority": "#E26D5A", "Moderate review priority": GOLD, "Lower review priority": TEAL},
        title="Composite healthcare review-priority screen",
        labels={"review_priority_score": "Priority score (0–100)", "state": "", "review_priority_band": "Band"},
    )
    style_plotly(priority_chart, height=650)
    st.plotly_chart(priority_chart, width="stretch")
    st.dataframe(priority_export(states), hide_index=True, width="stretch", height=460)
    st.download_button(
        "Download review-priority table", data=priority_export(states).to_csv(index=False).encode("utf-8"),
        file_name="india_healthcare_review_priority.csv", mime="text/csv", width="stretch",
    )
    render_notice(
        "teal", "4", "Transparent and completeness-aware",
        "The score averages percentiles for low 24x7 density, low PHC three-nurse readiness, low urban mapping, and high IMR. It requires at least three components and must be validated locally before action.",
    )

with methods_tab:
    m1, m2, m3 = st.columns(3)
    m1.metric("Quality checks", f"{len(quality)}")
    m2.metric("Passed", f"{int(quality['check_status'].eq('PASS').sum())}")
    m3.metric("Require context", f"{int(quality['check_status'].eq('REVIEW').sum())}")
    st.dataframe(quality, hide_index=True, width="stretch")
    st.dataframe(dictionary, hide_index=True, width="stretch")
    with st.expander("Review the DuckDB mart SQL"):
        st.code(SQL_PATH.read_text(encoding="utf-8"), language="sql", line_numbers=True)
    st.link_button("Open official NHM MIS source page", str(metadata["source_page"]), width="stretch")

    render_section("Power BI companion", "Desktop-ready model, DAX, theme, and validation guide")
    st.image(PROJECT_DIR / "assets" / "power_bi_companion.png", caption="Power BI executive-page layout target", width="stretch")
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download Power BI theme", (POWER_BI_DIR / "theme.json").read_bytes(), "healthcare_access_theme.json", "application/json", width="stretch")
    d2.download_button("Download DAX measures", (POWER_BI_DIR / "measures.dax").read_bytes(), "healthcare_access_measures.dax", "text/plain", width="stretch")
    d3.download_button("Download Power BI guide", (POWER_BI_DIR / "README.md").read_bytes(), "healthcare_access_power_bi_guide.md", "text/markdown", width="stretch")

render_footer()
