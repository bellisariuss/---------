import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# ✅ Зарежда правилния файл
df = pd.read_excel("ski_dataset.xlsx")

# Енкодиране на категориите
label_encoders = {}
for column in ["ниво", "стил", "тип ски", "писта", "име"]:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
    label_encoders[column] = le

# Подготовка на входове и изходи
X = df[["ниво", "ръст", "стил", "писта"]]
y_length = df["препоръчителна дължина"]
y_type = df["тип ски"]

# Обучение на два модела
model_length = RandomForestClassifier(n_estimators=100, random_state=42)
model_length.fit(X, y_length)

model_type = RandomForestClassifier(n_estimators=100, random_state=42)
model_type.fit(X, y_type)

# Записване
joblib.dump(model_length, "rf_modpython .\train_model.py)
el_length.pkl")
joblib.dump(model_type, "rf_model_type.pkl")
joblib.dump(label_encoders, "rf_label_encoders.pkl")

print("✅ Моделите са успешно обучени и записани!")
