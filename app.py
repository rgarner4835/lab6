from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
import os
import folium
from folium import plugins

currentlocation = os.path.dirname(os.path.abspath(__file__))

#Create a map centered on a specific location
latitude = 37.0902
longitude = 95.7129
mymap = folium.Map(location=[latitude, longitude], zoom_start=10)

# Enable the draw plugin
draw = plugins.Draw(export=True)
draw.add_to(mymap)

# Display the map
mymap.save('map.html')

app = Flask(__name__)
UN = ""
PW = ""

def initialize_database():
    conn = sqlite3.connect(os.path.join(currentlocation, 'users.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, Username TEXT NOT NULL, Password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

initialize_database()

@app.route("/")
def loginpage():
    
    return render_template("myform.html")

@app.route("/login", methods=["POST"])
def checklogin():
    UN = request.form['Username']
    PW = request.form['Password']

    print("Received Username:", UN)
    print("Received Password:", PW)

    sqlconnection = sqlite3.connect(os.path.join(currentlocation, "users.db"))
    cursor = sqlconnection.cursor()
    query1 = "SELECT Password From users WHERE Username = ?"
    cursor.execute(query1, (UN,))
    row = cursor.fetchone()

    
    if row and row[0] == hashlib.sha256(PW.encode()).hexdigest():
        return redirect(url_for('file_upload', username=UN))  # Redirect to file_upload route
    else:
        return render_template("myform.html")

@app.route("/register", methods=["POST"])
def register():
    UN = request.form['Username']
    PW = request.form['Password']

    sqlconnection = sqlite3.connect(os.path.join(currentlocation, "users.db"))
    cursor = sqlconnection.cursor()
    query1 = "SELECT Username From users WHERE Username = ?"
    cursor.execute(query1, (UN,))
    row = cursor.fetchone()

    if row:
        return render_template("myform.html")  # Username already exists
    else:
        hashed_pw = hashlib.sha256(PW.encode()).hexdigest()
        query2 = "INSERT INTO users (Username, Password) VALUES (?, ?)"
        cursor.execute(query2, (UN, hashed_pw))
        sqlconnection.commit()
        return redirect(url_for('file_upload'))  # Redirect to file_upload route


@app.route("/home/<username>")
def file_upload(username):

    sqlconnection = sqlite3.connect(os.path.join(currentlocation, "users.db"))
    cursor = sqlconnection.cursor()
    query1 = "SELECT Password From users WHERE Username = ?"
    cursor.execute(query1, (username, ))
    row = cursor.fetchone()
    return render_template("file_upload.html",current_user_password_hash=row[0])
    
    
if __name__ == '__main__':
    app.run(debug=True)


"""
# Function to create a hash of the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to initialize the SQLite database
def initialize_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password_hash TEXT)''')
    conn.commit()
    conn.close()

# Function to check if a user exists
def user_exists(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Function to insert a new user into the database
def insert_user(username, password_hash):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?)", (username, password_hash))
    conn.commit()
    conn.close()

# Function to handle the registration process
def register_user(username, password):
    password_hash = hash_password(password)
    if not user_exists(username):
        insert_user(username, password_hash)

# Function to authenticate user login
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        stored_password_hash = result[1]
        if stored_password_hash == hash_password(password):
            return True
    return False

# Route for the login and registration page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['var1']
        password = request.form['var2']
        if request.form['login_button'] == 'Login':
            if authenticate_user(username, password):
                return redirect("/file_upload")
        elif request.form['register_button'] == 'Register':
            register_user(username, password)
            return redirect("/file_upload")
    return render_template('myform.html')

# Route for the file upload page
@app.route('/file-upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        # Handle file upload logic here
        uploaded_file = request.files['file']
        # Process the uploaded file as needed
        # Get the API key (hash of the user's password)
        current_user_password_hash = hash_password("user_password")  # Replace "user_password" with the actual password
        return render_template('file_upload.html', current_user_password_hash=current_user_password_hash)
    # If the request method is GET, render the file upload form
    return render_template('file_upload.html', current_user_password_hash="")
    
"""
