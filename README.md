# MediTrack Analytics 🏥

A healthcare analytics dashboard for Pakistan clinic networks with intelligence features, voice commands, and an interactive OpenStreetMap.

![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 Features

### 🎨 Visual Uniqueness
- **Dark Command Center** - Hospital operations room aesthetic with neon teal accents
- **Interactive Pakistan Map** - OpenStreetMap with clinic markers, color-coded by revenue
- **Doctor Radar Charts** - 5-dimension performance visualization
- **Clinic Floor View** - Real-time appointment queue grid
- **Executive One-Pager** - Printable CEO summary

### 🎯 Intelligence Hub
- **Reminder ROI Calculator** - Estimate recovered no-shows and revenue saved
- **Churn Detection** - Flag patients 90+ days no return
- **Doctor Burnout Signal** - Track appointment density per doctor
- **Seasonal Patterns** - Flu season overlay on Pediatrics volume
- **Anomaly Detection** - Flag unusual no-show rate days
- **Revenue Alerts** - Monitor MoM drops >20%

### 🔔 Operational Features
- **Voice Navigation** - Push-to-talk commands (Chrome/Edge/Brave)
- **Campaign Builder** - Generate patient outreach CSV
- **Shift Intelligence** - Optimize doctor scheduling
- **City Benchmarking** - Head-to-head comparison

---

## 🗺️ Pakistan Map

Interactive map showing all 17 clinics across 5 cities:
- Karachi (4 clinics)
- Lahore (4 clinics)
- Islamabad (3 clinics)
- Peshawar (3 clinics)
- Multan (3 clinics)

Click markers to see:
- Clinic name
- Revenue
- Appointments
- Completion rate

---

## 🎤 Voice Commands

Use voice to navigate:
- Say "dashboard" → Dashboard
- Say "map" → Pakistan Map
- Say "doctors" → Doctor Scorecards
- Say "intelligence" → Intelligence Hub
- Say "campaign" → Campaign Builder

Works in Chrome, Edge, and Brave browsers.

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/your-account/meditrack-analytics.git
cd meditrack-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app_enhanced.py
```

---

## 📁 Project Structure

```
meditrack-analytics/
├── app_enhanced.py       # Main dashboard
├── meditrack.db           # SQLite database (22K appointments)
├── noshowmodel.pkl       # ML model for no-show prediction
├── requirements.txt     # Python dependencies
├── seed_db.py            # Database seeding script
└── train_model.py       # Model training script
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Maps | Folium + OpenStreetMap |
| Charts | Plotly |
| Database | SQLite |
| ML | scikit-learn |

---

## 📊 Data Summary

- **22,000** appointments
- **3,000** patients
- **82** doctors
- **17** clinics
- **5** cities
- **18 months** of data (Jan 2024 - Jun 2025)

---

## 📄 License

MIT License - See LICENSE file for details.

---

**Created**: 2024  
**Author**: MediTrack Team