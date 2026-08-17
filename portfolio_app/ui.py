"""Shared visual system for the Streamlit portfolio.

The design combines a friendly teal presentation with a structured navy
navigation and restrained chart styling. Everything is embedded so the app
has no external font, image, or stylesheet dependency.
"""
from __future__ import annotations

from html import escape

import streamlit as st

NAVY = "#173B63"
NAVY_DARK = "#102A43"
TEAL = "#0F8A7B"
TEAL_BRIGHT = "#16B8A6"
TEAL_PALE = "#DDF7F1"
GOLD = "#F4A340"
PURPLE = "#7C6CE7"
SLATE = "#63788B"
PALETTE = [TEAL, NAVY, GOLD, PURPLE, "#55A6D9", "#E26D5A"]


def configure_page(title: str, icon: str) -> None:
    """Set browser metadata before rendering other page elements."""
    st.set_page_config(
        page_title=f"{title} | Sarvesh Kommawar",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_css() -> None:
    """Apply the portfolio's shared teal-and-navy visual system."""
    st.markdown(
        """
        <style>
        :root {
            --navy: #173B63;
            --navy-dark: #102A43;
            --teal: #0F8A7B;
            --teal-bright: #16B8A6;
            --teal-pale: #DDF7F1;
            --gold: #F4A340;
            --ink: #173042;
            --muted: #63788B;
            --line: #DCE8E5;
            --canvas: #F4FAF8;
            --white: #FFFFFF;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
                "Segoe UI", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 92% 2%, rgba(22,184,166,.09), transparent 24rem),
                linear-gradient(180deg, #F8FCFB 0%, #F3F8F7 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: var(--navy-dark);
            letter-spacing: -.025em;
        }
        h1 { font-weight: 780 !important; }
        p { line-height: 1.65; }

        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid var(--line);
            box-shadow: 8px 0 28px rgba(16,42,67,.04);
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 1.15rem;
        }
        [data-testid="stSidebarNav"] {
            padding-top: .2rem;
        }
        [data-testid="stSidebarNav"]::before {
            content: "NAVIGATION";
            display: block;
            color: #79908F;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .14em;
            padding: .2rem 1.4rem .65rem;
        }
        [data-testid="stSidebarNav"] a {
            border-radius: .7rem;
            margin: .12rem .7rem;
            color: var(--navy) !important;
        }
        [data-testid="stSidebarNav"] a:hover {
            background: var(--teal-pale);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, #DDF7F1, #EEF9F6);
            color: #08766A !important;
            font-weight: 700;
        }

        .sidebar-brand {
            padding: 1rem 1rem .95rem;
            border-radius: 1rem;
            background: linear-gradient(145deg, #102A43, #1E4C75);
            color: white;
            margin-bottom: .7rem;
            box-shadow: 0 10px 24px rgba(16,42,67,.15);
        }
        .sidebar-brand__mark {
            width: 2.25rem;
            height: 2.25rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: .72rem;
            background: rgba(255,255,255,.13);
            color: #72F0DA;
            font-weight: 900;
            margin-bottom: .7rem;
        }
        .sidebar-brand__name { font-size: .98rem; font-weight: 800; }
        .sidebar-brand__role {
            margin-top: .18rem;
            color: #BBD7E8;
            font-size: .72rem;
            letter-spacing: .07em;
            text-transform: uppercase;
        }
        .sidebar-status {
            display: flex;
            align-items: center;
            gap: .5rem;
            padding: .7rem .8rem;
            margin: .7rem 0 1rem;
            border: 1px solid var(--line);
            border-radius: .8rem;
            color: #52706D;
            font-size: .76rem;
            background: #F8FCFB;
        }
        .status-dot {
            width: .54rem; height: .54rem; border-radius: 50%;
            background: #24B47E; box-shadow: 0 0 0 4px rgba(36,180,126,.12);
        }

        .home-hero, .page-hero {
            position: relative;
            overflow: hidden;
            border-radius: 1.55rem;
            padding: 2.25rem 2.4rem;
            color: white;
            background: linear-gradient(120deg, #0B6E65 0%, #0F8A7B 48%, #19B7A5 100%);
            box-shadow: 0 18px 48px rgba(15,138,123,.18);
            margin-bottom: 1.25rem;
        }
        .home-hero { padding: 3rem 2.7rem; }
        .home-hero::after, .page-hero::after {
            content: "";
            position: absolute;
            width: 19rem; height: 19rem;
            border: 1px solid rgba(255,255,255,.18);
            border-radius: 50%;
            top: -9rem; right: -4rem;
            box-shadow: 0 0 0 3.2rem rgba(255,255,255,.045),
                        0 0 0 6.4rem rgba(255,255,255,.025);
        }
        .hero-kicker {
            display: inline-flex;
            gap: .48rem;
            align-items: center;
            padding: .38rem .72rem;
            border-radius: 999px;
            background: rgba(255,255,255,.14);
            border: 1px solid rgba(255,255,255,.18);
            color: #E9FFFB;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
        }
        .home-hero h1, .page-hero h1 {
            color: white !important;
            margin: .85rem 0 .55rem;
            max-width: 780px;
            font-size: clamp(2rem, 4vw, 3.25rem);
            line-height: 1.08;
        }
        .page-hero h1 { font-size: clamp(1.8rem, 3.2vw, 2.65rem); }
        .hero-copy {
            max-width: 760px;
            color: #DDFBF5;
            font-size: 1.02rem;
            line-height: 1.6;
            margin: 0;
        }
        .hero-badges { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem; }
        .hero-badge {
            padding: .34rem .65rem;
            border-radius: .55rem;
            background: rgba(8,67,62,.22);
            color: #EFFFFC;
            font-size: .72rem;
            font-weight: 650;
        }

        [data-testid="stMetric"] {
            background: rgba(255,255,255,.92);
            border: 1px solid var(--line);
            padding: 1rem 1.05rem;
            border-radius: 1rem;
            box-shadow: 0 8px 24px rgba(16,42,67,.055);
            min-height: 112px;
        }
        [data-testid="stMetric"]:hover {
            border-color: #B4DED5;
            transform: translateY(-2px);
            transition: .2s ease;
        }
        [data-testid="stMetricLabel"] { color: #6A807F; }
        [data-testid="stMetricValue"] { color: var(--navy-dark); font-weight: 800; }

        .section-kicker {
            color: var(--teal);
            font-size: .72rem;
            font-weight: 850;
            letter-spacing: .11em;
            text-transform: uppercase;
            margin-top: 1.8rem;
        }
        .section-heading {
            color: var(--navy-dark);
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -.025em;
            margin: .24rem 0 .25rem;
        }
        .section-copy { color: var(--muted); margin-bottom: 1.1rem; }

        .project-card, .capability-card, .process-card {
            background: rgba(255,255,255,.96);
            border: 1px solid var(--line);
            border-radius: 1.15rem;
            padding: 1.25rem;
            box-shadow: 0 9px 26px rgba(16,42,67,.055);
        }
        .project-card {
            min-height: 230px;
            position: relative;
            overflow: hidden;
            transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
        }
        .project-card:hover {
            transform: translateY(-5px);
            border-color: #A8D9D0;
            box-shadow: 0 16px 34px rgba(15,138,123,.12);
        }
        .project-card::after {
            content: ""; position: absolute; top: 0; left: 0;
            width: 100%; height: 5px;
            background: var(--accent, var(--teal));
        }
        .project-number {
            width: 2.7rem; height: 2.7rem; border-radius: .85rem;
            display: flex; align-items: center; justify-content: center;
            background: var(--soft, var(--teal-pale)); color: var(--accent, var(--teal));
            font-weight: 850; margin: .25rem 0 1rem;
        }
        .project-title { color: var(--navy-dark); font-size: 1.06rem; font-weight: 800; }
        .project-copy { color: var(--muted); font-size: .86rem; line-height: 1.55; margin: .55rem 0 .85rem; }
        .tag {
            display: inline-block; padding: .25rem .5rem; margin: .15rem .18rem .15rem 0;
            background: #F0F7F5; color: #52716E; border-radius: 999px;
            font-size: .67rem; font-weight: 700;
        }
        .capability-card { min-height: 145px; }
        .capability-icon {
            width: 2.2rem; height: 2.2rem; border-radius: .7rem;
            display: flex; align-items: center; justify-content: center;
            background: var(--teal-pale); color: var(--teal); font-weight: 800;
            margin-bottom: .75rem;
        }
        .capability-title { font-weight: 800; color: var(--navy-dark); }
        .capability-copy { color: var(--muted); font-size: .78rem; line-height: 1.5; margin-top: .35rem; }
        .process-card { min-height: 116px; padding: 1rem; }
        .process-step { color: var(--teal); font-size: .7rem; font-weight: 850; letter-spacing: .07em; }
        .process-title { color: var(--navy-dark); font-size: .9rem; font-weight: 800; margin-top: .35rem; }
        .process-copy { color: var(--muted); font-size: .72rem; margin-top: .28rem; line-height: 1.45; }

        .notice {
            display: flex; gap: .9rem; align-items: flex-start;
            padding: 1rem 1.1rem; border-radius: 1rem; margin: .7rem 0 1.2rem;
            background: #FFFFFF; border: 1px solid var(--line);
        }
        .notice--teal { background: #F1FBF8; border-color: #C6EDE5; }
        .notice--amber { background: #FFF9EE; border-color: #F5DEB4; }
        .notice--navy { background: #F2F6FA; border-color: #D6E2ED; }
        .notice-icon {
            flex: 0 0 auto; width: 2rem; height: 2rem; border-radius: .65rem;
            display: flex; align-items: center; justify-content: center;
            background: #DDF7F1; color: var(--teal); font-weight: 900;
        }
        .notice--amber .notice-icon { background: #FFEBC7; color: #B66A16; }
        .notice--navy .notice-icon { background: #DDE8F2; color: var(--navy); }
        .notice-title { color: var(--navy-dark); font-weight: 800; font-size: .88rem; }
        .notice-copy { color: var(--muted); font-size: .79rem; line-height: 1.5; margin-top: .2rem; }

        [data-baseweb="tab-list"] {
            gap: .3rem; background: rgba(255,255,255,.82);
            padding: .4rem; border: 1px solid var(--line); border-radius: .85rem;
        }
        [data-baseweb="tab"] {
            border-radius: .62rem; padding: .5rem .8rem;
        }
        [data-baseweb="tab"][aria-selected="true"] {
            background: var(--teal-pale); color: #08766A;
        }
        [data-baseweb="tab-highlight"] { background-color: transparent; }

        div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line) !important;
            border-radius: 1rem !important;
            background: rgba(255,255,255,.72);
        }
        .stButton > button, .stDownloadButton > button, .stLinkButton > a {
            border-radius: .75rem !important;
            border: 1px solid #B9DBD5 !important;
            color: #086F65 !important;
            background: #F5FCFA !important;
            font-weight: 750 !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover {
            border-color: var(--teal) !important;
            background: var(--teal-pale) !important;
            transform: translateY(-1px);
        }
        [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(90deg, #0F8A7B, #16B8A6) !important;
            color: white !important; border: none !important;
        }

        [data-testid="stPlotlyChart"] {
            background: rgba(255,255,255,.95);
            border: 1px solid var(--line);
            border-radius: 1rem;
            padding: .45rem;
            box-shadow: 0 8px 24px rgba(16,42,67,.045);
        }
        [data-testid="stExpander"] {
            background: rgba(255,255,255,.8);
            border-color: var(--line);
            border-radius: .8rem;
        }

        .portfolio-footer {
            margin-top: 2.5rem;
            padding: 1.25rem 0 .3rem;
            border-top: 1px solid var(--line);
            display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
            color: #718784; font-size: .76rem;
        }
        .portfolio-footer a { color: var(--teal); text-decoration: none; font-weight: 700; }

        @media (max-width: 760px) {
            .block-container { padding: 1rem 1rem 3rem; }
            .home-hero, .page-hero { padding: 1.7rem 1.35rem; border-radius: 1.15rem; }
            .home-hero h1, .page-hero h1 { font-size: 2rem; }
            .project-card { min-height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render a compact identity and status block below native navigation."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand__mark">SK</div>
                <div class="sidebar-brand__name">Sarvesh Kommawar</div>
                <div class="sidebar-brand__role">Data Analyst Portfolio</div>
            </div>
            <div class="sidebar-status">
                <span class="status-dot"></span>
                Portfolio projects ready to explore
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            "View GitHub repository",
            "https://github.com/sarusarvesh993-cyber/data-analyst-ai-portfolio",
            width="stretch",
        )
        st.link_button(
            "Connect on LinkedIn",
            "https://www.linkedin.com/in/sarvesh-kommawar-3b166b278/",
            width="stretch",
        )
        st.caption("Python · Statistics · Streamlit · Decision analytics")


def render_home_hero() -> None:
    st.markdown(
        """
        <div class="home-hero">
            <span class="hero-kicker">● Available for data analyst opportunities</span>
            <h1>Hi, I'm Sarvesh. I turn business questions into clear decisions.</h1>
            <p class="hero-copy">
                Explore three interactive analytics workflows spanning retention,
                forecasting, and experimentation—each with tested calculations,
                honest limitations, and a stakeholder-ready recommendation.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">Python analytics</span>
                <span class="hero-badge">Statistical validation</span>
                <span class="hero-badge">Interactive dashboards</span>
                <span class="hero-badge">10 automated tests</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    eyebrow: str,
    title: str,
    subtitle: str,
    badges: list[str] | tuple[str, ...] = (),
) -> None:
    badge_html = "".join(
        f'<span class="hero-badge">{escape(badge)}</span>' for badge in badges
    )
    st.markdown(
        f"""
        <div class="page-hero">
            <span class="hero-kicker">{escape(eyebrow)}</span>
            <h1>{escape(title)}</h1>
            <p class="hero-copy">{escape(subtitle)}</p>
            <div class="hero-badges">{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(kicker: str, title: str, copy: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-kicker">{escape(kicker)}</div>
        <div class="section-heading">{escape(title)}</div>
        {f'<div class="section-copy">{escape(copy)}</div>' if copy else ''}
        """,
        unsafe_allow_html=True,
    )


def render_notice(kind: str, icon: str, title: str, copy: str) -> None:
    safe_kind = kind if kind in {"teal", "amber", "navy"} else "teal"
    st.markdown(
        f"""
        <div class="notice notice--{safe_kind}">
            <div class="notice-icon">{escape(icon)}</div>
            <div>
                <div class="notice-title">{escape(title)}</div>
                <div class="notice-copy">{escape(copy)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_plotly(figure, *, height: int | None = None, show_legend: bool | None = None):
    """Apply restrained navy/teal chart styling across project pages."""
    layout = {
        "template": "plotly_white",
        "paper_bgcolor": "rgba(255,255,255,0)",
        "plot_bgcolor": "#FFFFFF",
        "font": {"family": "Arial, sans-serif", "color": NAVY_DARK, "size": 12},
        "title": {"font": {"size": 17, "color": NAVY_DARK}, "x": 0.02},
        "margin": {"l": 48, "r": 28, "t": 65, "b": 48},
        "colorway": PALETTE,
        "hoverlabel": {"bgcolor": "#FFFFFF", "font_color": NAVY_DARK},
    }
    if height is not None:
        layout["height"] = height
    if show_legend is not None:
        layout["showlegend"] = show_legend
    figure.update_layout(**layout)
    figure.update_xaxes(showgrid=False, linecolor="#DCE8E5", zeroline=False)
    figure.update_yaxes(gridcolor="#E8F0EE", linecolor="#DCE8E5", zeroline=False)
    return figure


def render_footer() -> None:
    st.markdown(
        """
        <div class="portfolio-footer">
            <span>Built by Sarvesh Kommawar · Data Analyst Portfolio</span>
            <span>
                <a href="https://github.com/sarusarvesh993-cyber">GitHub</a>
                &nbsp;·&nbsp;
                <a href="https://www.linkedin.com/in/sarvesh-kommawar-3b166b278/">LinkedIn</a>
                &nbsp;·&nbsp;
                <a href="mailto:kommawar57@gmail.com">Email</a>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
