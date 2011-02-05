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
    name = db.Column(db.String)
    email = db.Column(db.String)
    content = db.Column(db.String)

    def __init__(self, post, name, email, content):
        self.post = post
        self.name = name
        self.email = email
        self.content = content

@app.route("/posts/<permalink>/")
def comments(permalink):
    return str(get_permalinks())

if __name__ == "__main__":
    app.run(debug=True)