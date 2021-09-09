import os
import re
from flask import Flask, request, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_migrate import Migrate
import datetime
import pytz
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sds_api'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///sds_api.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)
api = Api(app)


class SDS_Members(db.Model):    
    name = db.Column(db.String(100))
    mis = db.Column(db.Integer(), primary_key=True, nullable=False)
    email = db.Column(db.String())
    since = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(member, name, mis, email):
        member.name = name
        member.mis = mis
        member.email = email

    def json(member):
        return {'Name: ': member.name, 'MIS: ': member.mis, 'Email: ': member.email}

    def __str__(member):
        return f" Name of SDS Member: {member.name}\nMIS: {member.mis}\nEmail: {member.email}"
    

class SDS_Projects(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    projectName = db.Column(db.String(100))
    projectDesc = db.Column(db.String(500))
    mis_projectHead = db.Column(db.Integer())
    email_projectHead = db.Column(db.String())
    started = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(project, projectName, projectDesc, mis_projectHead, email_projectHead):
        project.projectName = projectName
        project.projectDesc = projectDesc
        project.mis_projectHead = mis_projectHead
        project.email_projectHead = email_projectHead

    def json(project):
        return {'Name: ': project.projectName, 'Project Description: ': project.projectDesc, 'MIS of Project Head: ': project.mis_projectHead, 'Email of Project Head: ': project.email_projectHead}

    def __str__(project):
        return f" Name of Project: {project.name}\nProject Description: {project.desc}\nMIS: {project.mis}\nEmail: {project.email}"

class SDS_API_History(db.Model):   
    id = db.Column(db.Integer(), primary_key=True) 
    operation = db.Column(db.String())
    performedOn = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(history, operation):
        history.operation = operation

    def json(history):
        return {'Operation ': history.operation}

    def __str__(history):
        return f" Operation Performed: {history.operation}"

db.create_all()
# member = SDS_Members(name="SHIKHAR", mis=112003005, email="agarawalsd20.comp@coep.ac.in")
# db.session.add(member)
# db.session.commit()
@app.route("/")
def HomePage():
    return render_template("sds_api_home.html")


@app.route('/members', methods=['GET'])
def read_members():
    if request.method == 'GET':
        members = SDS_Members.query.all()
        history = SDS_API_History(operation="Read Members")
        db.session.add(history)
        db.session.commit()
        return render_template("members.html", get=members)


@app.route('/members/', methods=['GET', 'POST'])
def create_member():
    if request.method == 'GET':
        return render_template("members_form.html")
    if request.method == 'POST':
        name = request.form['Name']
        mis = request.form['MIS']
        email = request.form['Email']

        members = SDS_Members(name, mis, email)
        db.session.add(members)
        db.session.commit()
        history = SDS_API_History(operation=("Created Member: " + str(mis)))
        db.session.add(history)
        db.session.commit()
        return redirect(url_for('read_members'))


@app.route('/members/delete/<mis>')
def delete_member(mis):
    ex_member = SDS_Members.query.filter_by(mis=mis).first()
    history = SDS_API_History(operation="Deleted Member: " + str(mis))
    db.session.delete(ex_member)
    db.session.add(history)
    db.session.commit()
    return redirect("/members")


@app.route('/members/update/<mis>', methods=['GET', 'POST'])
def update_member(mis):
    member = SDS_Members.query.filter_by(mis=mis).first()
    if request.method == 'GET':
        return render_template("members_update.html", update=member)
    if request.method == 'POST':
        member.name = request.form['Name']
        member.mis = request.form['MIS']
        member.email = request.form['Email']
        history = SDS_API_History(operation="Updated Member Info")
        db.session.add(history)
        # members = SDS_Members(name, mis, email)
        # db.session.update(members)
        db.session.commit()

        return redirect(url_for('read_members'))

@app.route('/projects', methods=['GET'])
def read_projects():
    if request.method == 'GET':
        projects = SDS_Projects.query.all()
        history = SDS_API_History(operation="Read Projects")
        db.session.add(history)
        db.session.commit()
        return render_template("project.html", get=projects)

@app.route('/projects/', methods=['GET', 'POST'])
def create_project():
    project = SDS_Projects(projectName="projectName", projectDesc="projectDesc", mis_projectHead=000000000, email_projectHead="email_projectHead")
    db.session.add(project)
    if request.method == 'GET':
        return render_template("projects_form.html")
    if request.method == 'POST':
        project.projectName = request.form['projectName']
        project.projectDesc = request.form['projectDesc']
        project.mis_projectHead = request.form['Mis_projectHead']
        project.email_projectHead = request.form['Email_projectHead']
        history = SDS_API_History(operation=("Created Project: " + project.projectName))
        db.session.add(history)
        # print(request.form['projectName'], ['projectDesc'], ['Mis_projectHead'], ['Email_projectHead'])
        # print(projectName, projectDesc, mis_projectHead, email_projectHead)
        # newProject = SDS_Projects(projectName=projectName, projectDesc=projectDesc, mis_projectHead=mis_projectHead, email_projectHead=email_projectHead)
        # db.session.add(newProject)
        db.session.commit()


        return redirect(url_for('read_projects'))

@app.route('/projects/delete/<projectName>')
def delete_project(projectName):
    old_project = SDS_Projects.query.filter_by(projectName=projectName).first()
    history = SDS_API_History(operation=("Deleted Project: " + projectName))
    db.session.delete(old_project)
    db.session.add(history)
    db.session.commit()
    return redirect("/projects")

@app.route('/projects/update/<projectName>', methods=['GET', 'POST'])
def update_project(projectName):
    project = SDS_Projects.query.filter_by(projectName=projectName).first()
    if request.method == 'GET':
        return render_template("project_update.html", update=project)
    if request.method == 'POST':
        project.projectName = request.form['projectName']
        project.projectDesc = request.form['projectDesc']
        project.mis_projectHead = request.form['Mis_projectHead']
        project.email_projectHead = request.form['Email_projectHead']
        history = SDS_API_History(operation="Updated Project Info")
        db.session.add(history)
        db.session.commit()
        # members = SDS_Members(name, mis, email)
        # db.session.update(members)


        return redirect(url_for('read_projects'))

@app.route('/history', methods=['GET'])
def read_history():
    if request.method == 'GET':
        history = SDS_API_History.query.all()
        return render_template("history.html", get=history)

class SDS_Member(Resource):
    def get(self,name, mis, email):
        check_member = db.session.query(db.exists().where(SDS_Members.mis == mis and SDS_Members.name == name and SDS_Members.email == email)).scalar()
        get_member_info = SDS_Members.query.filter_by(mis=mis).first()

        if check_member:
            history = SDS_API_History(operation="Read Specific Member Info")
            db.session.add(history)
            db.session.commit()
            return get_member_info.json()
        else:
            history = SDS_API_History(operation="Tried Reading Specific Member Info but Member Not Found")
            db.session.add(history)
            db.session.commit()
            return "Member not found", 404

    def post(self,name, mis, email):
        member = SDS_Members(name=name, mis=mis, email=email)
        history = SDS_API_History(operation="Created Member: " + str(mis))
        db.session.add(history)
        db.session.add(member)
        db.session.commit()
        
        return f"Member Created successfully \n{member.json()}"

    def delete(self,name, mis, email):
        check_member = db.session.query(db.exists().where(SDS_Members.mis == mis and SDS_Members.name == name and SDS_Members.email == email)).scalar()
        get_member_info = SDS_Members.query.filter_by(mis=mis).first()

        if check_member:
            history = SDS_API_History(operation="Deleted Member: " + str(mis))
            db.session.delete(get_member_info)
            db.session.add(history)
            db.session.commit()
            return "Member Deleted Successfully"
        else:
            history = SDS_API_History(operation="Tried Deleting Specific Member Info but Member Not Found")
            db.session.add(history)
            db.session.commit()
            return "Member not found", 404

class SDS_Project(Resource):
    def get(self, projectName, projectDesc, mis_projectHead, email_projectHead):
        check_project = db.session.query(db.exists().where(SDS_Projects.mis_projectHead == mis_projectHead and SDS_Projects.projectName == projectName and SDS_Projects.email_projectHead == email_projectHead and SDS_Projects.projectDesc == projectDesc)).scalar()
        get_project_info = SDS_Projects.query.filter_by(projectName=projectName).first()
        if check_project:
            history = SDS_API_History(operation="Read Specific Project Info")
            db.session.add(history)
            db.session.commit()
            return get_project_info.json()
        else:
            history = SDS_API_History(operation="Tried Reading Specific Project Info but Project Not Found")
            db.session.add(history)
            db.session.commit()
            return "Project not found", 404

    def post(self, projectName, projectDesc, mis_projectHead, email_projectHead):
        project = SDS_Projects(projectName=projectName, projectDesc=projectDesc, mis_projectHead=mis_projectHead, email_projectHead=email_projectHead)
        history = SDS_API_History(operation="Created Project: " + projectName)
        db.session.add(history)
        db.session.add(project)
        db.session.commit()
        
        return f"Project Created successfully \n{project.json()}"

    def delete(self, projectName, projectDesc, mis_projectHead, email_projectHead):
        check_project = db.session.query(db.exists().where(SDS_Projects.mis_projectHead == mis_projectHead and SDS_Projects.projectName == projectName and SDS_Projects.email_projectHead == email_projectHead and SDS_Projects.projectDesc == projectDesc)).scalar()
        get_project_info = SDS_Projects.query.filter_by(projectName=projectName).first()

        if check_project:
            history = SDS_API_History(operation="Deleted Project: " + projectName)
            db.session.delete(get_project_info)
            db.session.add(history)
            db.session.commit()
            return "Project Deleted Successfully"
        else:
            history = SDS_API_History(operation="Tried Deleting Specific Project Info but Project Not Found")
            db.session.add(history)
            db.session.commit()
            return "Project not found", 404

# class SDS_Alldata(Resource):
#     def get(self, type):
#         if type == "members_json":
#             members = SDS_Members.query.all()
#             for member in members:
#                 return member.json()
#             history = SDS_API_History(operation="Read All Members info")
#             db.session.add(history)
#             db.session.commit()
#         elif type == "projects_json":
#             projects = SDS_Projects.query.all()
#             for project in projects:
#                 return project.json()
#             history = SDS_API_History(operation="Read All Projects info")
#             db.session.add(history)
#             db.session.commit()

#         elif type == "alldata_json":
#             members = SDS_Members.query.all()
#             for member in members:
#                 return member.json()
#             projects = SDS_Projects.query.all()
#             for project in projects:
#                 return project.json()
#             history = SDS_API_History(operation="Read All Members and Projects info")
#             db.session.add(history)
#             db.session.commit()
            
#         else:
#             history = SDS_API_History(operation="Tried Reading Info but NOT FOUND")
#             db.session.add(history)
#             db.session.commit()
#             return "Data NOT FOUND"

class SDS_Members_Json(Resource):
    def get(self, type):
        if type == "members":
            history = SDS_API_History(operation="Read All Members Info")
            db.session.add(history)
            db.session.commit()
            members =[]
            member_all = SDS_Members.query.all()
            for member in member_all:
                member = member.json()
                members.append(member)
            # members = jsonify(members)
            # print (members)
            members = json.dumps(members)
            return f"{members}"
        elif type == "projects":
            history = SDS_API_History(operation="Read All Projects Info")
            db.session.add(history)
            db.session.commit()
            projects =[]
            project_all = SDS_Projects.query.all()
            for project in project_all:
                project = project.json()
                projects.append(project)
            # members = jsonify(members)
            # print (members)
            historys = json.dumps(projects)
            return f"{projects}"
        elif type == "historys":
            historys =[]
            history_all = SDS_API_History.query.all()
            for history in history_all:
                history = history.json()
                historys.append(history)
            # members = jsonify(members)
            # print (members)
            historys = json.dumps(historys)
            return f"{historys}"
        else:
            history = SDS_API_History(operation="Tried Reading Info But Bad Request")
            db.session.add(history)
            db.session.commit()
            return "Bad Request", 404

api.add_resource(SDS_Member, '/member_json/<string:name>/<int:mis>/<string:email>')
api.add_resource(SDS_Project, '/project_json/<string:projectName>/<string:projectDesc>/<int:mis_projectHead>/<string:email_projectHead>')
api.add_resource(SDS_Members_Json, '/<string:type>_json')

if __name__ == "__main__":
    app.run(debug=True)
