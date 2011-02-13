from flask import Flask, render_template
from flaskext.sqlalchemy import SQLAlchemy
import data
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://db.db'
db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String)
    # we want to store the GMT datetime, so that we can use some javascript trickery
    # to say "x time ago" or adapt the time to the user's timezone
    date = db.Column(db.DateTime)
    name = db.Column(db.String)
    email = db.Column(db.String)
    content = db.Column(db.String)

    def __init__(self, post, date, name, email, website, content):
        self.post = post
        self.date = date
        self.name = name
        self.email = email
        self.website = website
        self.content = content

@app.route("/posts/")
def posts():
    info = data.get_post_info()
    return render_template('dashboard.html', posts=info)

@app.route("/posts/<permalink>/")
def comments(permalink):
    return data.get_permalinks()

if __name__ == "__main__":
    app.run(debug=True)