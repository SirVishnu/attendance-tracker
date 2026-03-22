import datetime
from flask import Flask, render_template, request, session, redirect, g, url_for
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
   # initialize db
   db = get_db()
   group = db.execute("SELECT * FROM groups WHERE user_id = ?", [session['user_id']])
   return render_template("index.html",groups=group)

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



# group route
@app.route("/group/<int:id>", methods=['GET', 'POST'])
@login_required
def group(id):
   
    # initialize db
    db = get_db()
    group = db.execute("SELECT * FROM groups WHERE user_id = ? AND id = ?", [session['user_id'], id]).fetchone()


    # if user submits form for lecture
    if request.method == 'POST':
        attend = request.form.get("lec_attend")
        conduct = request.form.get("lec_conduct")
        date = request.form.get("date")

        # check if all inputs are present
        if not attend or not conduct or not date:
            return render_template("group.html", error="please enter all the input", id=id, group=group)
        
        # lec attend should not be more than conduct
        if int(attend) > int(conduct):
            return render_template("group.html", error="lecture attend should not be greater than lecture conducted", id=id, group=group)

        # save in db
        db.execute("INSERT INTO sessions (group_id, date, lecture_conducted, lecture_attended) VALUES (?, ?, ?, ?)", [id, date, conduct, attend])
        db.commit()

        return redirect(url_for('group', id=id))

    # get total attendance %
    attendance = db.execute("SELECT SUM(lecture_attended) as attend, SUM(lecture_conducted) as conduct FROM sessions WHERE group_id = ? GROUP BY group_id",[id]).fetchone()

    if attendance is None:
        percent = 0
        attendance = {'attend': 0, 'conduct': 0}
    else:
        percent = int(attendance['attend']) / int(attendance['conduct']) * 100
        percent = round(percent, 2)

    # check if use subgroup
    if group['use_subgroups'] == 1:
        sub_group = db.execute("SELECT * FROM subjects WHERE group_id = ?", [id]).fetchall()
        return render_template("group.html",attendance=attendance,percent=percent, group=group, subject=sub_group, id=id)

    return render_template("group.html",attendance=attendance, group=group, id=id,percent=percent, today=datetime.date.today())

# create new subject
@app.route("/group/<int:id>/create", methods=['GET', 'POST'])
@login_required
def create_subject(id):
    if request.method == 'POST':
        name = request.form.get("name")

        if not name:
            return render_template("create_sub.html", error="please enter subject name", id=id)
        
        # initialize db
        db = get_db()

        # insert in db
        db.execute("INSERT INTO subjects (group_id, name) VALUES (?, ?)", [id, name])
        db.commit()

        return redirect(url_for('group', id=id))

    return render_template("create_sub.html", id=id)

# subject route
@app.route("/group/<int:group_id>/subject/<int:sub_id>", methods=['GET', 'POST'])   
@login_required
def subject(group_id, sub_id):
    # initialize db
    db = get_db()
    sub = db.execute("SELECT * FROM subjects WHERE id = ? AND group_id = ?", [sub_id, group_id]).fetchone()

    if request.method == 'POST':
        attend = request.form.get("lec_attend")
        conduct = request.form.get("lec_conduct")
        date = request.form.get("date")
        if not attend or not conduct or not date:
            return render_template("subject.html", error="pls enter valid input", group_id=group_id, sub_id=sub_id)
        
        # lec attend should not be more than conduct
        if int(attend) > int(conduct):
            return render_template("subject.html", error="lecture attend should not be greater than lecture conducted", group_id=group_id, sub_id=sub_id)

        # save in db
        db.execute("INSERT INTO sessions (group_id, subject_id, date, lecture_conducted, lecture_attended) VALUES (?, ?,?, ?, ?)", [group_id,sub_id, date, conduct, attend])
        db.commit()
        return redirect(url_for('subject', group_id = group_id, sub_id=sub_id))

    # get total attendance %
    attendance = db.execute("SELECT SUM(lecture_attended) as attend, SUM(lecture_conducted) as conduct FROM sessions WHERE group_id = ? AND subject_id = ? GROUP BY subject_id",[group_id, sub_id]).fetchone()

    if attendance is None:
        percent = 0
        attendance = {'attend': 0, 'conduct': 0}
    else:
        percent = int(attendance['attend']) / int(attendance['conduct']) * 100
        percent = round(percent, 2)

    return render_template("subject.html",attendance=attendance, percent=percent, group_id=group_id, sub_id=sub_id, sub=sub, today=datetime.date.today())

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