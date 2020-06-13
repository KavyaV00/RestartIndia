from datetime import datetime

from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    docName = db.Column(db.String(50))
    department = db.Column(db.String(50))
    date = db.Column(db.Integer)
    time = db.Column(db.Integer)
    mode = db.Column(db.String(10))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby_name = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Pending')


class Diseases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(50))
    allergy = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Medicines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    dose = db.Column(db.Integer)
    medicine = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    bloodGroup = db.Column(db.String(10))
    heredityIssues = db.Column(db.String(100))
    contactNumber = db.Column(db.Integer)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# *****  DOCTOR SIDE *****
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    department = db.Column(db.String(50))
    password = db.Column(db.String(50))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(50))
    doc_name = db.Column(db.String(50))
    feedback = db.Column(db.String(50))
    medicines_to_be_taken = db.Column(db.String(50))
    consultation_fee = db.Column(db.Integer)
    doc_who_created_it = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))


################################  REGISTER  LOGIN  LOGOUT ROUTES ###################################


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = User.query.filter_by(username=username,
                                    password=password).first()

        if data is not None:
            session['user'] = data.id
            print(session['user'])
            return redirect(url_for('index'))

        return render_template('incorrectLogin.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'],
                        password=request.form['password'])

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


####################################  ROUTES TO DISPLAY #########################################

@app.route('/show')
def show():
    show_user = User.query.all()
    show_doc = Doctor.query.all()
    return render_template('show.html', show_user=show_user, show_doc=show_doc)


@app.route('/showfiles')
def showfiles():
    show_doc = Files.query.all()

    return render_template('showfiles.html', show_doc=show_doc)


@app.route('/showAppointment')
def showAppointment():
    show_appointment = Appointment.query.all()
    return render_template('showAppointment.html', show_appointment=show_appointment)


####################################  OTHER ROUTES  #########################################

@app.route('/index')
def index():
    username = User.query.get(session['user']).username
    print(username)
    show_doc = Doctor.query.all()
    myAppointments = Appointment.query.filter_by(createdby_name=username).filter_by(status='Confirmed').all()
    return render_template('index.html', myAppointments=myAppointments,show_doc=show_doc)


@app.route('/UserviewAppointments')
def UserviewAppointments():
    username = User.query.get(session['user']).username
    print(username)
    myAppointments = Appointment.query.filter_by(createdby_name=username).all()
    return render_template('UserviewAppointments.html', myAppointments=myAppointments)


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        user_id = session['user']
        print(user_id)
        new_appointment = Appointment(docName=request.form['docName'],
                                      department=request.form['department'],
                                      date=request.form['date'], time=request.form['time'], mode=request.form['mode'],
                                      createdby_id=user_id, createdby_name=User.query.get(user_id).username)

        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('index'))
    else:

        return render_template('appointment.html')


# @app.route("/upload-image", methods=["GET", "POST"])
# def upload_image():
#     if request.method == "POST":
#         if request.files:
#             file = request.files["file"]
#             print(file)
#             new_file= Files(name=file.filename, data=file.read())
#             db.session.add(new_file)
#             db.session.commit()
#             return redirect(request.url)
#
#     return render_template("upload_image.html")


@app.route('/editProfile', methods=['GET', 'POST'])
def editProfile():
    if request.method == 'POST':
        user_id = session['user']
        print(user_id)

        new_profile = UserProfile(name=request.form['name'],
                                  age=request.form['age'],
                                  gender=request.form['gender'], bloodGroup=request.form['bloodGroup'],
                                  heredityIssues=request.form['heredityIssues'],
                                  contactNumber=request.form['contactNumber'], createdby_id=user_id)

        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('editProfile.html')


@app.route('/profile')
def profile():
    id = session['user']
    Profile = UserProfile.query.filter_by(createdby_id=id).all()
    return render_template('profile.html', Profile=Profile)


@app.route('/diseases', methods=['GET', 'POST'])
def diseases():
    id = session['user']
    user_id = User.query.get(id)
    if request.method == 'POST':
        details = Diseases(desc=request.form['desc'],
                           allergy=request.form['allergy'],
                           createdby_id=id)
        db.session.add(details)
        db.session.commit()
        return redirect(url_for('history'))
    else:
        return render_template('diseases.html')


