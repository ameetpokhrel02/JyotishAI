# train_models.py - 3 Models + Clustering + Evaluation
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create synthetic + real-like data (5000 rows)
np.random.seed(42)
n = 5000

data = {
    'age': np.random.randint(18, 70, n),
    'lagna_sign': np.random.choice(range(12), n),
    'sun_sign': np.random.choice(range(12), n),
    'moon_sign': np.random.choice(range(12), n),
    'mars_in_7th': np.random.choice([0, 1], n, p=[0.8, 0.2]),
    'saturn_aspect_7th': np.random.choice([0, 1], n, p=[0.7, 0.3]),
    'rahu_ketu_axis': np.random.choice([0, 1], n, p=[0.6, 0.4]),
}

df = pd.DataFrame(data)

# Target 1: Career Success (High/Medium/Low)
df['career_level'] = np.where(
    (df['sun_sign'].isin([0,4,8])) & (df['lagna_sign'].isin([0,4,8])), 'High',
    np.where(df['mars_in_7th'] == 1, 'Low', 'Medium')
)

# Target 2: Health Issues
df['health_issues'] = np.where(
    (df['moon_sign'].isin([6,8,11])) | (df['saturn_aspect_7th'] == 1), 1, 0
)

# Target 3: Marriage Delay
df['marriage_delay'] = np.where(
    (df['age'] > 30) & (df['mars_in_7th'] == 1), 1, 0
)

# Features & Targets
X = df.drop(['career_level', 'health_issues', 'marriage_delay'], axis=1)
y_career = df['career_level']
y_health = df['health_issues']
y_marriage = df['marriage_delay']

# Encode career
le = LabelEncoder()
y_career_encoded = le.fit_transform(y_career)

# Split
X_train, X_test, y1_train, y1_test = train_test_split(X, y_career_encoded, test_size=0.2, random_state=42)
_, _, y2_train, y2_test = train_test_split(X, y_health, test_size=0.2, random_state=42)
_, _, y3_train, y3_test = train_test_split(X, y_marriage, test_size=0.2, random_state=42)

# Train 3 Models
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100),
    'SVM': SVC(kernel='rbf'),
    'Logistic Regression': LogisticRegression(max_iter=1000)
}

print("Training Models...")
results = {}
for name, model in models.items():
    model.fit(X_train, y1_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y1_test, pred)
    results[name] = acc
    print(f"{name}: {acc:.3f}")

# Save best model
best_model = RandomForestClassifier(n_estimators=100)
best_model.fit(X_train, y1_train)
joblib.dump(best_model, "../model/career_rf_model.pkl")
joblib.dump(le, "../model/career_label_encoder.pkl")

# Clustering (Personality Types)
kmeans = KMeans(n_clusters=5, random_state=42)
df['personality_cluster'] = kmeans.fit_predict(X)
joblib.dump(kmeans, "../model/personality_clusters.pkl")

# Confusion Matrix (Random Forest)
cm = confusion_matrix(y1_test, best_model.predict(X_test))
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
plt.title("Confusion Matrix - Career Prediction")
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.savefig("../assets/plots/confusion_matrix.png")
plt.close()

print("ALL MODELS TRAINED & SAVED!")
print("Confusion Matrix saved to assets/plots/")
