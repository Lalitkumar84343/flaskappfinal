from flask import Flask ,render_template,request, redirect,url_for,flash,send_from_directory
import pyotp
import time
import pyqrcode
from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

picsFolder=os.path.join("static","Pics")
app.config["UPLOAD_FOLDER"]=picsFolder


db=SQLAlchemy(app)


class users(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    keys=db.Column(db.String(100))

    def __init__(self,email,password,keys):
        self.email=email
        self.password=password
        self.keys=keys

@app.route('/',methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        uname = request.form["uname"]
        passw = request.form["passw"]
        token = request.form["token"]
        login = users.query.filter_by(email=uname, password=passw).first()
        print("printing:",login.keys)
        if login is not None:
            if token==(pyotp.TOTP(login.keys)).now():
                # return redirect(url_for('report'))
                return render_template('index.html')
 
         
    return render_template('login.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        if not request.form["email_reg"] or not request.form["password_reg"]:
            flash('Please enter all the fields', 'error')
        else:
            random_code=pyotp.random_base32()
            email_name=request.form["email_reg"]
            password_var=request.form["password_reg"]
            user=users(email_name,password_var,random_code)
            img = pyqrcode.create(pyotp.totp.TOTP(random_code).provisioning_uri(name=email_name, issuer_name='Secure App'))
            img.png('/tmp/MyQRCode.png',scale=8)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('qrcode'))
            
    return render_template('register.html')

@app.route('/qrcode',methods=['GET', 'POST'])
def qrcode():
    pic1=os.path.join(app.config["UPLOAD_FOLDER"],"MyQRCode.png")
    return render_template('qrcode.html',user_image=pic1)

if __name__ =="__main__":
    #db.create_al()
    with app.app_context():
        db.create_all()
    app.run(debug=True)



