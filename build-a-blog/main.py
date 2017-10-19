from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheese@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(15000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(40))
    blogs = db.relationship('Blog', backref='owner') # need to put 'owner' in Blog

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    num = request.args.get('id')
    if num:
        user = User.query.get(num)
        blogs = user.blogs
        return render_template('user.html', blogs=blogs)
    else:
        users = User.query.all()
        return render_template('index.html', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method=='POST':
        owner = User.query.filter_by(username=session['username']).first()
        title = request.form['new_title']
        body = request.form['new_blog']

        if title=='' or body=='':
            title_error=''
            body_error=''
            if title=='':
                title_error='Please fill in the title'
            if body=='':
                body_error='Please fill in the body'
            return render_template("newpost.html", title = "Build a Blog", 
                    title_error = title_error, body_error=body_error)   
        else:
            blog = Blog(title, body, owner)
            db.session.add(blog)
            db.session.commit()

            return render_template("single_post.html", blog = blog)
    
    users = User.query.all()
    blogs = Blog.query.all()

    num = request.args.get('id')
    if num:
        blog = Blog.query.get(num)
        return render_template('single_post.html', blog=blog, users=users)
        
    return render_template("blog.html", title = "Blogz", blogs=blogs, users=users)

@app.route('/newpost')
def newpost_page():
    return render_template("newpost.html", title = "Add a Blog Entry")



@app.route('/login', methods=['POST', 'GET'])
def login():
    e1 = ''
    e2 = ''
    e3=''
    e4=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if username == '' or password=='':
            if username=='':
                e1 = 'Please enter a username'
            if password == '':
                e2 = 'Please enter a password'
            return render_template('login.html', e1=e1, e2=e2)

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif user and user.password != password:
            e3 = 'Password is incorrect'
            return render_template('login.html', e3=e3)
        elif not user:
            e4 = 'User does not exist'
            return render_template('login.html', e4=e4)

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    e1=''
    e2=''
    e3=''
    e4=''
    e5=''
    e6=''
    e7=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if username == '' or password=='' or verify=='':
            if username=='':
                e1 = 'Please enter a username'
            if password == '':
                e2 = 'Please enter a password'
            if verify =='':
                e3 = 'Please verify password'
            return render_template('signup.html', e1=e1, e2=e2, e3=e3)
        if password != verify:
            e4 = 'Passwords do not match'
            return render_template('signup.html', e4=e4)
        if len(username)<3 or len(password)<3:
            if len(username)<3:
                e5 = 'Username must be more than three characters'
            if len(password)<3:
                e6 = 'Password must be more than three characters'
            return render_template('signup.html', e5=e5, e6=e6)
        if existing_user:
            e7 = 'User already exists'
            return render_template('signup.html', e7=e7)
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__=='__main__':
    app.run()