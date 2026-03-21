import datetime
from flask import Flask, render_template, request, session, redirect, g
from database import get_db, close_db
from help import login_required
from sqlite3 import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = '_5#y2L"F4Q8zdwurneufb]/'

# close db connection after every request automatically
app.teardown_appcontext(close_db)

app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=30)

# homepage route
@app.route("/")
@login_required
def index():
   return render_template("index.html")

# create new group
@app.route("/create", methods=['GET', 'POST'])  
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')

        # check if name entered
        if not name:
            return render_template("create.html", error="enter a valid group name")

        # initialize db
        db = get_db()

        # insert in db
        if subject:
            db.execute("INSERT INTO groups (user_id, name, use_subgroups) VALUES (?, ?, ?)", [session['user_id'], name, subject])
        else:
            db.execute("INSERT INTO groups (user_id, name) VALUES (?, ?)", [session['user_id'], name])
        db.commit()

        return redirect("/")

    else:
        return render_template("create.html")
    

# login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  
        username = request.form.get('username')
        password = request.form.get('password')
           
        # check if user entered username and password
        if not username or not password:
            return render_template("login.html", error="Please enter both username and password.")
        
        # hash password
        
        # check if username and password are correct
        db = get_db()
        # store user info
        info = db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchone()
        
        if info is None or not check_password_hash(info['password'], password):
            return render_template("login.html", error="Invalid username or password")
        else:
            # log in the user
            session['user_id'] = info['id']
            return redirect("/") 
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()

    return redirect("/")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method =='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        c_password = request.form.get('c_password')
        
        # check if user entered username and password
        if not username or not password or not c_password:
            return render_template("register.html", error="Please fill out all fields.")
        
        # check if passwords match
        if password != c_password:
            return render_template("register.html", error="Passwords do not match.")
        
        # hash the password before storing it in the database
        hashed = generate_password_hash(password)
        
        # initialize db
        db = get_db()
        
        try:
            # insert user in db
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashed])
            db.commit()
        except IntegrityError:  
            # if username exists
            return render_template("register.html", error="username already exists") 
        
        return redirect("/login")
    else:
        return render_template("register.html")

if __name__=='__main__': 
    app.run(debug=True) 