import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme Configuration ──────────────────────────────────────────────────────
THEME_COLORS = {
    "light": {
        "bg_primary": "#f9fafb",
        "bg_secondary": "#ffffff",
        "text_primary": "#1f2937",
        "text_secondary": "#6b7280",
        "border": "#e5e7eb",
        "accent": "#3b82f6",
        "accent_dark": "#2563eb",
        "success": "#10b981",
        "warning": "#f59e0b",
        "panel_bg": "#ffffff",
        "panel_subtle": "#f3f4f6",
        "code_bg": "#f9fafb",
        "code_pre_bg": "#1f2937",
        "code_pre_text": "#f3f4f6",
    },
    "dark": {
        "bg_primary": "#0f172a",
        "bg_secondary": "#1e293b",
        "text_primary": "#f1f5f9",
        "text_secondary": "#cbd5e1",
        "border": "#334155",
        "accent": "#60a5fa",
        "accent_dark": "#3b82f6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "panel_bg": "#1e293b",
        "panel_subtle": "#334155",
        "code_bg": "#1e293b",
        "code_pre_bg": "#0f172a",
        "code_pre_text": "#e2e8f0",
    }
}

# ── Custom CSS: Professional Research Workspace with Theme Support ─────────────
def get_themed_css():
    """Generate CSS with current theme colors."""
    theme = st.session_state.get("theme", "light")
    c = THEME_COLORS[theme]
    
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {c['text_primary']};
    background: {c['bg_primary']};
}}

.stApp {{
    background: {c['bg_primary']};
}}

#MainMenu, footer, header {{ visibility: hidden; }}

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {{
    background: {c['bg_secondary']};
    border-right: 1px solid {c['border']};
}}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0.25rem;
}}

/* ── Main content ── */
.block-container {{
    padding: 1.5rem 2rem 2rem;
    max-width: 100%;
}}

/* ── Header bar ── */
.workspace-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid {c['border']};
    margin-bottom: 2rem;
}}

.workspace-title {{
    font-size: 1.25rem;
    font-weight: 600;
    color: {c['text_primary']};
    letter-spacing: -0.01em;
}}

.workspace-status {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: {c['text_secondary']};
}}

.status-indicator {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {c['success']};
}}

.status-indicator.idle {{
    background: {c['text_secondary']};
}}

.status-indicator.running {{
    background: {c['warning']};
    animation: pulse 1.5s ease-in-out infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

/* ── Research input section ── */
.research-input-container {{
    margin-bottom: 2rem;
}}

.research-query-label {{
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: {c['text_primary']};
    margin-bottom: 0.75rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}

.research-query-description {{
    font-size: 0.9375rem;
    color: {c['text_secondary']};
    margin-bottom: 1rem;
    line-height: 1.5;
}}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {{
    background: {c['panel_bg']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 6px !important;
    color: {c['text_primary']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9375rem !important;
    padding: 0.75rem 0.875rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}

.stTextInput > div > div > input::placeholder {{
    color: {c['text_secondary']} !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: {c['accent']} !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}}

.stTextInput > label {{
    display: none !important;
}}

/* ── Button styling ── */
.stButton > button {{
    background: {c['accent']} !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9375rem !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.625rem 1.25rem !important;
    cursor: pointer !important;
    transition: background 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    width: 100%;
}}

.stButton > button:hover {{
    background: {c['accent_dark']} !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}}

.stButton > button:active {{
    background: {c['accent_dark']} !important;
}}

.stButton > button:disabled {{
    background: {c['text_secondary']} !important;
    cursor: not-allowed !important;
    opacity: 0.6 !important;
}}

/* ── Suggestion chips ── */
.suggestion-chips {{
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}}

.chip {{
    display: inline-block;
    background: {c['panel_subtle']};
    border: 1px solid {c['border']};
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
    color: {c['text_secondary']};
    cursor: default;
    transition: background 0.2s, border-color 0.2s;
}}

.chip:hover {{
    background: {c['border']};
    border-color: {c['text_secondary']};
}}

/* ── Pipeline timeline ── */
.pipeline-container {{
    margin: 2rem 0;
}}

.pipeline-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {c['text_secondary']};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: block;
}}

.pipeline-timeline {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
    position: relative;
}}

.pipeline-stage {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}}

.stage-indicator {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: {c['border']};
    border: 2px solid {c['border']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: 600;
    color: {c['text_secondary']};
    transition: all 0.3s;
    margin-bottom: 0.75rem;
}}

.stage-indicator.done {{
    background: {c['success']};
    border-color: {c['success']};
    color: #ffffff;
}}

.stage-indicator.running {{
    background: {c['warning']};
    border-color: {c['warning']};
    color: #ffffff;
    box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.1);
}}

.stage-name {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {c['text_primary']};
    text-align: center;
    min-height: 2rem;
}}

