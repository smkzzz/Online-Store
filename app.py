from flask import Flask, render_template, request,redirect,url_for,session,flash,make_response,g
from dbhelper import *

app = Flask(__name__, template_folder='templates')
app.secret_key ='!@@#S'
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/login',methods=['POST','GET'])
def login():
    username = ""
    password = ""
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            if username == '' or password == '':
                flash('Please fill all fields')
            elif getuser('user',username=username,password=password):
                session['username'] = 'admin'
                return redirect(url_for('home'))
            else:
                flash('Incorrect username or password.')
        except:
            flash('An error occured while connecting to database.')
    return render_template('login.html',title='Login', password=password,username=username)

@app.route('/update/<id>',methods=['GET'])
@app.route('/update',methods=['POST'])
def update(id=None):
    try:
        if 'username' not in session:
            flash('You need to login first')
            return redirect(url_for('login'))
        if request.method == 'POST':
            fields = request.form.to_dict()
            fields = {'idno': session['idno']} | fields
            if not bool(fields):
                flash(f'Fill all fields.')
                return redirect(f'/update/{session["idno"]}')
            for key in fields:
                if fields[key] == '':
                    flash(f'Field {key} is required.')
                    return redirect(f'/update/{session["idno"]}')
            if updaterecord('student',**fields):
                flash(f'Successfully Updated!','info')
                return redirect(url_for('home'))
            else:
                flash('No Changes made!','warning')
                return redirect(url_for('home',idno='1'))
        session['idno'] = id
        details = getrecord('student',idno=id)
        if len(details) <= 0:
            flash('Invalid Student IDNO')
            return redirect(url_for('home'))
        details= details[0]
        return render_template('update.html',title='Update', details=details)
    except Exception as e:
        print(e)
        flash("There was an error while loading the page.")
        return redirect(url_for('home'))

@app.route('/delete/<id>',methods=['GET'])
def delete(id):
    try:
        if 'username' not in session:
            flash('You need to login first')
            return redirect(url_for('login'))
            
        if deleterecord('student',idno=id):
            flash('Deleted Successfully','danger')
        else:
            flash('Student not found', 'danger')
        return redirect(url_for('home'))
    except:
        flash("There was an error while loading the page.")
        return redirect(url_for('home'))
@app.route('/create',methods=['POST','GET'])
def create():
    try:
        if 'username' not in session:
            flash('You need to login first')
            return redirect(url_for('login'))
        if request.method == 'POST':
            fields = request.form.to_dict()
            if not bool(fields):
                flash(f'Fill all fields.')
                return render_template('create.html',fields=fields,title='Create Student') 
            for key in fields:
                if fields[key] == '':
                    flash(f'Field {key} is required.')
                    return render_template('create.html',fields=fields,title='Create Student')
            try:
                if addrecord('student',**fields):
                    session['idno'] = fields['idno']
                    flash('New Student added!','success')
            except:
                flash('Student already exist','danger')
                return render_template('create.html',fields=fields,title='Create Student')
            return redirect(url_for('home'))
        fields = {
            'idno':'',
            'firstname':'',
            'lastname':'',
            'course':'',
            'level':''
        }
        return render_template('create.html',fields=fields,title='Create Student')
    except:
        flash("There was an error while loading the page.")
        return redirect(url_for('home'))
@app.route('/home',methods=['POST','GET'])
def home():
    if 'username' not in session:
        flash('You need to login first')
        return redirect(url_for('login'))
    if request.method == 'POST':
        id = request.form['idno']
    records = getall('student')
    idno = session['idno'] if 'idno' in session else None
    if 'idno' in session:
        session.pop('idno')
    print(idno)
    return render_template('home.html', idno=idno,records=records,title='Student List', headers=records[0] if len(records) > 0 else [])

@app.route('/')
def main():
    return render_template('index.html',title='WELCOME HOME')
if __name__ == '__main__':  
    app.run(host='0.0.0.0', debug=True, port=5000)
