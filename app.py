import sqlite3, pickle
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediTrack Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{
  --teal:#0d9488; --teal-light:#ccfbf1; --teal-dark:#134e4a;
  --red:#ef4444;  --amber:#f59e0b; --sky:#0ea5e9;
  --bg:#f0fdf9;   --card:#ffffff;  --border:#d1fae5;
  --text:#0f3832; --muted:#6b7280;
}
html,body,[class*="css"]{background:var(--bg)!important;color:var(--text);}
h1,h2,h3{font-family:'DM Serif Display',serif;}
p,div,span,label{font-family:'DM Sans',sans-serif;}
.metric-card{
  background:var(--card);border:1px solid var(--border);border-radius:16px;
  padding:20px 24px;box-shadow:0 2px 12px rgba(13,148,136,.08);
}
.metric-val{font-size:2.2rem;font-weight:600;color:var(--teal-dark);line-height:1.1;}
.metric-lbl{font-size:.8rem;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;}
.metric-delta{font-size:.85rem;margin-top:4px;}
.section-head{
  font-family:'DM Serif Display',serif;font-size:1.35rem;
  color:var(--teal-dark);border-left:4px solid var(--teal);
  padding-left:12px;margin:24px 0 12px;
}
div[data-testid="stSidebar"]{background:#134e4a!important;}
div[data-testid="stSidebar"] *{color:#ccfbf1!important;}
div[data-testid="stSidebar"] .stSelectbox label,
div[data-testid="stSidebar"] .stMultiSelect label{color:#ccfbf1!important;}
</style>
""", unsafe_allow_html=True)

# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    con = sqlite3.connect("meditrack.db")
    df = pd.read_sql("""
        SELECT a.*, d.name doctor_name, d.department, d.seniority,
               c.city, c.clinic_name
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN clinics c ON a.clinic_id = c.clinic_id
    """, con)
    con.close()
    df["appt_date"] = pd.to_datetime(df["appt_date"])
    df["month"]     = df["appt_date"].dt.to_period("M").astype(str)
    df["appt_hour"] = df["appt_time"].str[:2].astype(int)
    return df

df_all = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MediTrack")
    st.markdown("---")
    cities = st.multiselect("City", sorted(df_all.city.unique()), default=sorted(df_all.city.unique()))
    depts  = st.multiselect("Department", sorted(df_all.department.unique()), default=sorted(df_all.department.unique()))
    months = sorted(df_all.month.unique())
    date_range = st.select_slider("Month Range", options=months, value=(months[0], months[-1]))
    st.markdown("---")
    st.markdown("### No-Show Predictor")
    pred_dept  = st.selectbox("Dept", sorted(df_all.department.unique()), key="pd")
    pred_day   = st.selectbox("Day",  ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], key="pday")
    pred_hour  = st.slider("Hour", 8, 19, 10, key="ph")
    pred_new   = st.radio("Patient type", ["New","Returning"], key="pn")
    pred_snr   = st.selectbox("Doctor seniority", ["Junior","Mid","Senior","Consultant"], key="ps")
    pred_city  = st.selectbox("City", sorted(df_all.city.unique()), key="pc")
    predict_btn= st.button("Predict No-Show Risk", use_container_width=True)

# ── Filter data ───────────────────────────────────────────────────────────────
df = df_all[
    df_all.city.isin(cities) &
    df_all.department.isin(depts) &
    (df_all.month >= date_range[0]) &
    (df_all.month <= date_range[1])
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# MediTrack Analytics Dashboard")
st.markdown(f"<span style='color:var(--muted);font-family:DM Sans'>Showing <b>{len(df):,}</b> appointments across <b>{df.city.nunique()}</b> cities · <b>{df.clinic_name.nunique()}</b> clinics · <b>{df.doctor_name.nunique()}</b> doctors</span>", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
total_rev   = df[df.status=="completed"].fee_charged.sum()
completed_r = (df.status=="completed").mean()*100
noshows_r   = (df.status=="no_show").mean()*100
cancelled_r = (df.status=="cancelled").mean()*100
avg_fee     = df[df.status=="completed"].fee_charged.mean()
total_appts = len(df)

k1,k2,k3,k4,k5 = st.columns(5)
def kpi(col, label, val, delta=None, fmt=None):
    if fmt=="money": display = f"₨{val:,.0f}"
    elif fmt=="pct": display = f"{val:.1f}%"
    else:            display = f"{val:,}"
    dhtml = f"<div class='metric-delta' style='color:{'#ef4444' if delta and delta<0 else '#0d9488'}'>{delta:+.1f}% vs avg</div>" if delta is not None else ""
    col.markdown(f"<div class='metric-card'><div class='metric-lbl'>{label}</div><div class='metric-val'>{display}</div>{dhtml}</div>", unsafe_allow_html=True)

kpi(k1,"Total Appointments", total_appts)
kpi(k2,"Total Revenue",      total_rev,   fmt="money")
kpi(k3,"Completion Rate",    completed_r, fmt="pct")
kpi(k4,"No-Show Rate",       noshows_r,   fmt="pct")
kpi(k5,"Avg Fee (Completed)",avg_fee,     fmt="money")

st.markdown("")

# ── Row 1: Revenue by city + Appointment volume trend ─────────────────────────
st.markdown("<div class='section-head'>Revenue & Volume</div>", unsafe_allow_html=True)
c1, c2 = st.columns([1,2])

with c1:
    rev_city = df[df.status=="completed"].groupby("city")["fee_charged"].sum().sort_values(ascending=True).reset_index()
    fig = px.bar(rev_city, x="fee_charged", y="city", orientation="h",
                 color="fee_charged", color_continuous_scale=["#ccfbf1","#0d9488","#134e4a"],
                 labels={"fee_charged":"Revenue (₨)","city":"City"}, title="Revenue by City")
    fig.update_layout(coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
                      font_family="DM Sans", title_font_family="DM Serif Display",
                      margin=dict(t=40,b=20,l=0,r=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    vol = df.groupby("month").agg(total=("appt_id","count"), completed=("status", lambda x:(x=="completed").sum())).reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=vol.month, y=vol.total, name="All Appts",
                              line=dict(color="#0ea5e9",width=2), fill="tozeroy", fillcolor="rgba(14,165,233,.1)"))
    fig2.add_trace(go.Scatter(x=vol.month, y=vol.completed, name="Completed",
                              line=dict(color="#0d9488",width=2.5)))
    fig2.update_layout(title="Monthly Appointment Volume", plot_bgcolor="white", paper_bgcolor="white",
                       font_family="DM Sans", title_font_family="DM Serif Display",
                       legend=dict(orientation="h",y=1.1), margin=dict(t=40,b=20))
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Department performance ─────────────────────────────────────────────
st.markdown("<div class='section-head'>Department Performance</div>", unsafe_allow_html=True)
dept_stats = df.groupby("department").agg(
    total       =("appt_id","count"),
    completed   =("status", lambda x:(x=="completed").sum()),
    no_shows    =("status", lambda x:(x=="no_show").sum()),
    revenue     =("fee_charged","sum")
).reset_index()
dept_stats["no_show_rate"]    = dept_stats["no_shows"]/dept_stats["total"]*100
dept_stats["completion_rate"] = dept_stats["completed"]/dept_stats["total"]*100

d1,d2 = st.columns(2)
with d1:
    fig3 = px.bar(dept_stats.sort_values("no_show_rate",ascending=False),
                  x="department", y="no_show_rate",
                  color="no_show_rate", color_continuous_scale=["#ccfbf1","#f59e0b","#ef4444"],
                  title="No-Show Rate by Department (%)",
                  labels={"no_show_rate":"No-Show %","department":"Department"})
    fig3.update_layout(coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
                       font_family="DM Sans", title_font_family="DM Serif Display", margin=dict(t=40,b=20))
    st.plotly_chart(fig3, use_container_width=True)

with d2:
    fig4 = px.bar(dept_stats.sort_values("revenue",ascending=False),
                  x="department", y="revenue",
                  color="department", color_discrete_sequence=["#0d9488","#14b8a6","#2dd4bf","#5eead4","#99f6e4","#ccfbf1","#134e4a","#115e59"],
                  title="Total Revenue by Department",
                  labels={"revenue":"Revenue (₨)","department":""})
    fig4.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                       font_family="DM Sans", title_font_family="DM Serif Display", margin=dict(t=40,b=20))
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Doctor no-show league table ───────────────────────────────────────
st.markdown("<div class='section-head'>Doctor No-Show Rates (Top 15 Worst)</div>", unsafe_allow_html=True)
doc_ns = df.groupby(["doctor_name","department","city"]).agg(
    total   =("appt_id","count"),
    no_shows=("status", lambda x:(x=="no_show").sum())
).reset_index()
doc_ns["no_show_rate"] = doc_ns["no_shows"]/doc_ns["total"]*100
doc_ns = doc_ns[doc_ns.total >= 30].sort_values("no_show_rate",ascending=False).head(15)

fig5 = px.bar(doc_ns, x="no_show_rate", y="doctor_name", orientation="h",
              color="department", title="Doctors with Highest No-Show Rates",
              hover_data=["city","total"],
              labels={"no_show_rate":"No-Show %","doctor_name":"Doctor"})
fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                   font_family="DM Sans", title_font_family="DM Serif Display",
                   yaxis=dict(autorange="reversed"), height=420, margin=dict(t=40,b=20,l=0))
st.plotly_chart(fig5, use_container_width=True)

# ── Row 4: Day-of-week + Hour heatmap ─────────────────────────────────────────
st.markdown("<div class='section-head'>Temporal Patterns</div>", unsafe_allow_html=True)
t1,t2 = st.columns(2)

with t1:
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    dow_stats = df.groupby("day_of_week").agg(
        total   =("appt_id","count"),
        no_shows=("status", lambda x:(x=="no_show").sum())
    ).reset_index()
    dow_stats["no_show_rate"] = dow_stats["no_shows"]/dow_stats["total"]*100
    dow_stats = dow_stats.set_index("day_of_week").reindex(dow_order).reset_index()
    fig6 = px.bar(dow_stats, x="day_of_week", y=["total","no_shows"],
                  barmode="group", title="Appointments & No-Shows by Day",
                  labels={"value":"Count","day_of_week":"Day","variable":""},
                  color_discrete_map={"total":"#0d9488","no_shows":"#ef4444"})
    fig6.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       font_family="DM Sans", title_font_family="DM Serif Display", margin=dict(t=40,b=20))
    st.plotly_chart(fig6, use_container_width=True)

with t2:
    heat = df.groupby(["day_of_week","appt_hour"]).agg(
        no_show_rate=("status", lambda x:(x=="no_show").mean()*100)
    ).reset_index()
    heat_pivot = heat.pivot(index="day_of_week", columns="appt_hour", values="no_show_rate")
    heat_pivot = heat_pivot.reindex(dow_order)
    fig7 = px.imshow(heat_pivot, color_continuous_scale=["#f0fdf9","#0d9488","#7f1d1d"],
                     title="No-Show Rate Heatmap (Day × Hour)",
                     labels=dict(x="Hour of Day", y="Day", color="No-Show %"))
    fig7.update_layout(font_family="DM Sans", title_font_family="DM Serif Display",
                       margin=dict(t=40,b=20), height=320)
    st.plotly_chart(fig7, use_container_width=True)

# ── Row 5: New vs Returning patients ──────────────────────────────────────────
st.markdown("<div class='section-head'>Patient Segments</div>", unsafe_allow_html=True)
p1,p2 = st.columns(2)

with p1:
    seg = df.groupby("is_new_patient").agg(
        total   =("appt_id","count"),
        no_shows=("status", lambda x:(x=="no_show").sum()),
        revenue =("fee_charged","sum")
    ).reset_index()
    seg["label"] = seg.is_new_patient.map({0:"Returning",1:"New"})
    seg["no_show_rate"] = seg["no_shows"]/seg["total"]*100
    fig8 = px.bar(seg, x="label", y="no_show_rate",
                  color="label", color_discrete_map={"New":"#f59e0b","Returning":"#0d9488"},
                  title="No-Show Rate: New vs Returning Patients",
                  labels={"no_show_rate":"No-Show %","label":"Patient Type"})
    fig8.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                       font_family="DM Sans", title_font_family="DM Serif Display", margin=dict(t=40,b=20))
    st.plotly_chart(fig8, use_container_width=True)

with p2:
    city_dept = df[df.status=="completed"].groupby(["city","department"])["fee_charged"].sum().reset_index()
    fig9 = px.sunburst(city_dept, path=["city","department"], values="fee_charged",
                       color="fee_charged", color_continuous_scale=["#ccfbf1","#0d9488","#134e4a"],
                       title="Revenue Breakdown: City → Department")
    fig9.update_layout(font_family="DM Sans", title_font_family="DM Serif Display",
                       coloraxis_showscale=False, margin=dict(t=40,b=20))
    st.plotly_chart(fig9, use_container_width=True)

# ── No-Show Predictor ──────────────────────────────────────────────────────────
if predict_btn:
    st.markdown("<div class='section-head'>🔮 No-Show Risk Prediction</div>", unsafe_allow_html=True)
    try:
        bundle   = pickle.load(open("noshowmodel.pkl","rb"))
        model    = bundle["model"]
        encoders = bundle["encoders"]

        inp = pd.DataFrame([{
            "appt_hour":     pred_hour,
            "is_new_patient":1 if pred_new=="New" else 0,
            "day_of_week_enc":   encoders["day_of_week"].transform([pred_day])[0],
            "department_enc":    encoders["department"].transform([pred_dept])[0],
            "seniority_enc":     encoders["seniority"].transform([pred_snr])[0],
            "city_enc":          encoders["city"].transform([pred_city])[0],
        }])
        proba = model.predict_proba(inp)[0][1] * 100

        color = "#ef4444" if proba>30 else "#f59e0b" if proba>15 else "#0d9488"
        level = "HIGH RISK 🔴" if proba>30 else "MODERATE ⚠️" if proba>15 else "LOW RISK ✅"
        st.markdown(f"""
        <div style='background:white;border:1px solid {color};border-radius:16px;padding:24px;max-width:480px;'>
          <div style='font-family:DM Serif Display;font-size:1.2rem;color:#0f3832;margin-bottom:8px;'>
            Predicted No-Show Probability
          </div>
          <div style='font-size:3rem;font-weight:700;color:{color};'>{proba:.1f}%</div>
          <div style='font-size:1rem;color:{color};font-family:DM Sans;margin-top:4px;'>{level}</div>
          <hr style='border-color:#d1fae5;margin:12px 0;'>
          <div style='font-size:.85rem;color:#6b7280;font-family:DM Sans;'>
            {pred_dept} · {pred_day} {pred_hour:02d}:00 · {pred_snr} doctor · {pred_new} patient · {pred_city}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if proba > 25:
            st.info("💡 **Reminder recommended** — Send an SMS/WhatsApp reminder 24h and 2h before this appointment.")
    except FileNotFoundError:
        st.error("Model not found. Run `python train_model.py` first.")