.stage-description {{
    font-size: 0.7rem;
    color: {c['text_secondary']};
    text-align: center;
    line-height: 1.3;
    min-height: 2rem;
}}

.pipeline-connector {{
    position: absolute;
    top: 20px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: {c['border']};
    z-index: -1;
    transform: translateX(-50%);
    pointer-events: none;
}}

.pipeline-connector.done {{
    background: {c['success']};
}}

.pipeline-connector.partial {{
    background: linear-gradient(90deg, {c['success']} 0%, {c['border']} 100%);
}}

/* ── Activity console ── */
.activity-console {{
    background: {c['panel_bg']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 1.25rem;
    margin-bottom: 2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8125rem;
}}

.activity-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {c['text_secondary']};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: block;
}}

.activity-entry {{
    padding: 0.5rem 0;
    color: {c['text_primary']};
    line-height: 1.6;
    border-bottom: 1px solid {c['border']};
}}

.activity-entry:last-child {{
    border-bottom: none;
}}

.activity-icon {{
    display: inline-block;
    margin-right: 0.5rem;
    font-weight: 600;
}}

.activity-icon.done {{
    color: {c['success']};
}}

.activity-icon.running {{
    color: {c['warning']};
}}

.activity-icon.waiting {{
    color: {c['border']};
}}

.activity-text {{
    color: {c['text_primary']};
}}

.activity-subtext {{
    color: {c['text_secondary']};
    font-size: 0.75rem;
    margin-top: 0.25rem;
}}

/* ── Results workspace ── */
.results-container {{
    margin-top: 2rem;
}}

.results-divider {{
    height: 1px;
    background: {c['border']};
    margin: 2rem 0;
}}

.results-header {{
    font-size: 1rem;
    font-weight: 600;
    color: {c['text_primary']};
    margin-bottom: 1.5rem;
    letter-spacing: -0.01em;
}}

/* ── Tabs styling ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.5rem;
    border-bottom: 1px solid {c['border']};
}}

.stTabs [data-baseweb="tab"] {{
    font-size: 0.875rem;
    font-weight: 500;
    color: {c['text_secondary']};
    padding: 0.75rem 1rem !important;
    border-bottom: 2px solid transparent;
    border-radius: 0 !important;
}}

.stTabs [aria-selected="true"] [data-baseweb="tab"] {{
    color: {c['text_primary']} !important;
    border-bottom-color: {c['accent']} !important;
}}

/* ── Report panel ── */
.report-panel {{
    background: {c['panel_bg']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

.report-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {c['text_secondary']};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: block;
}}

.report-content {{
    font-size: 0.9375rem;
    line-height: 1.75;
    color: {c['text_primary']};
}}

.report-content h1, .report-content h2, .report-content h3 {{
    color: {c['text_primary']};
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}}

.report-content h1 {{ font-size: 1.75rem; font-weight: 700; }}
.report-content h2 {{ font-size: 1.375rem; font-weight: 600; }}
.report-content h3 {{ font-size: 1.125rem; font-weight: 600; }}

.report-content ul, .report-content ol {{
    margin: 0.75rem 0;
    padding-left: 1.5rem;
}}

.report-content li {{
    margin-bottom: 0.5rem;
}}

.report-content code {{
    background: {c['code_bg']};
    border: 1px solid {c['border']};
    border-radius: 3px;
    padding: 0.2em 0.4em;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875em;
    color: {c['accent']};
}}

.report-content pre {{
    background: {c['code_pre_bg']};
    color: {c['code_pre_text']};
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    margin: 1rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8125rem;
    line-height: 1.5;
}}

/* ── Critic panel ── */
.critic-panel {{
    background: {c['panel_subtle']};
    border: 1px solid {c['success']};
    border-radius: 6px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    opacity: 0.9;
}}

.critic-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {c['success']};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: block;
}}

