from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cheese@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(15000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.method=='POST':
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
            blog = Blog(title, body)
            db.session.add(blog)
            db.session.commit()

            return render_template("single_post.html", blog = blog)

    blogs = Blog.query.all()
    
    num = request.args.get('id')
    if num!=None:
        for blog in blogs:
            if blog.id==int(num):
                return render_template("single_post.html", blog=blog)
   

    return render_template("blog.html", title = "Build a Blog", blogs=blogs)



@app.route('/newpost')
def newpost_page():
    return render_template("newpost.html", title = "Add a Blog Entry")



if __name__=='__main__':
    app.run()