@app.route('/medicines', methods=['GET', 'POST'])
def medicines():
    id = session['user']
    user_id = User.query.get(id)
    if request.method == 'POST':
        details = Medicines(name=request.form['name'],
                            dose=request.form['dose'],
                            medicine=request.form['medicine'],
                            createdby_id=id)
        db.session.add(details)
        db.session.commit()
        return redirect(url_for('history'))
    else:
        return render_template('medicines.html')


@app.route('/history')
def history():
    id = session['user']
    print(id)
    diseases = Diseases.query.filter_by(createdby_id=id).all()
    medicines = Medicines.query.filter_by(createdby_id=id).all()
    feedback = Feedback.query.filter_by(patient_id=id).all()
    return render_template('history.html', diseases=diseases, medicines=medicines, feedback=feedback)


# @app.route('/viewhistory')
# def viewhistory():
#     id = session['user']
#     print(id)
#     history = History.query.filter_by(createdby_id=id).all()
#     return render_template('viewhistory.html', history=history)




######################################### ROUTES FOR THE DOCTORS ####################################

# *****  DOCTOR SIDE *****

@app.route('/dlogin', methods=['GET', 'POST'])
def dlogin():
    if request.method == 'GET':
        return render_template('dlogin.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = Doctor.query.filter_by(username=username,
                                      password=password).first()

        if data is not None:
            session['doctor'] = data.id
            print(session['doctor'])
            return redirect(url_for('dindex'))
        return render_template('incorrectLogin.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/dregister/', methods=['GET', 'POST'])
def dregister():
    if request.method == 'POST':
        new_user = Doctor(username=request.form['username'], department=request.form['department'],
                          password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('dlogin'))
    return render_template('dregister.html')


@app.route('/dlogout', methods=['GET', 'POST'])
def dlogout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/dindex')
def dindex():
    docname = Doctor.query.get(session['doctor']).username
    print(docname)
    myAppointments = Appointment.query.filter_by(docName=docname).filter_by(status='Confirmed').all()
    print(myAppointments)
    return render_template('dindex.html', myAppointments=myAppointments)


@app.route('/viewAppointments')
def viewAppointments():
    doctor_id = session['doctor']
    docname = Doctor.query.get(doctor_id).username
    myAppointments = Appointment.query.filter_by(docName=docname).all()
    print(myAppointments)
    return render_template('viewAppointments.html', myAppointments=myAppointments)


@app.route('/ConfirmAppointment')
def ConfirmAppointment():
    id = int(request.args['id'])
    print('to be confirmed ', id)
    confirm_appointment = Appointment.query.filter_by(id=id).one()
    print(confirm_appointment)
    confirm_appointment.status = 'Confirmed'
    db.session.commit()
    return redirect(url_for('dindex'))


@app.route('/CancelAppointment')
def CancelAppointment():
    id = int(request.args['id'])
    print('to be cancelled ', id)
    CancelAppointment = Appointment.query.filter_by(id=id).one()
    print(CancelAppointment)
    CancelAppointment.status = 'Denied'
    db.session.commit()
    return redirect(url_for('dindex'))


@app.route('/notification')
def Notification():
    doctor_id = session['doctor']
    docname = Doctor.query.get(doctor_id).username
    myAppointments = Appointment.query.filter_by(docName=docname).filter_by(status='Pending').all()
    print('notification', myAppointments)
    return render_template('notification.html', myAppointments=myAppointments)


@app.route('/doc_view_history')
def doc_view_history():
    id = int(request.args['id'])
    print('toview_history ', id)
    diseases = Diseases.query.filter_by(createdby_id=id).all()
    medicines = Medicines.query.filter_by(createdby_id=id).all()
    return render_template('doc_view_history.html', diseases=diseases, medicines=medicines)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    doc_id = session['user']
    docname = Doctor.query.get(doc_id).username
    user_id = int(request.args['id'])
    if request.method == 'POST':
        details = Feedback(patient_name=request.form['patient_name'], doc_name=docname,
                           feedback=request.form['feedback'],
                           medicines_to_be_taken=request.form['medicines_to_be_taken'],
                           consultation_fee=request.form['consultation_fee'],
                           doc_who_created_it=doc_id, patient_id=user_id)
        db.session.add(details)
        db.session.commit()
        return redirect(url_for('dindex'))
    else:
        return render_template('feedback.html')


######################################### MAIN ####################################


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
