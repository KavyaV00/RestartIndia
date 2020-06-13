from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'), db.ForeignKey('history.id'))
    createdby_name=db.Column(db.String(50))
    status = db.Column(db.String(50), default='Pending')


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(50))
    allergy = db.Column(db.String(50))
    med = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# *****  DOCTOR SIDE *****
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))


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
    return render_template('show.html', show_user=show_user,show_doc=show_doc)


@app.route('/showAppointment')
def showAppointment():
    show_appointment = Appointment.query.all()
    return render_template('showAppointment.html', show_appointment=show_appointment)




####################################  OTHER ROUTES  #########################################

@app.route('/index')
def index():
    username = User.query.get(session['user']).username
    print(username)
    myAppointments = Appointment.query.filter_by(createdby_name=username).filter_by(status='Confirmed').all()
    return render_template('index.html',myAppointments=myAppointments)

@app.route('/history', methods=['GET', 'POST'])
def history():
    id = session['user']
    if request.method =='POST':
        details = History(desc=request.form['desc'],
                        allergy=request.form['allergy'],
                        med=request.form['med'],
                       createdby_id=id)
        db.session.add(details)
        db.session.commit()
        return redirect(url_for('viewhistory'))
    else:
        return render_template('history.html')

@app.route('/viewhistory')
def viewhistory():
    id = session['user']
    history = History.query.filter_by(createdby_id=id).all()
    return render_template('viewhistory.html', history=history)


@app.route('/UserviewAppointments')
def UserviewAppointments():
    username = User.query.get(session['user']).username
    print(username)
    myAppointments = Appointment.query.filter_by(createdby_name=username).all()
    return render_template('UserviewAppointments.html',myAppointments=myAppointments)

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
        new_user = Doctor(username=request.form['username'],
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
    history=[]
    for a in myAppointments:
        dci=a.createdby_id
        history.append(History.query.filter_by(createdby_id=dci).all())
        # history.append(a.createdby_id)
    print(history)
    return render_template('dindex.html', myAppointments=myAppointments, history=set(history))


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
    confirm_appointment.status='Confirmed'
    db.session.commit()
    return redirect(url_for('dindex'))

@app.route('/CancelAppointment')
def CancelAppointment():
    id = int(request.args['id'])
    print('to be cancelled ', id)
    CancelAppointment = Appointment.query.filter_by(id=id).one()
    print(CancelAppointment)
    CancelAppointment.status='Denied'
    db.session.commit()
    return redirect(url_for('dindex'))


@app.route('/notification')
def Notification():
    doctor_id = session['doctor']
    docname = Doctor.query.get(doctor_id).username
    myAppointments = Appointment.query.filter_by(docName=docname).filter_by(status='Pending').all()
    print('notification', myAppointments)
    return render_template('notification.html', myAppointments=myAppointments)



######################################### MAIN ####################################


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
