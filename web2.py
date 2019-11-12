from flask import Flask, flash, redirect, render_template, request, session, abort,url_for,send_file
from flask_sqlalchemy import SQLAlchemy 
from io import BytesIO
a=Flask(__name__)
a.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
a.config['SECRET_KEY']='password'
database=SQLAlchemy(a)
class User(database.Model):
    id=database.Column(database.Integer,primary_key=True)
    name=database.Column(database.String(15))
    username=database.Column(database.String(30))
    password=database.Column(database.String(30))
    filename=database.Column(database.String(300))
    filedata=database.Column(database.LargeBinary)

globalusr='str'

@a.route("/")
def home():
    database.create_all()
    return render_template("home.html")

@a.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        nm=request.form['name']
        usr=request.form['username']
        pas=request.form['password']
        if len(nm)<3 or len(usr)<3 or len(pas)<5:
            return redirect(url_for('signup'))
        con_pas=request.form['con_password']
        if User.query.filter_by(username=usr).first()==None:
            if pas==con_pas:
                newuser=User(name=nm,username=usr,password=pas,filename="notfound")
                database.session.add(newuser)
                database.session.commit()
                global globalusr
                globalusr=usr
                return redirect(url_for('userhome'))
            else:
                return redirect(url_for('signup'))
        else:
            return redirect(url_for('signup'))
    return render_template('signup.html')
        
@a.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        user_name=request.form['username']
        pass_word=request.form['password']
        if User.query.filter_by(username=user_name).first() != None:
           cought=User.query.filter_by(username=user_name).first()
           if cought.password==pass_word:
               global globalusr
               globalusr=user_name 
               return redirect(url_for('userhome'))
           else:
                abort(403,'Wrong username or password')
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@a.route('/userhome')
def userhome():
    global globalusr
    if User.query.filter_by(username=globalusr).first()== None:
        return "you are not logged in"
    return render_template('userhome.html')
@a.route('/upload',methods=['GET','POST'])
def upload():
    global globalusr
    cought=User.query.filter_by(username=str(globalusr)).first()
    if cought==None:
        return "Your are not logged in"
    if request.method=='POST':
        files=request.files['files']
        blob=request.files['files'].read()
        size = len(blob)
        if (size>1000):
            return "Not valid"
        if (files.filename[-1]=="l" and files.filename[-2]=="m" and files.filename[-3]=="t" and files.filename[-4]=="h" and files.filename[-5]==".") or (files.filename[-1]=="p" and files.filename[-2]=="h" and files.filename[-3]=="p" and files.filename[-4]=="."): 
            return "files of this kind is not acceptable"
        else:
            if cought.filename=="notfound":
                cought.filename=files.filename
                cought.filedata=blob
                database.session.commit()
                return "success"

            else:
                newuf=User(username=globalusr,filename=files.filename,filedata=blob)
                database.session.add(newuf)
                database.session.commit()
                return "success"

    return render_template('upload.html')
@a.route('/download',methods=['GET','POST'])
def download():
    global globalusr
    cought=User.query.filter_by(username=str(globalusr)).all()
    if cought==[]:
            return "Your are not logged in"

    for i in cought:
        flash(str(i.filename))

    if request.method=='POST':
        file_name=request.form['download']
        if User.query.filter_by(username=str(globalusr),filename=file_name).first() != None: 
           file_data = User.query.filter_by(username=str(globalusr),filename=file_name).first()
           return send_file(BytesIO(file_data.filedata),attachment_filename=file_name,as_attachment=True)

    return render_template('download.html')
@a.route('/view',methods=['GET','POST'])
def view():
    global globalusr
    cought=User.query.filter_by(username=str(globalusr)).all()
    list_files=[]
    if cought==[]:
            return "Your are not logged in"

    for i in cought:
        list_files.append(str(i.filename))  
        flash(str(i.filename))

    if request.method=='POST':
        view_file=request.form['view']
        if view_file in list_files:
            for i in cought:
                if str(i.filename)==str(view_file):
                    return i.filedata

    return render_template('view.html') 
if __name__=="__main__":
    a.run(debug=True)
