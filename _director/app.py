import urllib
import hashlib
from datetime import datetime
from flask import Flask, render_template, request
from flaskext.sqlalchemy import SQLAlchemy
import data
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../comments.db'
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

    def __init__(self, post, author, email, content, website=None, date=datetime.now()):
        self.post = post
        self.author = author
        self.email = email
        self.content = content
        self.website = website
        self.date = date
        
    def gravatar_url(self, size=80):
        url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email).hexdigest() + "?"
        url += urllib.urlencode({'d': 'identicon', 's': size})
        return url

@app.route("/posts/")
def posts():
    info = data.get_post_info()
    # 1. group comments by permalink and do an aggregate
    # 2. do the same for old permalinks
    # 3. take the sum of both
    return render_template('dashboard.html', posts=info)

@app.route("/comments/", methods=['GET'])
def comments():
    permalink = request.args.get('permalink')
    old_permalink = data.get_old_url(permalink)
    matches = Comment.query.filter(Comment.post.in_([old_permalink, permalink])).all()
    return render_template('comments.html', comments=matches)

@app.route("/comments/", methods=['POST'])
def post_comment():
    permalink = request.args.get('permalink')
    comment = Comment('/2010/05/05/something/', 'Stijn D.', 'stijn-at-stdout.be', 'Hello world.')
    db.session.add(comment)
    db.session.commit()
    return 'OK'

if __name__ == "__main__":
    app.run(debug=True)