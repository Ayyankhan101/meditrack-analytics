import sqlite3, pickle, io, base64
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediTrack Command Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark Command Center Theme ─────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root{
  --bg-dark:#0a0f0d; --bg-card:#0d1411; --bg-card-hover:#112420;
  --teal:#0d9488; --teal-light:#ccfbf1; --teal-dark:#134e4a;
  --teal-neon:#14ffec; --teal-dim:#0a6b68;
  --red:#ef4444; --amber:#f59e0b; --sky:#0ea5e9;
  --text:#e2e8f0; --text-muted:#94a3b8; --text-dim:#64748b;
  --border:#1e3a35; --glow:rgba(20,255,236,0.3);
}
html,body,[class*="css"]{background:var(--bg-dark)!important;color:var(--text)!important;}
h1,h2,h3{font-family:'DM Serif Display',serif;color:var(--teal-light)!important;}
p,div,span,label{font-family:'DM Sans',sans-serif;}
.stApp{background:var(--bg-dark)!important;}
[data-testid="stSidebar"]{background:#0d1411!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--teal-light)!important;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2{color:var(--teal-neon)!important;}
.metric-card{
  background:linear-gradient(135deg,var(--bg-card) 0%,#0f1f1c 100%);
  border:1px solid var(--border);border-radius:16px;
  padding:20px 24px;box-shadow:0 4px 20px rgba(0,0,0,0.4),0 0 30px var(--glow);
  transition:transform 0.2s ease,box-shadow 0.2s ease;
}
.metric-card:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,0,0,0.5),0 0 40px var(--glow);}
.metric-val{font-size:2.2rem;font-weight:700;color:var(--teal-neon);line-height:1.1;font-family:'DM Sans',sans-serif;}
.metric-lbl{font-size:.75rem;color:var(--text-dim);letter-spacing:.1em;text-transform:uppercase;}
.section-head{
  font-family:'DM Serif Display',serif;font-size:1.3rem;
  color:var(--teal-neon);border-left:4px solid var(--teal-neon);
  padding-left:12px;margin:32px 0 16px;background:linear-gradient(90deg,rgba(20,255,236,0.1) 0%,transparent 100%);
  padding:8px 12px 8px 16px;
}
div[data-testid="stMetric"]{background:var(--bg-card);border-radius:12px;padding:12px;}
div[data-testid="stMetric"] label{color:var(--text-muted)!important;}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{color:var(--teal-neon)!important;}
.stButton>button{
  background:linear-gradient(135deg,var(--teal) 0%,var(--teal-dark) 100%);
  color:var(--teal-light);border:none;border-radius:8px;font-weight:600;
  box-shadow:0 4px 15px rgba(13,148,136,0.4);
}
.stButton>button:hover{background:linear-gradient(135deg,var(--teal-neon) 0%,var(--teal) 100%);color:var(--bg-dark)!important;}
.stSelectbox>div>div{background:var(--bg-card)!important;border:1px solid var(--border)!important;color:var(--text)!important;}
.stMultiSelect>div>div{background:var(--bg-card)!important;border:1px solid var(--border)!important;color:var(--text)!important;}
div[data-testid="stDataFrame"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:12px;}
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--bg-dark);}
::-webkit-scrollbar-thumb{background:var(--teal-dark);border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:var(--teal);}
.alert-box{
  background:linear-gradient(135deg,rgba(239,68,68,0.1) 0%,rgba(239,68,68,0.05) 100%);
  border:1px solid var(--red);border-radius:12px;padding:16px;margin:8px 0;
  animation:pulse 2s infinite;
}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.4);}50%{box-shadow:0 0 0 10px rgba(239,68,68,0);}}
.info-box{
  background:linear-gradient(135deg,rgba(20,255,236,0.1) 0%,rgba(20,255,236,0.05) 100%);
  border:1px solid var(--teal);border-radius:12px;padding:16px;margin:8px 0;
}
.radar-card{
  background:var(--bg-card);border:1px solid var(--border);border-radius:16px;
  padding:20px;transition:all 0.3s ease;
}
.radar-card:hover{border-color:var(--teal-neon);box-shadow:0 0 20px var(--glow);}
.floor-card{
  background:var(--bg-card);border:1px solid var(--border);border-radius:12px;
  padding:12px;transition:all 0.2s ease;cursor:pointer;
}
.floor-card:hover{transform:scale(1.02);border-color:var(--teal);}
.floor-completed{background:linear-gradient(135deg,rgba(20,255,236,0.15) 0%,rgba(13,148,136,0.1) 100%);border-left:4px solid var(--teal-neon);}
.floor-pending{background:linear-gradient(135deg,rgba(245,158,11,0.15) 0%,rgba(245,158,11,0.1) 100%);border-left:4px solid var(--amber);}
.floor-noshow{background:linear-gradient(135deg,rgba(239,68,68,0.15) 0%,rgba(239,68,68,0.1) 100%);border-left:4px solid var(--red);}
</style>
""",
    unsafe_allow_html=True,
)


# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    con = sqlite3.connect("meditrack.db")
    df = pd.read_sql(
        """
        SELECT a.*, d.name doctor_name, d.department, d.seniority,
               c.city, c.clinic_name
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN clinics c ON a.clinic_id = c.clinic_id
    """,
        con,
    )
    con.close()
    df["appt_date"] = pd.to_datetime(df["appt_date"])
    df["month"] = df["appt_date"].dt.to_period("M").astype(str)
    df["appt_hour"] = df["appt_time"].str[:2].astype(int)
    df["week"] = df["appt_date"].dt.isocalendar().week.astype(int)
    df["year"] = df["appt_date"].dt.year
    df["day_of_week_num"] = df["appt_date"].dt.dayofweek
    return df


@st.cache_data
def load_patients():
    con = sqlite3.connect("meditrack.db")
    df = pd.read_sql(
        """
        SELECT p.*, 
               MAX(a.appt_date) as last_visit,
               COUNT(a.appt_id) as total_visits,
               SUM(CASE WHEN a.status='completed' THEN a.fee_charged ELSE 0 END) as lifetime_value
        FROM patients p
        LEFT JOIN appointments a ON p.patient_id = a.patient_id
        GROUP BY p.patient_id
    """,
        con,
    )
    con.close()
    df["last_visit"] = pd.to_datetime(df["last_visit"])
    return df


df_all = load_data()
patients_df = load_patients()
max_date = df_all["appt_date"].max()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MediTrack")
    st.markdown("### Command Center")
    st.markdown("---")

    # Handle voice navigation from session state
    if "page_nav" in st.session_state and st.session_state.page_nav:
        default_page = st.session_state.page_nav
        st.session_state.page_nav = None  # Clear after use
    else:
        default_page = "Dashboard"

    st.markdown("**Navigation**")
    page = st.radio(
        "Go to",
        [
            "Dashboard",
            "Pakistan Map",
            "Clinic Floor",
            "Doctor Scorecards",
            "Intelligence Hub",
            "Campaign Builder",
            "Shift Intelligence",
            "City vs City",
            "Executive Summary",
        ],
        label_visibility="collapsed",
        index=[
            "Dashboard",
            "Pakistan Map",
            "Clinic Floor",
            "Doctor Scorecards",
            "Intelligence Hub",
            "Campaign Builder",
            "Shift Intelligence",
            "City vs City",
            "Executive Summary",
        ].index(default_page)
        if default_page
        in [
            "Dashboard",
            "Pakistan Map",
            "Clinic Floor",
            "Doctor Scorecards",
            "Intelligence Hub",
            "Campaign Builder",
            "Shift Intelligence",
            "City vs City",
            "Executive Summary",
        ]
        else 0,
    )
    st.markdown("---")
    cities = st.multiselect(
        "Filter: City",
        sorted(df_all.city.unique()),
        default=sorted(df_all.city.unique()),
        key="sidebar_city",
    )
    depts = st.multiselect(
        "Filter: Department",
        sorted(df_all.department.unique()),
        default=sorted(df_all.department.unique()),
        key="sidebar_dept",
    )
    st.markdown("---")
    st.markdown("**No-Show Predictor**")
    pred_dept = st.selectbox("Department", sorted(df_all.department.unique()), key="pd")
    pred_day = st.selectbox(
        "Day",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        key="pday",
    )
    pred_hour = st.slider("Hour", 8, 19, 10, key="ph")
    pred_new = st.radio("Patient", ["New", "Returning"], key="pn", horizontal=True)
    pred_snr = st.selectbox(
        "Seniority", ["Junior", "Mid", "Senior", "Consultant"], key="ps"
    )
    pred_city = st.selectbox("City", sorted(df_all.city.unique()), key="pc")
    predict_btn = st.button("Predict Risk", use_container_width=True)
    st.markdown("---")
    st.markdown("**🎤 Voice Navigation**")
    st.markdown("*Type command or use floating mic button*")

    # Voice command input with form
    with st.form("voice_form"):
        voice_input = st.text_input(
            "Voice command",
            key="voice_input",
            placeholder="e.g., dashboard, map, doctors...",
        )
        submit_btn = st.form_submit_button("Go ↵", use_container_width=True)

        if submit_btn and voice_input:
            cmd = voice_input.lower().strip()
            page_found = False

            if any(w in cmd for w in ["dashboard", "home", "main"]):
                st.session_state.page_nav = "Dashboard"
                page_found = True
            elif any(w in cmd for w in ["map", "pakistan", "geo"]):
                st.session_state.page_nav = "Pakistan Map"
                page_found = True
            elif any(w in cmd for w in ["clinic", "floor", "today", "queue"]):
                st.session_state.page_nav = "Clinic Floor"
                page_found = True
            elif any(w in cmd for w in ["doctor", "scorecard", "doctors"]):
                st.session_state.page_nav = "Doctor Scorecards"
                page_found = True
            elif any(w in cmd for w in ["intelligence", "analytics", "ai", "smart"]):
                st.session_state.page_nav = "Intelligence Hub"
                page_found = True
            elif any(w in cmd for w in ["campaign", "reminder", "outreach"]):
                st.session_state.page_nav = "Campaign Builder"
                page_found = True
            elif any(w in cmd for w in ["shift", "schedule", "timing"]):
                st.session_state.page_nav = "Shift Intelligence"
                page_found = True
            elif any(w in cmd for w in ["compare", "city", "benchmark", "versus"]):
                st.session_state.page_nav = "City vs City"
                page_found = True
            elif any(w in cmd for w in ["executive", "summary", "ceo", "report"]):
                st.session_state.page_nav = "Executive Summary"
                page_found = True

            if page_found:
                st.success(f"🎤 Navigating to: {st.session_state.page_nav}")

    # Floating mic button with better JS
    voice_js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const hasSpeechAPI = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        
        if (hasSpeechAPI) {
            const micBtn = document.createElement('button');
            micBtn.innerHTML = '🎤';
            micBtn.id = 'floating-mic';
            micBtn.title = 'Click to speak (Chrome/Edge/Brave)';
            micBtn.style.cssText = 'position:fixed; bottom:20px; right:20px; width:60px; height:60px; border-radius:50%; background:#0d9488; border:none; color:white; font-size:24px; cursor:pointer; box-shadow:0 4px 15px rgba(0,0,0,0.3); z-index:9999;';
            document.body.appendChild(micBtn);
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            
            let isListening = false;
            
            micBtn.onclick = function() {
                if (!isListening) {
                    isListening = true;
                    micBtn.style.background = '#ef4444';
                    recognition.start();
                }
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                // Find the voice input field by placeholder
                const inputs = document.querySelectorAll('input[type="text"]');
                const voiceInput = Array.from(inputs).find(i => i.placeholder && i.placeholder.includes('e.g.'));
                if (voiceInput) {
                    voiceInput.value = transcript;
                    voiceInput.focus();
                    micBtn.style.background = '#14ffec';
                    setTimeout(() => { 
                        micBtn.style.background = '#0d9488'; 
                        isListening = false;
                    }, 500);
                }
            };
            
            recognition.onerror = function() {
                micBtn.style.background = '#f59e0b';
                setTimeout(() => { 
                    micBtn.style.background = '#0d9488'; 
                    isListening = false;
                }, 1000);
            };
        }
    });
    </script>
    """
    st.markdown(voice_js, unsafe_allow_html=True)

