from xml.etree.ElementTree import ElementTree
from urlparse import urlparse
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://db.db'
db = SQLAlchemy(app)

def get_permalinks():
    tree = ElementTree()
    # /_site/sitemap.xml actually
    root = tree.parse("../sitemap.xml")
    links = []
    for link in root.findall("*/{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        absolute_url = urlparse(link.text).path
        links.append(absolute_url)
    return links

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

@app.route("/posts/<permalink>/")
def comments(permalink):
    return str(get_permalinks())

if __name__ == "__main__":
    app.run(debug=True)