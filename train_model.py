import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ---------------- Step 1: Load CSV safely ----------------
df = pd.read_csv("product_reviews.csv", quotechar='"')  # handles commas in reviews
print("✅ CSV loaded successfully")

# ---------------- Step 2: Clean text ----------------
import re

def clean_text(text):
    text = text.lower().strip()                  # lowercase & remove extra spaces
    text = re.sub(r'[^a-z\s]', '', text)        # remove punctuation
    return text

df['cleaned_review'] = df['review'].apply(clean_text)
print("✅ Text cleaned")

# ---------------- Step 3: Features and labels ----------------
X = df['cleaned_review']
y = df['sentiment']

# ---------------- Step 4: Vectorize ----------------
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)
print("✅ Text vectorized")

# ---------------- Step 5: Train/Test split ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

# ---------------- Step 6: Train model ----------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)
print("✅ Model trained")

# ---------------- Step 7: Evaluate ----------------
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy on test set: {acc*100:.2f}%")

# ---------------- Step 8: Save model & vectorizer ----------------
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Model and vectorizer saved successfully!")