# ── Filter data ───────────────────────────────────────────────────────────────
df = df_all[df_all.city.isin(cities) & df_all.department.isin(depts)].copy()


# ── Helper functions ──────────────────────────────────────────────────────────
def kpi(col, label, val, delta=None, fmt=None):
    if fmt == "money":
        display = f"₨{val:,.0f}"
    elif fmt == "pct":
        display = f"{val:.1f}%"
    else:
        display = f"{val:,}"
    delta_color = "var(--red)" if delta and delta < 0 else "#14ffec"
    dhtml = (
        f"<div style='color:{delta_color};font-size:.85rem;margin-top:4px;'>{delta:+.1f}% vs avg</div>"
        if delta is not None
        else ""
    )
    col.markdown(
        f"<div class='metric-card'><div class='metric-lbl'>{label}</div><div class='metric-val'>{display}</div>{dhtml}</div>",
        unsafe_allow_html=True,
    )


def get_city_revenue():
    return df[df.status == "completed"].groupby("city")["fee_charged"].sum().to_dict()


# ── Page routing ───────────────────────────────────────────────────────────────
if page == "Dashboard":
    st.markdown("# 📊 MediTrack Command Center")
    st.markdown(
        f"<span style='color:var(--text-muted)'>Live operations · {max_date.strftime('%Y-%m-%d')} · {len(df):,} appointments</span>",
        unsafe_allow_html=True,
    )

    # KPI Row
    total_rev = df[df.status == "completed"].fee_charged.sum()
    completed_r = (df.status == "completed").mean() * 100
    noshows_r = (df.status == "no_show").mean() * 100
    avg_fee = df[df.status == "completed"].fee_charged.mean()
    total_appts = len(df)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi(k1, "Total Appointments", total_appts)
    kpi(k2, "Total Revenue", total_rev, fmt="money")
    kpi(k3, "Completion Rate", completed_r, fmt="pct")
    kpi(k4, "No-Show Rate", noshows_r, fmt="pct")
    kpi(k5, "Avg Fee", avg_fee, fmt="money")

    # Revenue by City
    st.markdown(
        "<div class='section-head'>Revenue by City</div>", unsafe_allow_html=True
    )
    rev_city = (
        df[df.status == "completed"]
        .groupby("city")["fee_charged"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig = px.bar(
        rev_city,
        x="city",
        y="fee_charged",
        color="fee_charged",
        color_continuous_scale=["#0d2626", "#0d9488", "#14ffec"],
        title="",
        labels={"fee_charged": "Revenue (₨)", "city": ""},
    )
    fig.update_layout(
        plot_bgcolor="#0a0f0d",
        paper_bgcolor="#0a0f0d",
        font_family="DM Sans",
        font_color="#e2e8f0",
        coloraxis_showscale=False,
        margin=dict(t=20, b=40),
        yaxis=dict(gridcolor="#1e3a35", tickfont=dict(color="#94a3b8")),
        xaxis=dict(tickfont=dict(color="#94a3b8")),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Trend
    st.markdown(
        "<div class='section-head'>Appointment Volume Trend</div>",
        unsafe_allow_html=True,
    )
    vol = (
        df.groupby("month")
        .agg(
            total=("appt_id", "count"),
            completed=("status", lambda x: (x == "completed").sum()),
        )
        .reset_index()
    )
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=vol.month,
            y=vol.total,
            name="All",
            line=dict(color="#0a6b68", width=2),
            fill="tozeroy",
            fillcolor="rgba(13,148,136,0.1)",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=vol.month,
            y=vol.completed,
            name="Completed",
            line=dict(color="#14ffec", width=3),
        )
    )
    fig2.update_layout(
        plot_bgcolor="#0a0f0d",
        paper_bgcolor="#0a0f0d",
        font_family="DM Sans",
        font_color="#e2e8f0",
        legend=dict(orientation="h", y=1.1, font=dict(color="#94a3b8")),
        margin=dict(t=20, b=40),
        yaxis=dict(gridcolor="#1e3a35", tickfont=dict(color="#94a3b8")),
        xaxis=dict(tickfont=dict(color="#94a3b8")),
    )
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Pakistan Map":
    st.markdown("# 🗺️ Pakistan Clinic Network")
    st.markdown(
        "<span style='color:var(--text-muted)'>Select a city to view individual clinics on OpenStreetMap</span>",
        unsafe_allow_html=True,
    )

    # City center coordinates and zoom levels
    city_centers = {
        "All": {"center": [30, 70], "zoom": 5},
        "Karachi": {"center": [24.86, 67.01], "zoom": 12},
        "Lahore": {"center": [31.55, 74.35], "zoom": 12},
        "Islamabad": {"center": [33.72, 73.06], "zoom": 12},
        "Peshawar": {"center": [34.01, 71.57], "zoom": 12},
        "Multan": {"center": [30.20, 71.47], "zoom": 12},
    }

    # City dropdown
    selected_city = st.selectbox(
        "Select City", list(city_centers.keys()), key="map_city_select"
    )

    # Get clinic-level data from database
    con = sqlite3.connect("meditrack.db")
    clinic_df = pd.read_sql(
        """
        SELECT c.clinic_name, c.city, c.clinic_id, 
               COUNT(a.appt_id) as appointments,
               SUM(CASE WHEN a.status='completed' THEN a.fee_charged ELSE 0 END) as revenue,
               SUM(CASE WHEN a.status='completed' THEN 1 ELSE 0 END) as completed
        FROM clinics c
        LEFT JOIN appointments a ON c.clinic_id = a.clinic_id
        GROUP BY c.clinic_id
    """,
        con,
    )
    con.close()

    # Filter by selected city
    if selected_city != "All":
        clinic_df = clinic_df[clinic_df.city == selected_city]

    clinic_df["completion_rate"] = (
        clinic_df["completed"] / clinic_df["appointments"] * 100
    ).round(1)

    # Add approximate coordinates (using city center + random offset)
    np.random.seed(42)
    city_offsets = {
        "All": (30, 70),
        "Karachi": (24.86, 67.01),
        "Lahore": (31.55, 74.35),
        "Islamabad": (33.72, 73.06),
        "Peshawar": (34.01, 71.57),
        "Multan": (30.20, 71.47),
    }

    base_center = city_offsets.get(selected_city, (30, 70))
    clinic_df["lat"] = base_center[0] + np.random.uniform(-0.05, 0.05, len(clinic_df))
    clinic_df["lon"] = base_center[1] + np.random.uniform(-0.05, 0.05, len(clinic_df))

    # Get center and zoom for selected city
    center = city_centers[selected_city]["center"]
    zoom = city_centers[selected_city]["zoom"]

    # Create Folium map with OpenStreetMap tiles
    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

    # Add clinic markers
    for _, clinic in clinic_df.iterrows():
        # Color based on revenue
        if clinic["revenue"] > 5000000:
            color = "darkgreen"
            icon = "star"
        elif clinic["revenue"] > 1000000:
            color = "green"
            icon = "plus"
        elif clinic["revenue"] > 500000:
            color = "orange"
            icon = "minus"
        else:
            color = "red"
            icon = "home"

        popup_html = f"""
        <div style="width:200px;">
            <h4>{clinic["clinic_name"]}</h4>
            <b>City:</b> {clinic["city"]}<br>
            <b>Revenue:</b> ₨{clinic["revenue"]:,.0f}<br>
            <b>Appointments:</b> {clinic["appointments"]}<br>
            <b>Completion:</b> {clinic["completion_rate"]}%
        </div>
        """

        folium.Marker(
            location=[clinic["lat"], clinic["lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=clinic["clinic_name"],
            icon=folium.Icon(color=color, icon=icon),
        ).add_to(m)

    # Display the map
    st_folium(m, width=800, height=500)

    # Right panel with clinic stats
    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown(f"### {selected_city} Clinics")
        total_rev = clinic_df["revenue"].sum()
        total_appts = clinic_df["appointments"].sum()
        st.metric("Total Revenue", f"₨{total_rev / 1e6:.1f}M")
        st.metric("Appointments", f"{total_appts:,}")
        st.markdown("---")
        for _, row in clinic_df.iterrows():
            st.markdown(
                f"""
                <div class="metric-card" style="padding:10px 14px;margin:6px 0;">
                    <div style="font-weight:600;color:#ccfbf1;font-size:0.9rem;">{row["clinic_name"]}</div>
                    <div style="display:flex;justify-content:space-between;margin-top:4px;">
                        <span style="color:#0d9488;">₨{row["revenue"] / 1e6:.1f}M</span>
                        <span style="color:#94a3b8;">{row["appointments"]} appts</span>
                        <span style="color:#14ffec;">{row["completion_rate"]}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

elif page == "Clinic Floor":
    st.markdown("# 🏥 Today's Clinic Floor")
    st.markdown(
        "<span style='color:var(--text-muted)'>Real-time appointment queue</span>",
        unsafe_allow_html=True,
    )

    today = max_date.strftime("%Y-%m-%d")
    today_df = df[df.appt_date.dt.strftime("%Y-%m-%d") == today]

    if today_df.empty:
        st.warning("No appointments today in selected filters")
    else:
        clinics = today_df.groupby("clinic_name")
        for clinic_name, clinic_data in clinics:
            st.markdown(f"### {clinic_name}")
            cols = st.columns(4)
            for i, (_, row) in enumerate(clinic_data.iterrows()):
                status_class = (
                    "floor-completed"
                    if row["status"] == "completed"
                    else "floor-pending"
                    if row["status"] == "scheduled"
                    else "floor-noshow"
                )
                time = row["appt_time"]
                with cols[i % 4]:
                    st.markdown(
                        f"""
                    <div class="floor-card {status_class}">
                        <div style="font-size:0.85rem;color:var(--text-muted);">{time}</div>
                        <div style="font-weight:600;color:var(--teal-light);">{row["doctor_name"]}</div>
                        <div style="font-size:0.8rem;color:var(--text-dim);">{row["department"]}</div>
                        <div style="font-size:0.75rem;margin-top:4px;color:{"#14ffec" if row["status"] == "completed" else "var(--amber)" if row["status"] == "scheduled" else "var(--red)"};">{row["status"].upper()}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            st.markdown("---")

elif page == "Doctor Scorecards":
    st.markdown("# 👨‍⚕️ Doctor Scorecards")
    st.markdown(
        "<span style='color:var(--text-muted)'>Performance radar across 5 dimensions</span>",
        unsafe_allow_html=True,
    )

    doc_stats = (
        df.groupby(["doctor_name", "department", "city"])
        .agg(
            total=("appt_id", "count"),
            completed=("status", lambda x: (x == "completed").sum()),
            no_shows=("status", lambda x: (x == "no_show").sum()),
            revenue=("fee_charged", "sum"),
            avg_fee=("fee_charged", "mean"),
        )
        .reset_index()
    )
    doc_stats["completion_rate"] = doc_stats["completed"] / doc_stats["total"] * 100
    doc_stats["no_show_rate"] = doc_stats["no_shows"] / doc_stats["total"] * 100

    patient_visits = df.groupby("doctor_name")["patient_id"].nunique().reset_index()
    patient_visits.columns = ["doctor_name", "unique_patients"]
    doc_stats = doc_stats.merge(patient_visits, on="doctor_name")
    doc_stats["retention"] = (
        doc_stats["completed"] / doc_stats["unique_patients"]
    ).clip(0, 100)

    doc_stats = (
        doc_stats[doc_stats.total >= 20]
        .sort_values("revenue", ascending=False)
        .head(12)
    )

    for i in range(0, len(doc_stats), 3):
        cols = st.columns(3)
        for j, (_, row) in enumerate(doc_stats.iloc[i : i + 3].iterrows()):
            with cols[j]:
                categories = [
                    "Completion",
                    "Revenue",
                    "No-Show",
                    "Retention",
                    "Avg Fee",
                ]
                values = [
                    row["completion_rate"] / 100,
                    min(row["revenue"] / doc_stats["revenue"].max(), 1),
                    1 - row["no_show_rate"] / 100,
                    row["retention"] / 100,
                    row["avg_fee"] / doc_stats["avg_fee"].max(),
                ]

                fig = go.Figure()
                fig.add_trace(
                    go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill="toself",
                        line_color="#14ffec",
                        fillcolor="rgba(20,255,236,0.3)",
                        name=row["doctor_name"],
                    )
                )
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1],
                            tickfont=dict(color="#94a3b8"),
                            gridcolor="#1e3a35",
                        ),
                        bgcolor="#0a0f0d",
                    ),
                    paper_bgcolor="#0a0f0d",
                    margin=dict(t=30, b=20, l=20, r=20),
                    height=250,
                    showlegend=False,
                    title=dict(
                        text=f"{row['doctor_name']}<br><span style='font-size:10px;color:#64748b'>{row['department']} · {row['city']}</span>",
                        font=dict(color="#ccfbf1", size=14),
                    ),
                )
                st.plotly_chart(fig, use_container_width=True)