.critic-content {{
    font-size: 0.9375rem;
    line-height: 1.75;
    color: {c['text_primary']};
}}

/* ── Action buttons ── */
.action-buttons {{
    display: flex;
    gap: 0.75rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}}

.action-button {{
    padding: 0.625rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    border: 1px solid {c['border']};
    background: {c['panel_bg']};
    color: {c['text_primary']};
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}}

.action-button:hover {{
    background: {c['panel_subtle']};
    border-color: {c['text_secondary']};
}}

.action-button.primary {{
    background: {c['accent']};
    color: #ffffff;
    border-color: {c['accent']};
}}

.action-button.primary:hover {{
    background: {c['accent_dark']};
    border-color: {c['accent_dark']};
}}

/* ── Empty state ── */
.empty-state {{
    text-align: center;
    padding: 3rem 2rem;
}}

.empty-state-title {{
    font-size: 1.125rem;
    font-weight: 600;
    color: {c['text_primary']};
    margin-bottom: 0.5rem;
}}

.empty-state-description {{
    font-size: 0.9375rem;
    color: {c['text_secondary']};
    margin-bottom: 1.5rem;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}}

/* ── Expander styling ── */
details summary {{
    font-weight: 500 !important;
    font-size: 0.9375rem !important;
    color: {c['text_primary']} !important;
    cursor: pointer !important;
    padding: 0.5rem 0 !important;
}}

/* ── Footer ── */
.footer {{
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid {c['border']};
    font-size: 0.8125rem;
    color: {c['text_secondary']};
    letter-spacing: 0.05em;
}}

