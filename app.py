from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import  FlaskForm
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from wtforms import StringField,PasswordField,SubmitField,EmailField
from wtforms.validators import InputRequired,Length,Email,ValidationError
app=Flask(__name__)
DB_NAME="database.sqlite"
app.config["SECRET_KEY"]='brian'
app.config["SQLALCHEMY_DATABASE_URI"]=f"sqlite:///{DB_NAME}"
login_manager = LoginManager()
login_manager.init_app(app=app)
db=SQLAlchemy(app)
db.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    f_name=db.Column(db.String(10),nullable=False)
    l_name=db.Column(db.String(10),nullable=False)
    email=db.Column(db.String(10),nullable=False,unique=True)
    password=db.Column(db.String(100))
    voted=db.Column(db.Boolean) 
class RegisterForm(FlaskForm):
    firstName=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"FirstName"})
    lastName=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"LastName"})
    email=EmailField(validators=[InputRequired(),Length(min=10,max=20)],render_kw={"placeholder":"Enter email"})
    password=PasswordField(validators=[InputRequired(),Length(min=8,max=20)],render_kw={"placeholder":"enter password"})
    submit=SubmitField("Register")
class LoginForm(FlaskForm):
    email=EmailField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Enter Email"})
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={
        "placeholder":"Enter Password"})
    submit=SubmitField("Login")
@app.route('/home')
@login_required
def home():
    return render_template("home.html")
@app.route('/',methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("Not Registerd",category="error")
            return redirect("register")
        if user.password == form.password.data:
            return redirect("home")
    return render_template("login.html",form=form)
@app.route("/register",methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("User Already Exists",category="error")
            return redirect("login")
        user=User(f_name=form.firstName.data,l_name=form.lastName.data,email=form.email.data,password=form.password.data,voted=False)
        db.session.add(user)
        db.session.commit()
        return redirect("login")
    return render_template("register.html",form=form)
if __name__=="__main__":
    db.create_all()
    app.run(debug=True)