elif page == "Intelligence Hub":
    st.markdown("# 🧠 Intelligence Hub")
    st.markdown(
        "<span style='color:var(--text-muted)'>Smart predictions & anomaly detection</span>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "📈 Reminder ROI",
            "⚠️ Churn Detection",
            "🔥 Doctor Burnout",
            "🦠 Seasonal Patterns",
            "🚨 Anomaly Detection",
            "💰 Revenue Alerts",
        ]
    )

    with tab1:
        st.markdown("### Reminder ROI Calculator")
        remind_count = st.number_input("Patients to remind", 10, 5000, 100)

        historical_ns = df[df.status == "no_show"].shape[0] / len(df) * 100
        avg_fee = df[df.status == "completed"]["fee_charged"].mean()

        recovered = remind_count * (historical_ns / 100) * 0.5
        revenue_saved = recovered * avg_fee

        st.markdown(
            f"""
        <div class="info-box">
            <div style="font-size:1.5rem;color:var(--teal-neon);font-weight:700;">{int(recovered)} patients</div>
            <div style="color:var(--text-muted);">Estimated no-shows recovered (50% reminder success)</div>
            <div style="font-size:2rem;color:var(--teal-neon);font-weight:700;margin-top:12px;">₨{revenue_saved:,.0f}</div>
            <div style="color:var(--text-muted);">Estimated revenue saved</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with tab2:
        st.markdown("### Churn Detection (90+ Days)")
        cutoff_date = max_date - timedelta(days=90)
        churned = patients_df[
            (patients_df.last_visit.notna()) & (patients_df.last_visit < cutoff_date)
        ].copy()
        churned["days_since"] = (max_date - churned["last_visit"]).dt.days
        churned["est_lifetime_visits"] = (
            churned["total_visits"]
            / ((max_date - churned["last_visit"]).dt.days / 365).replace(0, 1)
        ).clip(0, 50)
        churned["est_ltv"] = (
            churned["est_lifetime_visits"]
            * churned["lifetime_value"]
            / churned["total_visits"].replace(0, 1)
        )

        st.metric("Churned Patients", len(churned))
        st.metric("Estimated Lost LTV", f"₨{churned['est_ltv'].sum():,.0f}")

        st.dataframe(
            churned.sort_values("days_since", ascending=False)
            .head(10)[["name", "city", "days_since", "total_visits", "lifetime_value"]]
            .assign(est_ltv=lambda x: x["lifetime_value"]),
            use_container_width=True,
        )

    with tab3:
        st.markdown("### Doctor Burnout Signal")
        weekly_docs = (
            df.groupby(["doctor_name", "year", "week"])
            .size()
            .reset_index(name="appointments")
        )
        avg_weekly = (
            weekly_docs.groupby("doctor_name")["appointments"].mean().reset_index()
        )
        avg_weekly.columns = ["doctor_name", "avg_weekly"]
        avg_weekly = avg_weekly.sort_values("avg_weekly", ascending=False)

        burnout_thresh = 40
        overloaded = avg_weekly[avg_weekly.avg_weekly >= burnout_thresh]

        st.metric("Doctors Monitored", len(avg_weekly))
        st.metric("Overloaded (40+ appts/week)", len(overloaded))

        fig = px.bar(
            avg_weekly.head(15),
            x="avg_weekly",
            y="doctor_name",
            orientation="h",
            color="avg_weekly",
            color_continuous_scale=["#0d2626", "#f59e0b", "#ef4444"],
            title="Appointments per Doctor per Week",
        )
        fig.update_layout(
            plot_bgcolor="#0a0f0d",
            paper_bgcolor="#0a0f0d",
            font_color="#e2e8f0",
            coloraxis_showscale=False,
            yaxis=dict(tickfont=dict(color="#94a3b8")),
            xaxis=dict(gridcolor="#1e3a35", tickfont=dict(color="#94a3b8")),
            margin=dict(t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        if not overloaded.empty:
            st.markdown(
                f"""
            <div class="alert-box">
                <strong>⚠️ Burnout Warning</strong><br>
                {len(overloaded)} doctor(s) exceed {burnout_thresh} appointments/week. Consider adding support or adjusting schedules.
            </div>
            """,
                unsafe_allow_html=True,
            )

    with tab4:
        st.markdown("### Seasonal Illness Patterns")
        seasonal_months = ["10", "11", "12", "01", "02"]
        df["month_num"] = df["appt_date"].dt.month
        seasonal = (
            df[df.month_num.isin([10, 11, 12, 1, 2])]
            .groupby(["month", "department"])
            .size()
            .reset_index(name="count")
        )
        non_seasonal = (
            df[~df.month_num.isin([10, 11, 12, 1, 2])]
            .groupby("department")
            .size()
            .reset_index(name="avg_monthly")
        )

        pediatrics = (
            df[df.department.isin(["Pediatrics", "General"])]
            .groupby("month")
            .size()
            .reset_index(name="count")
        )
        fig = px.line(
            pediatrics,
            x="month",
            y="count",
            title="Pediatrics/General Volume by Month (Flu Season Highlighted)",
            markers=True,
        )
        fig.add_vrect(
            x0="2024-10",
            x1="2025-02",
            fillcolor="rgba(239,68,68,0.1)",
            opacity=0.5,
            line_width=0,
            annotation_text="Flu Season",
            annotation_position="top left",
        )
        fig.update_layout(
            plot_bgcolor="#0a0f0d",
            paper_bgcolor="#0a0f0d",
            font_color="#e2e8f0",
            margin=dict(t=30, b=40),
            yaxis=dict(gridcolor="#1e3a35", tickfont=dict(color="#94a3b8")),
            xaxis=dict(tickfont=dict(color="#94a3b8")),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.markdown("### Anomaly Detection")
        daily_ns = (
            df.groupby("appt_date")
            .agg(
                total=("appt_id", "count"),
                no_shows=("status", lambda x: (x == "no_show").sum()),
            )
            .reset_index()
        )
        daily_ns["ns_rate"] = daily_ns["no_shows"] / daily_ns["total"] * 100
        mean_ns = daily_ns["ns_rate"].mean()
        std_ns = daily_ns["ns_rate"].std()
        threshold = mean_ns + 2 * std_ns
        anomalies = daily_ns[daily_ns["ns_rate"] > threshold]

        st.metric("Days Analyzed", len(daily_ns))
        st.metric(
            "Anomalous Days",
            len(anomalies),
            delta=f"{len(anomalies) / len(daily_ns) * 100:.1f}%",
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=daily_ns["appt_date"],
                y=daily_ns["ns_rate"],
                mode="lines+markers",
                line=dict(color="#0d9488", width=2),
                name="Daily Rate",
            )
        )
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="#ef4444",
            annotation_text="2 Std Dev",
        )
        fig.add_hline(
            y=mean_ns,
            line_dash="dot",
            line_color="#14ffec",
            annotation_text="Mean",
        )
        fig.update_layout(
            title="Daily No-Show Rate with Anomaly Detection",
            plot_bgcolor="#0a0f0d",
            paper_bgcolor="#0a0f0d",
            font_color="#e2e8f0",
            yaxis=dict(gridcolor="#1e3a35", tickfont=dict(color="#94a3b8")),
            xaxis=dict(tickfont=dict(color="#94a3b8")),
            margin=dict(t=30, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        if not anomalies.empty:
            st.markdown("### 🚨 What Happened?")
            for _, row in anomalies.iterrows():
                st.markdown(
                    f"""
                <div class="alert-box">
                    <strong>{row["appt_date"].strftime("%Y-%m-%d")}</strong>: {row["ns_rate"]:.1f}% no-show rate (vs {mean_ns:.1f}% avg)<br>
                    <span style="color:var(--text-muted)">{row["no_shows"]} no-shows out of {row["total"]} appointments</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with tab6:
        st.markdown("### Revenue Alerts (MoM Drop >20%)")
        clinic_rev = (
            df[df.status == "completed"]
            .groupby(["clinic_name", "month"])["fee_charged"]
            .sum()
            .reset_index()
        )
        clinic_rev = clinic_rev.sort_values(["clinic_name", "month"])
        clinic_rev["prev_month"] = clinic_rev.groupby("clinic_name")[
            "fee_charged"
        ].shift(1)
        clinic_rev["pct_change"] = (
            (clinic_rev["fee_charged"] - clinic_rev["prev_month"])
            / clinic_rev["prev_month"]
            * 100
        )
        alerts = clinic_rev[clinic_rev["pct_change"] < -20].dropna()

        st.metric("Clinics Monitored", df.clinic_name.nunique())
        st.metric("Revenue Alerts", len(alerts))

        if not alerts.empty:
            for _, row in alerts.iterrows():
                st.markdown(
                    f"""
                <div class="alert-box">
                    <strong>🏥 {row["clinic_name"]}</strong><br>
                    <span style="color:var(--teal-neon);font-size:1.2rem;">{row["pct_change"]:.1f}% MoM</span> drop<br>
                    <span style="color:var(--text-muted)">₨{row["prev_month"]:,.0f} → ₨{row["fee_charged"]:,.0f}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

elif page == "Campaign Builder":
    st.markdown("# 📢 Reminder Campaign Builder")
    st.markdown(
        "<span style='color:var(--text-muted)'>Generate patient list for outreach</span>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        start_date = st.date_input("Start Date", max_date - timedelta(days=30))
    with c2:
        end_date = st.date_input("End Date", max_date)
    with c3:
        risk_threshold = st.slider("Min Risk Score %", 0, 100, 30)

    campaign_df = df[
        (df.appt_date >= pd.to_datetime(start_date))
        & (df.appt_date <= pd.to_datetime(end_date))
    ].copy()

    patient_ns_rate = (
        df.groupby("patient_id")["status"]
        .apply(lambda x: (x == "no_show").mean() * 100)
        .reset_index()
    )
    patient_ns_rate.columns = ["patient_id", "no_show_rate"]
    campaign_df = campaign_df.merge(patient_ns_rate, on="patient_id", how="left")
    campaign_df["no_show_rate"] = campaign_df["no_show_rate"].fillna(15)

    campaign_df["risk_score"] = np.where(
        campaign_df["is_new_patient"] == 1,
        campaign_df["no_show_rate"] * 1.5,
        campaign_df["no_show_rate"],
    )

    patients = (
        campaign_df.groupby("patient_id")
        .agg(
            patient_id=("patient_id", "first"),
            city=("city", "first"),
            department=("department", "first"),
            no_show_rate=("no_show_rate", "first"),
            upcoming=("appt_id", "count"),
        )
        .reset_index(drop=True)
    )

    patients_info = load_patients()[["patient_id", "name"]]
    patients = patients.merge(patients_info, on="patient_id", how="left")

    patients["risk_score"] = patients["no_show_rate"].fillna(15) * np.where(
        patients["upcoming"] > 3, 1.2, 1
    )

    filtered = patients[patients["risk_score"] >= risk_threshold]

    st.metric("Total Patients", len(patients))
    st.metric(f"High Risk (≥{risk_threshold}%)", len(filtered))

    st.dataframe(filtered.head(20), use_container_width=True)

    csv = filtered.to_csv(index=False)
    st.download_button(
        "📥 Download Campaign CSV", csv, "reminder_campaign.csv", "text/csv"
    )

elif page == "Shift Intelligence":
    st.markdown("# ⏰ Shift Intelligence")
    st.markdown(
        "<span style='color:var(--text-muted)'>Optimize doctor scheduling</span>",
        unsafe_allow_html=True,
    )

    hourly = (
        df.groupby(["clinic_name", "appt_hour"]).size().reset_index(name="appointments")
    )
    clinic_totals = df.groupby("clinic_name").size().reset_index(name="total")
    hourly = hourly.merge(clinic_totals, on="clinic_name")
    hourly["utilization"] = (
        hourly["appointments"] / (hourly["total"] / (df.appt_hour.nunique())) * 100
    )

    st.markdown("### Underbooked Slots by Clinic")
    underbooked = hourly[hourly["utilization"] < 30].sort_values("utilization")

    if not underbooked.empty:
        fig = px.scatter(
            underbooked,
            x="appt_hour",
            y="utilization",
            color="clinic_name",
            size="appointments",
            title="Underutilized Hour Slots (<30%)",
        )
        fig.update_layout(
            plot_bgcolor="#0a0f0d",
            paper_bgcolor="#0a0f0d",
            font_color="#e2e8f0",
            yaxis=dict(gridcolor="#1e3a35", tickfont=dict(color="#94a3b8")),
            xaxis=dict(tickfont=dict(color="#94a3b8"), title="Hour of Day"),
            margin=dict(t=30, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Recommendations")
        for clinic in underbooked.clinic_name.unique():
            clinic_slots = underbooked[underbooked.clinic_name == clinic]
            st.markdown(
                f"**{clinic}**: Consider reducing hours at {', '.join(map(str, clinic_slots['appt_hour'].tolist()))}:00"
            )
    else:
        st.success("All clinics have well-utilized schedules!")

    st.markdown("### Peak Hours Analysis")
    peak = df.groupby("appt_hour").size().reset_index(name="count")
    fig = px.bar(
        peak,
        x="appt_hour",
        y="count",
        title="Appointments by Hour",
        color="count",
        color_continuous_scale=["#0d2626", "#0d9488", "#14ffec"],
    )
    fig.update_layout(
        plot_bgcolor="#0a0f0d",
        paper_bgcolor="#0a0f0d",
        font_color="#e2e8f0",
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="#1e3a35", tickfont=dict(color="#94a3b8")),
        xaxis=dict(tickfont=dict(color="#94a3b8"), title="Hour"),
        margin=dict(t=30, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "City vs City":
    st.markdown("# 🏆 City vs City Benchmarking")
    st.markdown(
        "<span style='color:var(--text-muted)'>Head-to-head comparison</span>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        city1 = st.selectbox(
            "City 1", sorted(df_all.city.unique()), index=0, key="city1"
        )
    with c2:
        city2 = st.selectbox(
            "City 2", sorted(df_all.city.unique()), index=1, key="city2"
        )

    def get_city_metrics(city):
        cdf = df[df.city == city]
        return {
            "appointments": len(cdf),
            "revenue": cdf[cdf.status == "completed"]["fee_charged"].sum(),
            "completion": (cdf.status == "completed").mean() * 100,
            "noshow": (cdf.status == "no_show").mean() * 100,
            "clinics": cdf.clinic_name.nunique(),
            "doctors": cdf.doctor_name.nunique(),
            "avg_fee": cdf[cdf.status == "completed"]["fee_charged"].mean(),
        }

    m1 = get_city_metrics(city1)
    m2 = get_city_metrics(city2)

    st.markdown("### Performance Comparison")
    metrics = [
        "appointments",
        "revenue",
        "completion",
        "noshow",
        "clinics",
        "doctors",
        "avg_fee",
    ]
    labels = [
        "Appointments",
        "Revenue",
        "Completion %",
        "No-Show %",
        "Clinics",
        "Doctors",
        "Avg Fee",
    ]

    cols = st.columns(len(metrics))
    for i, (m, l) in enumerate(zip(metrics, labels)):
        v1, v2 = m1[m], m2[m]
        winner = (
            "▲"
            if (
                m in ["completion", "revenue", "clinics", "doctors", "avg_fee"]
                and v1 > v2
            )
            or (m == "noshow" and v1 < v2)
            else "▼"
        )
        color = "#14ffec" if winner == "▲" else "var(--red)"

        if m in ["revenue", "avg_fee"]:
            fmt = f"₨{v1:,.0f}"
            fmt2 = f"₨{v2:,.0f}"
        elif m in ["completion", "noshow"]:
            fmt = f"{v1:.1f}%"
            fmt2 = f"{v2:.1f}%"
        else:
            fmt = f"{v1:,}"
            fmt2 = f"{v2:,}"

        with cols[i]:
            st.markdown(
                f"""
            <div class="metric-card" style="padding:16px;text-align:center;">
                <div style="font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;">{l}</div>
                <div style="font-size:1.5rem;color:var(--teal-neon);font-weight:700;">{fmt}</div>
                <div style="font-size:1rem;color:var(--text-muted);">{fmt2}</div>
                <div style="font-size:1.2rem;color:{color};">{winner}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("### Department Comparison")
    d1 = df[df.city == city1].groupby("department").size().reset_index(name=city1)
    d2 = df[df.city == city2].groupby("department").size().reset_index(name=city2)
    dept_comp = d1.merge(d2, on="department", how="outer").fillna(0)

    fig = go.Figure(
        data=[
            go.Bar(
                name=city1,
                x=dept_comp.department,
                y=dept_comp[city1],
                marker_color="#0d9488",
            ),
            go.Bar(
                name=city2,
                x=dept_comp.department,
                y=dept_comp[city2],
                marker_color="#14ffec",
            ),
        ]
    )
    fig.update_layout(
        barmode="group",
        plot_bgcolor="#0a0f0d",
        paper_bgcolor="#0a0f0d",
        font_color="#e2e8f0",
        margin=dict(t=30, b=40),
        legend=dict(font=dict(color="#94a3b8")),
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Executive Summary":
    st.markdown("# 📋 Executive One-Pager")
    st.markdown(
        "<span style='color:var(--text-muted)'>CEO-ready snapshot · Printable</span>",
        unsafe_allow_html=True,
    )

    # Key metrics
    total_rev = df[df.status == "completed"].fee_charged.sum()
    completed_r = (df.status == "completed").mean() * 100
    noshows_r = (df.status == "no_show").mean() * 100
    avg_fee = df[df.status == "completed"]["fee_charged"].mean()
    top_city = (
        df[df.status == "completed"].groupby("city")["fee_charged"].sum().idxmax()
    )
    top_dept = (
        df[df.status == "completed"].groupby("department")["fee_charged"].sum().idxmax()
    )
    total_patients = df.patient_id.nunique()
    total_doctors = df.doctor_name.nunique()

    # Calculate YoY if we have data
    year_revs = df[df.status == "completed"].groupby("year")["fee_charged"].sum()
    yoy_growth = (
        ((year_revs.iloc[-1] - year_revs.iloc[0]) / year_revs.iloc[0] * 100)
        if len(year_revs) > 1
        else 0
    )

    st.markdown(
        """
    <style>
    .exec-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;}
    .exec-card{
        background:linear-gradient(135deg,var(--bg-card) 0%,#0f1f1c 100%);
        border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center;
    }
    .exec-val{font-size:2rem;font-weight:700;color:var(--teal-neon);}
    .exec-lbl{font-size:0.8rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.1em;}
    .exec-delta{font-size:0.9rem;margin-top:4px;}
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="exec-grid">
        <div class="exec-card">
            <div class="exec-lbl">Total Revenue</div>
            <div class="exec-val">₨{total_rev / 1e6:.1f}M</div>
            <div class="exec-delta" style="color:var(--teal-neon)">+{yoy_growth:.1f}% YoY</div>
        </div>
        <div class="exec-card">
            <div class="exec-lbl">Completion Rate</div>
            <div class="exec-val">{completed_r:.1f}%</div>
            <div class="exec-delta" style="color:var(--text-muted)">of appointments</div>
        </div>
        <div class="exec-card">
            <div class="exec-lbl">No-Show Rate</div>
            <div class="exec-val">{noshows_r:.1f}%</div>
            <div class="exec-delta" style="color:var(--text-muted)">of appointments</div>
        </div>
        <div class="exec-card">
            <div class="exec-lbl">Avg Fee</div>
            <div class="exec-val">₨{avg_fee:,.0f}</div>
            <div class="exec-delta" style="color:var(--text-muted)">per visit</div>
        </div>
    </div>
    <div class="exec-grid">
        <div class="exec-card">
            <div class="exec-lbl">Top City</div>
            <div class="exec-val" style="font-size:1.5rem">{top_city}</div>
            <div class="exec-delta" style="color:var(--text-muted)">by revenue</div>
        </div>
        <div class="exec-card">
            <div class="exec-lbl">Top Department</div>
            <div class="exec-val" style="font-size:1.5rem">{top_dept}</div>
            <div class="exec-delta" style="color:var(--text-muted)">by revenue</div>
        </div>
        <div class="exec-card">
            <div class="exec-lbl">Patients</div>
            <div class="exec-val">{total_patients:,}</div>
            <div class="exec-delta" style="color:var(--text-muted)">unique</div>
        </div>
        <div class="exec-card">
            <div class="exec-lbl">Doctors</div>
            <div class="exec-val">{total_doctors}</div>
            <div class="exec-delta" style="color:var(--text-muted)">active</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Mini charts
    c1, c2 = st.columns(2)
    with c1:
        rev_trend = (
            df[df.status == "completed"]
            .groupby("month")["fee_charged"]
            .sum()
            .reset_index()
        )
        fig = px.line(rev_trend, x="month", y="fee_charged", title="Revenue Trend")
        fig.update_layout(
            plot_bgcolor="#0a0f0d",
            paper_bgcolor="#0a0f0d",
            font_color="#e2e8f0",
            margin=dict(t=20, b=30),
            yaxis=dict(tickformat="₨{:.0f}", gridcolor="#1e3a35"),
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        dept_rev = (
            df[df.status == "completed"]
            .groupby("department")["fee_charged"]
            .sum()
            .reset_index()
            .sort_values("fee_charged", ascending=True)
            .tail(5)
        )
        fig = px.barh(
            dept_rev, x="fee_charged", y="department", title="Top Departments"
        )
        fig.update_layout(
            plot_bgcolor="#0a0f0d",
            paper_bgcolor="#0a0f0d",
            font_color="#e2e8f0",
            margin=dict(t=20, b=30),
            xaxis=dict(gridcolor="#1e3a35"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center;color:var(--text-dim);font-size:0.8rem;'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} · MediTrack Command Center</div>",
        unsafe_allow_html=True,
    )

# ── No-Show Predictor ──────────────────────────────────────────────────────────
if predict_btn:
    st.markdown("### 🔮 No-Show Risk Prediction")
    try:
        bundle = pickle.load(open("noshowmodel.pkl", "rb"))
        model = bundle["model"]
        encoders = bundle["encoders"]

        inp = pd.DataFrame(
            [
                {
                    "appt_hour": pred_hour,
                    "is_new_patient": 1 if pred_new == "New" else 0,
                    "day_of_week_enc": encoders["day_of_week"].transform([pred_day])[0],
                    "department_enc": encoders["department"].transform([pred_dept])[0],
                    "seniority_enc": encoders["seniority"].transform([pred_snr])[0],
                    "city_enc": encoders["city"].transform([pred_city])[0],
                }
            ]
        )
        proba = model.predict_proba(inp)[0][1] * 100

        color = (
            "var(--red)" if proba > 30 else "var(--amber)" if proba > 15 else "#14ffec"
        )
        level = (
            "HIGH RISK 🔴"
            if proba > 30
            else "MODERATE ⚠️"
            if proba > 15
            else "LOW RISK ✅"
        )
        st.markdown(
            f"""
        <div style='background:var(--bg-card);border:1px solid {color.replace("var(", "var(--").replace(")", ");")};border-radius:16px;padding:24px;max-width:400px;'>
            <div style='font-family:DM Serif Display;font-size:1.2rem;color:var(--teal-light);margin-bottom:8px;'>
                Predicted No-Show Probability
            </div>
            <div style='font-size:3rem;font-weight:700;color:{color};'>{proba:.1f}%</div>
            <div style='font-size:1rem;color:{color};font-family:DM Sans;margin-top:4px;'>{level}</div>
            <hr style='border-color:var(--border);margin:12px 0;'>
            <div style='font-size:.85rem;color:var(--text-muted);font-family:DM Sans;'>
                {pred_dept} · {pred_day} {pred_hour:02d}:00 · {pred_snr} · {pred_new} · {pred_city}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if proba > 25:
            st.info(
                "💡 **Reminder recommended** — Send SMS/WhatsApp reminder 24h and 2h before appointment."
            )
    except FileNotFoundError:
        st.error("Model not found. Run `python train_model.py` first.")
