import sqlite3, random, numpy as np
from datetime import datetime, timedelta

random.seed(42); np.random.seed(42)

CITIES = {
    "Karachi":   ["KHI-Central","KHI-North","KHI-South","KHI-East"],
    "Lahore":    ["LHR-Garden","LHR-Gulberg","LHR-Model Town","LHR-DHA"],
    "Islamabad": ["ISB-F8","ISB-G9","ISB-Blue Area"],
    "Peshawar":  ["PSH-Saddar","PSH-Hayatabad","PSH-University Road"],
    "Multan":    ["MUL-Cantt","MUL-Gulgasht","MUL-Shah Rukn-e-Alam"],
}
DEPTS   = ["General","Cardiology","Ortho","Dermatology","Pediatrics"]
SENIORS = ["Junior","Mid","Senior","Consultant"]
BASE_FEE = {"General":800,"Cardiology":3000,"Ortho":2500,"Dermatology":1800,"Pediatrics":1200}
SR_MULT  = {"Junior":1.0,"Mid":1.3,"Senior":1.6,"Consultant":2.2}
STATUSES = ["completed","cancelled","no_show"]
STATUS_W = [0.70, 0.18, 0.12]

con = sqlite3.connect("meditrack.db")
cur = con.cursor()

cur.executescript("""
DROP TABLE IF EXISTS clinics;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS appointments;

CREATE TABLE clinics(
  clinic_id   INTEGER PRIMARY KEY,
  clinic_name TEXT, city TEXT, address TEXT
);
CREATE TABLE doctors(
  doctor_id   INTEGER PRIMARY KEY,
  name        TEXT, department TEXT, seniority TEXT,
  clinic_id   INTEGER, consultation_fee REAL
);
CREATE TABLE patients(
  patient_id  INTEGER PRIMARY KEY,
  name        TEXT, age INTEGER, gender TEXT,
  city        TEXT, is_new INTEGER
);
CREATE TABLE appointments(
  appt_id       INTEGER PRIMARY KEY,
  patient_id    INTEGER, doctor_id INTEGER,
  clinic_id     INTEGER, appt_date TEXT,
  appt_time     TEXT, status TEXT,
  fee_charged   REAL, day_of_week TEXT,
  is_new_patient INTEGER
);
""")

# --- Clinics ---
clinic_rows = []
cid = 1
for city, names in CITIES.items():
    for n in names:
        clinic_rows.append((cid, n, city, f"{n} Street, {city}"))
        cid += 1
cur.executemany("INSERT INTO clinics VALUES(?,?,?,?)", clinic_rows)

# --- Doctors (4-6 per clinic) ---
first = ["Ayesha","Bilal","Fatima","Hassan","Imran","Sana","Tariq","Zara","Kamran","Nadia","Usman","Rida"]
last  = ["Khan","Ahmed","Ali","Malik","Sheikh","Qureshi","Siddiqui","Rao","Chaudhry","Mirza"]
doctor_rows = []; did = 1
for c in clinic_rows:
    for _ in range(random.randint(4,6)):
        dept  = random.choice(DEPTS)
        snr   = random.choice(SENIORS)
        fee   = round(BASE_FEE[dept] * SR_MULT[snr] * random.uniform(0.9,1.1))
        dname = f"Dr. {random.choice(first)} {random.choice(last)}"
        doctor_rows.append((did, dname, dept, snr, c[0], fee))
        did += 1
cur.executemany("INSERT INTO doctors VALUES(?,?,?,?,?,?)", doctor_rows)

# --- Patients ---
pfirst = ["Ali","Sara","Omar","Hina","Zain","Layla","Asad","Maryam","Faisal","Noor"]
plast  = ["Khan","Butt","Raza","Javed","Hussain","Ansari","Syed","Baig","Lone","Gill"]
patient_rows = []
for pid in range(1, 3001):
    city = random.choice(list(CITIES.keys()))
    age  = int(np.random.normal(38, 15))
    age  = max(1, min(90, age))
    gndr = random.choice(["Male","Female"])
    is_new = 1 if pid > 2400 else 0
    patient_rows.append((pid, f"{random.choice(pfirst)} {random.choice(plast)}", age, gndr, city, is_new))
cur.executemany("INSERT INTO patients VALUES(?,?,?,?,?,?)", patient_rows)

# --- Appointments (18 months of data) ---
start = datetime(2024, 1, 1)
appt_rows = []; aid = 1
hours = list(range(8,20))
for _ in range(22000):
    pat   = random.randint(1, 3000)
    doc   = random.choice(doctor_rows)
    clin  = doc[4]
    delta = random.randint(0, 545)
    d     = start + timedelta(days=delta)
    if d.weekday() == 6: d += timedelta(days=1)   # skip Sundays
    h     = random.choice(hours)
    t     = f"{h:02d}:{random.choice(['00','15','30','45'])}"
    # no-show more likely early morning & new patients
    w = STATUS_W.copy()
    if h < 10:        w[2] += 0.07; w[0] -= 0.07
    if h > 17:        w[2] += 0.04; w[0] -= 0.04
    if patient_rows[pat-1][5] == 1:  w[2] += 0.05; w[0] -= 0.05
    w = [max(0,x) for x in w]; s = sum(w); w = [x/s for x in w]
    status = np.random.choice(STATUSES, p=w)
    fee    = doc[5] if status == "completed" else 0
    dow    = d.strftime("%A")
    is_new = patient_rows[pat-1][5]
    appt_rows.append((aid, pat, doc[0], clin, d.strftime("%Y-%m-%d"), t, status, fee, dow, is_new))
    aid += 1
cur.executemany("INSERT INTO appointments VALUES(?,?,?,?,?,?,?,?,?,?)", appt_rows)

con.commit(); con.close()
print(f"✅ Database seeded — {len(appt_rows):,} appointments, {len(doctor_rows)} doctors, {len(clinic_rows)} clinics.")