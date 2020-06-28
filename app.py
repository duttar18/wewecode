from flask import Flask, request, jsonify,redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import flask_cors
from flask_cors import CORS, cross_origin
import os
  
app = Flask(__name__) 
basedir = os.path.abspath(os.path.dirname(__file__))
CORS(app)

#Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)

class Projects(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    link = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    peerlimit = db.Column(db.Integer)
    peernum = db.Column(db.Integer)
    openspot = db.Column(db.Boolean)

    def __init__(self,link,description,peerlimit):
        self.link=link
        self.description=description
        self.peerlimit=peerlimit+1
        self.peernum=1
        self.openspot = True
        if self.peerlimit==self.peernum:
            self.openspot=False

@app.route("/", methods=["GET"]) 
def home_view(): 
        projectsq = Projects.query.filter_by(openspot=True).all()
        projects = []
        for project in projectsq:
            projects.append({
                "description" : project.description,
                "peernum" : project.peernum,
                "peerlimit" : project.peerlimit,
                "link" : "/projects/join/"+str(project.id)
            })
        context = {
            "projects" : projects
        }

        return render_template("index.html",**context)
@app.route("/projects/add", methods=["POST"]) 
def add_project(): 
        project = Projects(request.json['link'],request.json['description'],int(request.json['peerlimit']))
        db.session.add(project)
        db.session.commit()
        return jsonify(
            id = project.id
        )
@app.route("/projects/join/<path:id>", methods=["GET"]) 
def delete_project(id): 
        project = Projects.query.filter_by(id=id).first()
        if not project.openspot:
            return redirect("/")
        link = project.link
        project.peernum+=1
        if project.peerlimit==project.peernum:
            project.openspot=False
        db.session.commit()
        return redirect(link)

if __name__ == "__main__":
            app.run()