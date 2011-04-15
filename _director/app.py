import urllib
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, Response, redirect
from functools import wraps
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

    # we may want to implement a more sophisticated spam deterrent in the future
    def check_if_spam(self):
        if self.honeypot:
            return True
        else:
            return False

    @property
    def is_valid(self):
        if self.post and self.author and self.email and self.content and self.date:
            if not self.check_if_spam():
                return True
        
        return False
    
    @property    
    def is_recent(self):
        return datetime.now() - self.date < timedelta(days=5)

    def __init__(self, post, author, email, content, website=None, date=datetime.now(), suikerklontje='', **kwargs):    
        self.post = post
        self.author = author
        self.email = email
        self.content = content
        self.website = website
        self.date = date
        self.honeypot = suikerklontje

    @property
    def content_html(self):
        parts = self.content.split("\n\n")
        parts = ["<p>" + part + "</p>" for part in parts]
        return "\n\n".join(parts)
        
    def gravatar_url(self, size=80):
        url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email).hexdigest() + "?"
        url += urllib.urlencode({'d': 'identicon', 's': size})
        return url

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == data.settings["USERNAME"] and password == data.settings["PASSWORD"]

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

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
    raw_date = "-".join(permalink.lstrip('/').split('/')[:3])
    date = datetime.strptime(raw_date, '%Y-%m-%d')
    post_is_recent = datetime.now() - date < timedelta(days=10)
    post_is_lively = len([match for match in matches if match.is_recent])
    allows_comments = post_is_recent or post_is_lively
    return render_template('comments.html', 
        comments=matches, 
        permalink=permalink, 
        allows_comments=allows_comments,
        )

@app.route("/comments/", methods=['POST'])
def post_comment():
    # transforms a multidict into a regular dict
    data = {}
    for key in request.form:
        data[key] = request.form[key]

    comment = Comment(**data)
    
    if comment.is_valid:
        db.session.add(comment)
        db.session.commit()
        return render_template('comment.html', comment=comment), 201
    else:
        return '', 400

@app.route("/comments/moderation/", methods=['GET'])
@requires_auth
def moderate_comments():
    comments = Comment.query.order_by(Comment.date.desc())[:20]    
    return render_template('moderation.html', comments=comments)

@app.route("/comments/<id>/", methods=['POST', 'DELETE'])
@requires_auth
def delete_comment(id):
    if request.form['_method'] != 'DELETE':
        return '', 400
    
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return redirect('/director/comments/moderation/')

if __name__ == "__main__":
    app.run(debug=False)