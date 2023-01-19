from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import  FlaskForm
from flask_login import UserMixin,LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from wtforms import StringField,PasswordField,SubmitField,EmailField,FileField
from wtforms.validators import InputRequired,Length,Email,ValidationError
from werkzeug.utils import secure_filename
import os
app=Flask(__name__)
DB_NAME="database.sqlite"
EXTENSIONS=["jpg","png"]
app.config["SECRET_KEY"]='brian'
app.config["UPLOAD_FOLDER"]="static/IMAGES"
PATH=os.path.join(os.path.dirname(__file__),app.config['UPLOAD_FOLDER'])
app.config["SQLALCHEMY_DATABASE_URI"]=f"sqlite:///{DB_NAME}"
login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view="login"
db=SQLAlchemy(app)
db.init_app(app)
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    f_name=db.Column(db.String(10),nullable=False)
    l_name=db.Column(db.String(10),nullable=False)
    email=db.Column(db.String(10),nullable=False,unique=True)
    password=db.Column(db.String(100))
    vie=db.Column(db.Boolean,default=True)
    voted=db.Column(db.Boolean,default=False)
    info=db.relationship("Info")
    candidates=db.relationship('Candidates')
class Info(db.Model):
    id=db.Column(db.Integer,db.ForeignKey("user.id"),primary_key=True)
    image=db.Column(db.String(150),nullable=True)
    address=db.Column(db.String(150))
    city=db.Column(db.String(150))
    sex=db.Column(db.String(4))
    status=db.Column(db.String(10))
class Candidates(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))
    votes=db.Column(db.Integer,default=0)
    country=db.Column(db.String(20))
    county=db.Column(db.String(20))
    ward=db.Column(db.String(20))
    position=db.Column(db.String(20))
    party=db.Column(db.String(20))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
class RegisterForm(FlaskForm):
    firstName=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"FirstName"})
    lastName=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"LastName"})
    email=EmailField(validators=[InputRequired(),Length(min=10,max=40)],render_kw={"placeholder":"Enter email"})
    password=PasswordField(validators=[InputRequired(),Length(min=8,max=20)],render_kw={"placeholder":"enter password"})
    submit=SubmitField("Register")
class LoginForm(FlaskForm):
    email=EmailField(validators=[InputRequired(),Length(min=4,max=40)],render_kw={"placeholder":"Enter Email"})
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={
        "placeholder":"Enter Password"})
    submit=SubmitField("Login")
class UpdateForm(FlaskForm):
    address=StringField(validators=[InputRequired(),Length(min=4,max=10)],render_kw={'placeholder':'Enter Address'})
    city=StringField(validators=[InputRequired(),Length(min=2,max=10)],render_kw={'placeholder':'Enter City'})
    sex=StringField(validators=[InputRequired(),Length(min=1,max=6)],render_kw={"placeholder":"Enter Sex"})
    status=StringField(validators=[InputRequired(),Length(min=1,max=10)],render_kw={
        "placeholder":"Enter Status"
    })
    file=FileField(validators=[InputRequired()])
    submit=SubmitField("Submit")
class VieForm(FlaskForm):
    party=StringField(validators=[InputRequired(),Length(min=4,max=10)],render_kw={"placeholder":"party"})
    country=StringField(validators=[InputRequired(),Length(min=4,max=10)],render_kw={"placeholder":"country"})
    position=StringField(validators=[InputRequired(),Length(min=4,max=10)],render_kw={"placeholder":"position"})
    county=StringField(validators=[InputRequired(),Length(min=4,max=10)],render_kw={"placeholder":"county"})
    ward=StringField(validators=[InputRequired(),Length(min=4,max=10)],render_kw={"placeholder":"ward"})
    submit=SubmitField("Submit")
@app.route('/')
@login_required
def home():
    return render_template("home.html",user=current_user)
@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("Not Registerd",category="error")
            return redirect("register")
        if user.password == form.password.data:
            login_user(user,remember=True)
            return redirect("/")
    return render_template("login.html",form=form,user=current_user)
@app.route("/register",methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("User Already Exists",category="error")
            return redirect("login")
        user=User(f_name=form.firstName.data,l_name=form.lastName.data,email=form.email.data,password=form.password.data,voted=False)
        add_to_database(user)
        login_user(user,remember=True)
        return redirect("/")
    return render_template("register.html",form=form,user=current_user)
@app.route("/update",methods=['GET','POST'])
@login_required
def update():
    form=UpdateForm()
    if form.validate_on_submit():
        info=Info.query.filter_by(id=current_user.id).first()
        if info:
            if info.image:
                delete_file(info.image)
            delete_from_database(info)
        file=form.file.data
        if not check_filename(file.filename):
             redirect(url_for("/upload"))
        file_name=upload(file)
        info=Info(id=current_user.id,image=file_name,address=form.address.data,city=form.city.data,sex=form.sex.data,status=form.status.data)
        add_to_database(info)
        return redirect("/")
    return render_template("update.html",form=form,user=current_user)
def upload(file):
      file_name=secure_filename(file.filename)
      file.save(os.path.join(PATH,file_name))
      return file_name
def delete_file(filename):
      os.unlink(os.path.join(PATH,filename))
def check_filename(filename):
    return "." in filename and filename.split(".",1)[1] in EXTENSIONS
def add_to_database(record):
    db.session.add(record)
    db.session.commit()
def delete_from_database(record):
    db.session.delete(record)
    db.session.commit()
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("login")
@app.route("/vie",methods=['GET','POST'])
@login_required
def vie():
    form=VieForm()
    if form.validate_on_submit():
        if   Candidates.query.filter_by(user_id=current_user.id).first():
            flash("Cannot Vie Twice",category='error')
            return redirect("/")
        else:
            Candidates(name=current_user.f_name,party=form.party.data,country=form.country.data,position=form.position.data,county=form.county.data,ward=form.ward.data)
            flash("Successfully Vied",category='success')
            return redirect('/')
    return render_template("vie.html",form=form,user=current_user)
@app.route('/vote',methods=['POST','GET'])
@login_required
def vote():
    candidates=Candidates.query.all()
    return render_template("vote.html",user=current_user,list=candidates)
@app.route("/result")
@login_required
def result():
    pass
if __name__=="__main__":
    db.create_all()
    app.run(debug=True)
 