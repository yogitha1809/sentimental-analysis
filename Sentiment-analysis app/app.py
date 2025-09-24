from flask import Flask, request, render_template, redirect, url_for, session, flash, get_flashed_messages
import pickle
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "replace_this_with_a_secure_random_key"  # Change in production

# ---------------- Load ML model and vectorizer ----------------
with open(r"C:\internship -1\august-_internship-_2025\Sentiment-analysis app\model.pkl", "rb") as f:
    model = pickle.load(f)

with open(r"C:\internship -1\august-_internship-_2025\Sentiment-analysis app\vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# ---------------- Database connection ----------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Your MySQL password
            database="sentiment_analysis"
        )
        return conn
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        return None

# ---------------- Routes ----------------

# Home page (public, always visible)
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- Prediction page (login required) ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "username" not in session:
        _ = get_flashed_messages()  # clear old messages
        flash("⚠ Please login to access prediction page!", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        input_text = request.form.get("text", "").strip()
        if not input_text:
            flash("⚠ Please enter some text!", "error")
            return render_template("index.html")

        input_vec = vectorizer.transform([input_text])
        prediction = model.predict(input_vec)[0]
        proba = float(model.predict_proba(input_vec).max()) if hasattr(model, "predict_proba") else None

        # Save to DB
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
            except Exception as e:
                print("Database insert error:", e)
            finally:
                conn.close()

        return render_template("index.html", input_text=input_text, prediction=prediction, proba=proba)

    return render_template("index.html")

# ---------------- History page (login required) ----------------
@app.route("/history")
def history():
    if "username" not in session:
        _ = get_flashed_messages()
        flash("⚠ Please login to access history page!", "error")
        return redirect(url_for("login"))

    predictions = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, input_text, predicted_label, created_at FROM predictions ORDER BY created_at DESC"
            )
            predictions = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print("Database error:", e)
        finally:
            conn.close()

    return render_template("history.html", predictions=predictions)

# ---------------- Login ----------------
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
                print("Database error:", e)
            finally:
                conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            flash("✅ Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("❌ Invalid username or password!", "error")

    return render_template("login.html")

# ---------------- Register ----------------
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
            except mysql.connector.IntegrityError:
                flash("⚠ Username or email already exists!", "error")
                return render_template("register.html")
            finally:
                conn.close()

        flash("✅ Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.pop("username", None)
    _ = get_flashed_messages()
    flash("⚠ Please login to access prediction page!", "error")
    return redirect(url_for("login"))

# ---------------- Run the app ----------------
if __name__ == "__main__":
    app.run(debug=True)
