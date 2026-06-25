from flask import Flask, request, render_template, redirect, url_for, session, flash
from functools import wraps
import pickle
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "replace_this_with_a_secure_random_key"
app.permanent_session_lifetime = timedelta(minutes=30)

# ---------------- Load ML model and vectorizer ----------------
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# ---------------- Database connection ----------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sentiment_analysis"
        )
        return conn
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        return None

# ---------------- Login required decorator ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("⚠ Please login to access this page!", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- Utility functions ----------------
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def analyze_sentiment(text):
    vect_text = vectorizer.transform([text])
    if hasattr(model, "predict_proba"):
        proba_all = model.predict_proba(vect_text)[0]
        predicted_index = int(proba_all.argmax())
        raw_label = model.classes_[predicted_index]
        proba = round(float(proba_all[predicted_index]), 4)
        prediction = str(raw_label).lower()
    else:
        prediction = str(model.predict(vect_text)[0]).lower()
        proba = None
    return prediction, proba

# ---------------- Routes ----------------

# Home page
@app.route("/")
def home():
    recent_predictions = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT input_text, predicted_label, created_at "
                "FROM predictions ORDER BY created_at DESC LIMIT 12"
            )
            recent_predictions = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print("DB error:", e)
        finally:
            conn.close()

    # Check if user is logged in
    logged_in = 'username' in session

    return render_template(
        "home.html",
        recent_predictions=recent_predictions,
        logged_in=logged_in
    )



# Predict page
@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    input_text = ""
    prediction = None
    proba = None

    if request.method == "POST":
        input_text = request.form.get("text", "").strip()
        if not input_text:
            flash("⚠ Please enter some text!", "error")
            return render_template("predict.html", input_text=input_text)

        cleaned_text = clean_text(input_text)
        prediction, proba = analyze_sentiment(cleaned_text)

        # Save prediction to DB
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO predictions (input_text, predicted_label) VALUES (%s, %s)",
                    (input_text, prediction)
                )
                conn.commit()
                cursor.close()
                flash("✅ Prediction saved successfully!", "success")
            except Exception as e:
                flash(f"❌ Error saving prediction: {e}", "error")
            finally:
                conn.close()

    return render_template("predict.html", input_text=input_text, prediction=prediction, proba=proba)

# History page
@app.route("/history")
@login_required
def history():
    predictions = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, input_text, predicted_label, created_at FROM predictions ORDER BY created_at DESC"
            )
            predictions = cursor.fetchall()
            cursor.close()
        except Exception as e:
            flash(f"❌ Error fetching history: {e}", "error")
        finally:
            conn.close()
    return render_template("history.html", predictions=predictions)

# Clear history
@app.route("/clear_history", methods=["POST"])
@login_required
def clear_history():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM predictions")
            conn.commit()
            cursor.close()
            flash("✅ Your history has been cleared.", "success")
        except Exception as e:
            flash(f"❌ Error clearing history: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for("history"))

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection()
        user = None
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                user = cursor.fetchone()
                cursor.close()
            except Exception as e:
                flash(f"❌ Database error: {e}", "error")
            finally:
                conn.close()

        if user and check_password_hash(user["password"], password):
            session.permanent = True
            session["username"] = user["username"]
            flash("✅ Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("❌ Invalid username or password!", "error")

    return render_template("login.html")

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if not username or not email or not password:
            flash("⚠ Please fill all fields!", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, hashed_password)
                )
                conn.commit()
                cursor.close()
                flash("✅ Registration successful! Please login.", "success")
                return redirect(url_for("login"))
            except mysql.connector.IntegrityError:
                flash("❌ Username already exists!", "error")
            except Exception as e:
                flash(f"❌ Error during registration: {e}", "error")
            finally:
                conn.close()

    return render_template("register.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    flash("✅ You have been logged out.", "success")
    return redirect(url_for("login"))

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
