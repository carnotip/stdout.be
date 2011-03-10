import urllib
import hashlib
from datetime import datetime
from flask import Flask, render_template, request
from flaskext.sqlalchemy import SQLAlchemy
import data
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../comments.db'
db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String)
    author = db.Column(db.String)
    email = db.Column(db.String)
    content = db.Column(db.String)
    website = db.Column(db.String)
    # we want to store the GMT datetime, so that we can use some javascript trickery
    # to say "x time ago" or adapt the time to the user's timezone
    date = db.Column(db.DateTime)

    # todo
    def check_if_spam(self):
        return False

    @property
    def is_valid(self):
        if self.post and self.author and self.email and self.content and self.date:
            if not self.check_if_spam():
                return True
        
        return False

    def __init__(self, post, author, email, content, website=None, date=datetime.now()):    
        self.post = post
        self.author = author
        self.email = email
        self.content = content
        self.website = website
        self.date = date

    @property
    def content_html(self):
        parts = self.content.split("\n\n")
        parts = ["<p>" + part + "</p>" for part in parts]
        return "\n\n".join(parts)
        
    def gravatar_url(self, size=80):
        url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email).hexdigest() + "?"
        url += urllib.urlencode({'d': 'identicon', 's': size})
        return url

#@app.route("/posts/")
def posts():
    info = data.get_post_info()
    # 1. group comments by permalink and do an aggregate
    # 2. do the same for old permalinks
    # 3. take the sum of both
    return render_template('dashboard.html', posts=info)

@app.route("/comments/", methods=['GET'])
def comments():
    permalink = request.args.get('permalink')
    matches = Comment.query.filter_by(post=permalink).all()
    return render_template('comments.html', comments=matches)

#@app.route("/comments/", methods=['POST'])
def post_comment():
    data = {
        "post": request.args.get('permalink'), 
        "author": request.args.get('author'), 
        "email": request.args.get('email'), 
        "content": request.args.get('content'), 
        "website": request.args.get('website'), 
        }
    
    comment = Comment(**data)
    
    if comment.is_valid:
        db.session.add(comment)
        db.session.commit()
        return '', 201
    else:
        return '', 400

if __name__ == "__main__":
    app.run(debug=False)