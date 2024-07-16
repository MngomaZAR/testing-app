from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_bcrypt import Bcrypt
import os
import secrets

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize bcrypt for password hashing
bcrypt = Bcrypt(app)

# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    candidate = db.relationship('Candidate', backref='user', uselist=False)

# Define Candidate model
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(20), nullable=False, default='default.jpg')
    speech = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    votes = db.relationship('Vote', backref='candidate', lazy=True)

# Define Vote model
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    voted_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

# Define forms using WTForms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CandidateForm(FlaskForm):
    name = StringField('Candidate Name', validators=[DataRequired()])
    picture = FileField('Candidate Picture', validators=[DataRequired()])
    speech = TextAreaField('Candidate Speech', validators=[DataRequired()])
    submit = SubmitField('Register')

# Routes for the application
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    candidates = Candidate.query.all()
    if request.method == 'POST':
        candidate_id = request.form['candidate']
        vote = Vote(voter_id=current_user.id, candidate_id=candidate_id)
        db.session.add(vote)
        db.session.commit()
        flash('Your vote has been cast successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('vote.html', title='Vote', candidates=candidates)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    candidates = Candidate.query.all()
    return render_template('admin_dashboard.html', title='Admin Dashboard', candidates=candidates)

@app.route('/register_candidate', methods=['GET', 'POST'])
@login_required
def register_candidate():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = CandidateForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        candidate = Candidate(name=form.name.data, speech=form.speech.data, picture=picture_file, user_id=current_user.id)
        db.session.add(candidate)
        db.session.commit()
        flash('Candidate has been registered successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('candidate_register.html', title='Register Candidate', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/candidate_images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

# USSD endpoint
@app.route('/ussd', methods=['POST'])
def ussd_handler():
    sessionId = request.form['sessionId']
    serviceCode = request.form['serviceCode']
    text = request.form['text']

    if text == '':
        response = "CON Hi, welcome to the Voting System USSD service.\n"
        response += "1. Register\n"
        response += "2. Login\n"
        response += "3. Vote\n"
        response += "4. Admin Dashboard\n"
    elif text == '1':
        response = "CON Please register with your username, email, and password separated by commas (e.g., John,john@example.com,123456)\n"
    elif text.startswith('1*'):
        parts = text.split('*')
        if len(parts) == 4:
            username, email, password = parts[1], parts[2], parts[3]
            # Process registration logic here
            response = "END Registration successful. You can now login.\n"
        else:
            response = "CON Invalid input. Please try again.\n"
    elif text == '2':
        response = "CON Please enter your email and password separated by a comma (e.g., john@example.com,123456)\n"
    elif text.startswith('2*'):
        parts = text.split('*')
        if len(parts) == 3:
            email, password = parts[1], parts[2]
            # Process login logic here
            response = "END Login successful. Welcome.\n"
        else:
            response = "CON Invalid input. Please try again.\n"
    elif text == '3':
        response = "CON Here are the candidates:\n"
        candidates = Candidate.query.all()
        for candidate in candidates:
            response += f"{candidate.id}. {candidate.name}\n"
        response += "Please enter the candidate ID to vote.\n"
    elif text.startswith('3*'):
        parts = text.split('*')
        if len(parts) == 2:
            candidate_id = int(parts[1])
            # Process vote logic here
            response = "END Vote cast successfully.\n"
        else:
            response = "CON Invalid input. Please try again.\n"
    elif text == '4':
        if current_user.is_authenticated and current_user.is_admin:
            # Provide admin options
            response = "CON Admin options:\n"
            response += "1. Register Candidate\n"
            response += "Please enter option number:\n"
        else:
            response = "END You do not have permission to access this.\n"
    elif text.startswith('4*'):
        if current_user.is_authenticated and current_user.is_admin:
            parts = text.split('*')
            if len(parts) == 2:
                option = int(parts[1])
                if option == 1:
                    response = "CON Register Candidate:\n"
                    response += "Enter candidate details (name, speech) separated by commas:\n"
                else:
                    response = "END Invalid option.\n"
            elif len(parts) == 3:
                option = int(parts[1])
                if option == 1:
                    details = parts[2].split(',')
                    if len(details) == 2:
                        name, speech = details[0], details[1]
                        # Process candidate registration logic here
                        response = "END Candidate registered successfully.\n"
                    else:
                        response = "CON Invalid input. Please try again.\n"
                else:
                    response = "END Invalid option.\n"
            else:
                response = "CON Invalid input. Please try again.\n"
        else:
            response = "END You do not have permission to access this.\n"
    else:
        response = "END Invalid input. Please try again.\n"

    return response

if __name__ == '__main__':
    app.run(debug=True)
