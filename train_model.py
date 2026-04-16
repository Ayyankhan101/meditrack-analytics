import sqlite3, pickle
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

con = sqlite3.connect("meditrack.db")
df = pd.read_sql("""
    SELECT a.status, a.appt_time, a.day_of_week, a.is_new_patient,
           d.department, d.seniority, c.city
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.doctor_id
    JOIN clinics c ON a.clinic_id = c.clinic_id
""", con)
con.close()

df["target"]    = (df["status"] == "no_show").astype(int)
df["appt_hour"] = df["appt_time"].str[:2].astype(int)

encoders = {}
cat_cols = ["day_of_week","department","seniority","city"]
for col in cat_cols:
    le = LabelEncoder()
    df[col+"_enc"] = le.fit_transform(df[col])
    encoders[col] = le

features = ["appt_hour","is_new_patient"] + [c+"_enc" for c in cat_cols]
X, y = df[features], df["target"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

model = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.08, random_state=42)
model.fit(X_tr, y_tr)
print(classification_report(y_te, model.predict(X_te)))

pickle.dump({"model": model, "encoders": encoders, "features": features}, open("noshowmodel.pkl","wb"))
print("✅ Model saved to noshowmodel.pkl")