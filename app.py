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
    title = db.Column(db.String(100))
    peerlimit = db.Column(db.Integer)
    peernum = db.Column(db.Integer)

    def __init__(self,link,description,peerlimit,title):
        self.link=link
        self.description=description
        self.peerlimit=peerlimit+1
        self.peernum=1
        self.title=title

@app.route("/", methods=["GET"]) 
def home_view(): 
        projectsq = Projects.query.all()
        projects = []
        for project in projectsq:
            projects.append({
                "description" : project.description,
                "peernum" : project.peernum,
                "peerlimit" : project.peerlimit,
                "title" : project.title,
                "link" : "/projects/join/"+str(project.id)
            })
        context = {
            "projects" : projects
        }

        return render_template("index.html",**context)
@app.route("/projects/add", methods=["POST"]) 
def add_project(): 
        project = Projects.query.filter_by(link=request.json['link']).first()
        if project is None:
            if request.json['peerlimit']==0:
                return jsonify(
                    id = -1
                )
            project = Projects(request.json['link'],request.json['description'],int(request.json['peerlimit']),request.json['title'])
            db.session.add(project)
            db.session.commit()
            return jsonify(
                id = project.id
            )
        if int(request.json['peerlimit'])<=project.peernum:
            db.session.delete(project)
            db.session.commit()
            return jsonify(
                id = -1
            )
        project.description=request.json['description']
        project.peerlimit=int(request.json['peerlimit'])
        project.title=request.json['title']
        db.session.commit()
        return jsonify(
            id = project.id
        )
@app.route("/projects/join/<path:id>", methods=["GET"]) 
def delete_project(id): 
        project = Projects.query.filter_by(id=id).first()
        link = project.link
        project.peernum+=1
        if project.peerlimit==project.peernum:
            db.session.delete(project)
        db.session.commit()
        return redirect(link)

if __name__ == "__main__":
            app.run()