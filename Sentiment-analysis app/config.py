import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",           # or 'flaskuser'
        password="",           # replace with your MySQL password
        database="sentiment_analysis"
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO predictions (input_text, predicted_label) VALUES (%s, %s)",
        ("Test text", "positive")
    )
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Insert successful")
except Exception as e:
    print("❌ Database error:", e)
    import traceback
    traceback.print_exc()
