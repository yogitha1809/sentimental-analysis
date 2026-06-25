# Sentiment Analysis Web App (Flask + Machine Learning)

An AI-powered Sentiment Analysis Web Application built using Flask, Machine Learning, and MySQL.  
The system classifies input text into sentiment categories and stores predictions with user authentication.

---

## Features

- User registration and login system with secure password hashing  
- Machine learning-based sentiment prediction  
- Pre-trained model using pickle (model and vectorizer)  
- MySQL database integration  
- Prediction history tracking  
- Clear history option  
- Session timeout (30 minutes auto logout)  
- Protected routes using login required decorator  
- Recent predictions displayed on homepage  

---

## Tech Stack

- Frontend: HTML, CSS, Jinja2 Templates  
- Backend: Flask (Python)  
- Machine Learning: Scikit-learn (model.pkl, vectorizer.pkl)  
- Database: MySQL  
- Security: Werkzeug password hashing  
- Libraries: pickle, regex, datetime  

---

## Project Structure

project/

├── app.py  
├── config.py  
├── model.pkl  
├── vectorizer.pkl  

├── ml/  
│   ├── train_model.py  
│   └── product_reviews.csv  

├── templates/  
│   ├── home.html  
│   ├── login.html  
│   ├── register.html  
│   ├── predict.html  
│   ├── history.html  
│   └── sidebar.html  

├── static/  
│   ├── css/  
│   │   ├── home.css  
│   │   ├── login.css  
│   │   ├── register.css  
│   │   ├── predict.css  
│   │   ├── history.css  
│   │   └── sidebar.css  
│   └── bg.jpg  

└── README.md  

---

## Installation & Setup

### 1. Clone the Repository

git clone https://github.com/yogitha1809/sentiment-analysis.git  
cd sentiment-analysis  

---

### 2. Create Virtual Environment

python -m venv venv  
venv\Scripts\activate   (Windows)

---

### 3. Install Dependencies

pip install flask mysql-connector-python scikit-learn werkzeug  

---

### 4. Database Setup (MySQL)

CREATE DATABASE sentiment_analysis;

---

Users Table

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(100),
    password VARCHAR(255)
);

---

Predictions Table

CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_text TEXT,
    predicted_label VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---

### 5. Run the Application

python app.py  

Open in browser:  
http://127.0.0.1:5000/

---

## How It Works

- User registers or logs in  
- User enters text input  
- Text is cleaned using preprocessing  
- Vectorizer converts text into numerical format  
- Machine learning model predicts sentiment  
- Prediction is stored in MySQL database  
- History is displayed in UI  

---

## Model Details

- Model: Scikit-learn classifier (Logistic Regression / SVM / etc.)  
- Vectorizer: TF-IDF or CountVectorizer  
- Output: Positive / Negative / Neutral  

---

## Security Features

- Password hashing using Werkzeug  
- Login required decorator for protected pages  
- Session-based authentication  
- Auto logout after 30 minutes  

---

## Future Improvements

- Add sentiment confidence score visualization  
- Deploy on cloud (AWS / Render / Heroku)  
- Add REST API support  
- Improve UI with Bootstrap or Tailwind  
- Add real-time sentiment dashboard  

---

## Author

Yogitha Lakshmi S