</style>
"""
    
st.markdown(get_themed_css(), unsafe_allow_html=True)


# ── UI Component Functions ──────────────────────────────────────────────────

def render_sidebar():
    """Render the professional sidebar with navigation and status."""
    with st.sidebar:
        # Logo area
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #e5e7eb;">
            <div style="font-size: 1.75rem; font-weight: 700; color: #3b82f6; margin-bottom: 0.25rem;">◉</div>
            <div style="font-size: 0.9375rem; font-weight: 700; color: #111827;">RESEARCH</div>
            <div style="font-size: 0.9375rem; font-weight: 700; color: #111827;">MIND</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("☀️ Light", use_container_width=True, key="theme_light"):
                st.session_state.theme = "light"
                st.rerun()
        with col2:
            if st.button("🌙 Dark", use_container_width=True, key="theme_dark"):
                st.session_state.theme = "dark"
                st.rerun()
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # New Research button
        if st.button("+ New Research", use_container_width=True, key="new_research_btn"):
            st.session_state.results = {}
            st.session_state.running = False
            st.session_state.done = False
            st.session_state.topic_input = ""
            st.rerun()
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Workflow section
        st.markdown("""
        <div style="font-size: 0.75rem; font-weight: 600; color: #6b7280; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1rem;">
            Workflow
        </div>
        """, unsafe_allow_html=True)
        
        steps = [
            ("01", "Search Agent", "search"),
            ("02", "Reader Agent", "reader"),
            ("03", "Writer Chain", "writer"),
            ("04", "Critic Chain", "critic"),
        ]
        
        r = st.session_state.results
        for num, name, key in steps:
            if key in r:
                status = "✓ Done"
                status_color = "#10b981"
                indicator_color = "#10b981"
            elif st.session_state.running:
                # Check if this is the running step
                completed = list(r.keys())
                all_steps = ["search", "reader", "writer", "critic"]
                if key not in completed:
                    for k in all_steps:
                        if k not in completed:
                            status = "● Running" if k == key else "○ Waiting"
                            status_color = "#f59e0b" if k == key else "#9ca3af"
                            indicator_color = "#f59e0b" if k == key else "#9ca3af"
                            break
                else:
                    status = "○ Waiting"
                    status_color = "#9ca3af"
                    indicator_color = "#9ca3af"
            else:
                status = "○ Waiting"
                status_color = "#9ca3af"
                indicator_color = "#9ca3af"
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; padding: 0.5rem; border-radius: 4px; background: #f9fafb;">
                <div style="width: 4px; height: 20px; border-radius: 2px; background: {indicator_color};"></div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-size: 0.8125rem; font-weight: 500; color: #374151;">{name}</div>
                    <div style="font-size: 0.75rem; color: {status_color}; font-weight: 500;">{status}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Status indicator
        status_text = "Running" if st.session_state.running else ("Complete" if st.session_state.done else "Ready")
        status_color = "#f59e0b" if st.session_state.running else ("#10b981" if st.session_state.done else "#6b7280")
        indicator_class = "running" if st.session_state.running else ("done" if st.session_state.done else "idle")
        
        st.markdown(f"""
        <div style="padding: 1rem; background: #f3f4f6; border-radius: 6px; text-align: center;">
            <div style="font-size: 0.75rem; color: #6b7280; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">Status</div>
            <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                <div class="status-indicator {indicator_class}"></div>
                <span style="font-weight: 600; color: {status_color};">{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_header():
    """Render the compact workspace header."""
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        <div class="workspace-header">
            <div class="workspace-title">Research Workspace</div>
        """, unsafe_allow_html=True)
    with col2:
        status_text = "Running" if st.session_state.running else ("Complete" if st.session_state.done else "Ready")
        status_indicator = "running" if st.session_state.running else ("done" if st.session_state.done else "idle")
        st.markdown(f"""
        <div style="text-align: right; padding-top: 1rem;">
            <span class="workspace-status">
                <span class="status-indicator {status_indicator}"></span>
                <span>● {status_text}</span>
            </span>
        </div>
        """, unsafe_allow_html=True)


def render_research_input():
    """Render the research query input section."""
    st.markdown('<div class="research-input-container">', unsafe_allow_html=True)
    
    st.markdown('<span class="research-query-label">Research Query</span>', unsafe_allow_html=True)
    st.markdown('<p class="research-query-description">What would you like to investigate?</p>', unsafe_allow_html=True)
    
    topic = st.text_input(
        "topic",
        placeholder="Enter a research topic...",
        key="topic_input",
        label_visibility="collapsed",
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("")  # spacer
    with col2:
        run_btn = st.button("Run Research →", use_container_width=True, key="run_btn")
    
    # Suggestion chips
    st.markdown('<div class="suggestion-chips">', unsafe_allow_html=True)
    suggestions = ["LLM agents", "CRISPR", "Fusion energy"]
    cols = st.columns(len(suggestions))
    for idx, suggestion in enumerate(suggestions):
        with cols[idx]:
            st.button(
                suggestion,
                key=f"chip_{idx}",
                use_container_width=True,
                on_click=set_topic_input,
                args=(suggestion,),
            )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return topic, run_btn


def set_topic_input(topic):
    """Set the text input from a suggestion before the next script run."""
    st.session_state.topic_input = topic


def get_pipeline_state(step_key):
    """Get the state of a pipeline step."""
    r = st.session_state.results
    if not r:
        return "waiting"
    
    steps = ["search", "reader", "writer", "critic"]
    if step_key in r:
        return "done"
    
    if st.session_state.running:
        completed = list(r.keys())
        for k in steps:
            if k not in completed:
                return "running" if k == step_key else "waiting"
    
    return "waiting"


def render_pipeline():
    """Render the horizontal pipeline visualization."""
    st.markdown('<span class="pipeline-label">Execution Pipeline</span>', unsafe_allow_html=True)
    
    stages = [
        ("Search", "Gather sources", "search"),
        ("Reader", "Extract data", "reader"),
        ("Writer", "Write report", "writer"),
        ("Critic", "Review", "critic"),
    ]
    
    pipeline_html = '<div class="pipeline-timeline">'
    
    for idx, (name, desc, key) in enumerate(stages):
        state = get_pipeline_state(key)
        
        # Connector
        if idx > 0:
            prev_state = get_pipeline_state(stages[idx-1][2])
            connector_class = "done" if prev_state == "done" else ("partial" if prev_state == "running" else "")
            pipeline_html += f'<div class="pipeline-connector {connector_class}"></div>'
        
        indicator_class = f"{state}"
        icon = "✓" if state == "done" else ("●" if state == "running" else "○")
        
        pipeline_html += f"""
        <div class="pipeline-stage">
            <div class="stage-indicator {indicator_class}">{icon}</div>
            <div class="stage-name">{name}</div>
            <div class="stage-description">{desc}</div>
        </div>
        """
    
    pipeline_html += '</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)


def render_activity_console():
    """Render the activity console during execution."""
    r = st.session_state.results
    
    if not r or not st.session_state.running:
        return
    
    st.markdown('<span class="activity-label">Activity</span>', unsafe_allow_html=True)
    st.markdown('<div class="activity-console">', unsafe_allow_html=True)
    
    stages = [
        ("Search Agent", "search", "Gathering sources and web information"),
        ("Reader Agent", "reader", "Extracting and scraping content"),
        ("Writer Chain", "writer", "Generating research report"),
        ("Critic Chain", "critic", "Reviewing and providing feedback"),
    ]
    
    for name, key, description in stages:
        r = st.session_state.results
        if key in r:
            icon = "✓"
            icon_class = "done"
            status = "Completed"
        elif st.session_state.running:
            completed = list(r.keys())
            all_steps = ["search", "reader", "writer", "critic"]
            is_running = all(k in completed or k == key or all_steps.index(k) > all_steps.index(key) for k in all_steps if k not in completed or k == key)
            
            # Find if this is the current running step
            is_current = True
            for k in all_steps:
                if k not in completed:
                    is_current = (k == key)
                    break
            
            if is_current:
                icon = "●"
                icon_class = "running"
                status = "Running"
            else:
                icon = "○"
                icon_class = "waiting"
                status = "Waiting"
        else:
            icon = "○"
            icon_class = "waiting"
            status = "Waiting"
        
        st.markdown(f"""
        <div class="activity-entry">
            <span class="activity-icon {icon_class}">{icon}</span>
            <span class="activity-text">{name}</span>
            <div class="activity-subtext">{description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_empty_state():
    """Render the empty state when no research is in progress."""
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-title">Ready for Research</div>
        <p class="empty-state-description">
            Ask a question and let the research pipeline investigate it. 
            The system will search, extract, synthesize, and critique findings automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done", "theme", "submitted_topic"):
    if key not in st.session_state:
        if key == "results":
            st.session_state[key] = {}
        elif key == "theme":
            st.session_state[key] = "light"  # default to light theme
        elif key == "submitted_topic":
            st.session_state[key] = ""
        else:
            st.session_state[key] = False


# ── Render sidebar ────────────────────────────────────────────────────────────
render_sidebar()


# ── Main content ──────────────────────────────────────────────────────────────
render_header()

# Research input section
topic, run_btn = render_research_input()

# Pipeline visualization
if st.session_state.results or st.session_state.running:
    render_pipeline()
else:
    render_empty_state()


# ── Run pipeline logic ────────────────────────────────────────────────────────
# This backend logic is UNCHANGED from the original
if run_btn:
    topic = topic.strip()
    if not topic:
        st.error("Please enter a research topic first.")
    else:
        st.session_state.submitted_topic = topic
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    # Display activity console while running
    render_activity_console()
    
    results = {}
    topic_val = st.session_state.get("submitted_topic", "").strip()
    if not topic_val:
        st.session_state.running = False
        st.error("Research stopped because the topic was empty. Please enter a topic and try again.")
        st.stop()

    try:
        # ── Step 1: Search (BACKEND UNCHANGED) ──
        with st.spinner("🔍  Search Agent is working…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)

        # ── Step 2: Reader (BACKEND UNCHANGED) ──
        with st.spinner("📄  Reader Agent is scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)

        # ── Step 3: Writer (BACKEND UNCHANGED) ──
        with st.spinner("✍️  Writer is drafting the report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)

        # ── Step 4: Critic (BACKEND UNCHANGED) ──
        with st.spinner("🧐  Critic is reviewing the report…"):
            results["critic"] = critic_chain.invoke({
                "topic": topic_val,
                "report": results["writer"]
            })
            st.session_state.results = dict(results)

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    except Exception as e:
        st.session_state.running = False
        err_msg = str(e)
        if "401" in err_msg or "UNAUTHENTICATED" in err_msg or "ACCESS_TOKEN_TYPE_UNSUPPORTED" in err_msg:
            st.error(
                "🔑 **Authentication Error with Google Gemini API**\n\n"
                "Your `GEMINI_API_KEY` is invalid or is an access token instead of an API Key.\n\n"
                "**How to fix:**\n"
                "1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and click **Create API Key**.\n"
                "2. Your key should start with `AIzaSy...`\n"
                "3. Paste it into your `.env` file as `GEMINI_API_KEY=AIzaSy...`\n"
                "4. Restart the app."
            )
        else:
            st.error(f"❌ **An error occurred during research:** {err_msg}")


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="results-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="results-header">Research Results</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Tabs for different result views
    tab1, tab2, tab3, tab4 = st.tabs(["Report", "Sources", "Content", "Review"])
    
    with tab1:
        if "writer" in r:
            st.markdown('<div class="report-panel">', unsafe_allow_html=True)
            st.markdown('<span class="report-label">Final Research Report</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-content">', unsafe_allow_html=True)
            st.markdown(r["writer"])
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download as Markdown",
                    data=r["writer"],
                    file_name=f"research_report_{int(time.time())}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col2:
                if st.button("Copy Report", use_container_width=True, key="copy_btn"):
                    st.toast("Report copied! (Note: Use Ctrl+C in browser)", icon="📋")
    
    with tab2:
        if "search" in r:
            with st.expander("Search Results", expanded=True):
                st.markdown('<div class="report-panel">', unsafe_allow_html=True)
                st.markdown('<span class="report-label">Web Search Results</span>', unsafe_allow_html=True)
                st.markdown(f'<pre style="background: #f9fafb; padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 0.875rem; color: #374151;">{r["search"]}</pre>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        if "reader" in r:
            with st.expander("Scraped Content", expanded=True):
                st.markdown('<div class="report-panel">', unsafe_allow_html=True)
                st.markdown('<span class="report-label">Extracted Content</span>', unsafe_allow_html=True)
                st.markdown(f'<pre style="background: #f9fafb; padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 0.875rem; color: #374151;">{r["reader"]}</pre>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        if "critic" in r:
            st.markdown('<div class="critic-panel">', unsafe_allow_html=True)
            st.markdown('<span class="critic-label">Quality Review</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="critic-content">{r["critic"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    ResearchMind · Multi-Agent Research Pipeline · Powered by LangChain
</div>
""", unsafe_allow_html=True)