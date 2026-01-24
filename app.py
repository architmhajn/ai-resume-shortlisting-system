from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Archit@dbms",
        database="resume_ai"
    )

@app.route('/')
def upload():
    return render_template('upload.html')
@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(tables)

if __name__ == "__main__":
    app.run(debug=True)
