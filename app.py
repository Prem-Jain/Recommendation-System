from flask import Flask, render_template, request, url_for, redirect
from pdfminer.high_level import extract_text
import sqlite3
import pandas as pd

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'RECSYS801')


def pdf(resume):
    page = extract_text(resume)
    return page

class setSkills():
    def __init__(self, skills):
        self.skills = skills

his_skill = setSkills(0)

def extract(page):
    subject = ['python', 'java', 'c', 'c++', 'html', 'php', 'machine learning', 'artificial intelligence', 'deep learning', 'data science','javascript', 'github', 'msoffice', 'node js', 'react', 
            'flask','django','sql', 'database', 'iot']
    page = page.lower()
    skills=[]
    for i in subject:
        if i in page:
            skills.append(i)
    his_skill.skills = skills

def sql(name, email, phno, resume):
    try:
        con = sqlite3.connect("RecommendSystem.db")
        c = con.cursor()
        x = (name, email, phno, resume)
        insert = """INSERT INTO Resumes (Name, Email, PhoneNumber, Resume) VALUES (?,?,?,?);"""
        c.execute(insert, x)
    finally:    
        con.commit()
        c.close()
        con.close()
        
class setMarks():
    def __init__(self):
        self.marks = {'python' : 90, "c" : 90, "java" : 90}

class setExam():
    def __init__(self):
        self.train_skills = {}
        self.pass_skills = []
    def appendSkills(self, train, pass_skill):
        self.train_skills = train
        self.pass_skills = pass_skill
exam = setExam()

def courses():
    train_courses = pd.read_csv("Requirments/Trainers.csv")
    pass_skill = []
    train = dict()
    courses = []
    his_marks = setMarks()
    for skill, mark in his_marks.marks.items():
        for i in range(train_courses.shape[0]):
            if(train_courses.iloc[i][0] == skill):
                if(train_courses.iloc[i][1] <= mark <= train_courses.iloc[i][2]):
                    if(pd.isnull(train_courses.iloc[i][3])):
                        pass_skill.append(skill)
                        continue
                    courses.append(train_courses.iloc[i][3])
                    for j in range(4, train_courses.shape[1], 3):
                        if(pd.isnull(train_courses.iloc[i][j])):
                            continue
                        train[train_courses.iloc[i][j], train_courses.iloc[i][j + 1], train_courses.iloc[i][j + 2]] = train_courses.iloc[i][3]
    exam.appendSkills(train, pass_skill)

class JobClass():
    def __init__(self):
        self.jobDict = {}
    
    def appendJobDict(self, jobDict):
        self.jobDict = jobDict

com_pos = JobClass()

def recom_job():
    file = pd.read_csv("Requirments/Recruiters.csv")
    skills = file['Skills_required']
    set_skills = []
    job = {}
    for index in skills:
        set_skills.append(index.split(','))
    for i in range(len(set_skills)):
        count=0
        for j in set_skills[i]:
            for k in exam.pass_skills:
                if(j == k):
                    count+=1
        if(count==len(set_skills[i])):
            job[file.iloc[i][0]] = file.iloc[i][1]
    com_pos.appendJobDict(job)
    
@app.route('/', methods = ["POST", "GET"])
def form():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phno = request.form['phoneNumber']
        resume = request.files['resume']
        page = pdf(resume)
        extract(page)
        sql(name, email, phno, resume.read())
        return redirect(url_for('skills'))
    return render_template('Home.html')

@app.route('/skills', methods = ["POST", "GET"])
def skills():
    if request.method == "POST":
        courses()
        if len(exam.train_skills) == 0:
            return redirect(url_for('job'))
        else:
            return redirect(url_for('train'))
    return render_template('TakeTest.html', skills = his_skill.skills)

@app.route('/train', methods = ["POST", "GET"])
def train():
    if len(exam.pass_skills) == 0:
        return render_template('AllFail.html', train_skills = exam.train_skills)
    else:
        return render_template('Train.html', train_skills = exam.train_skills, pass_skills = exam.pass_skills)

@app.route('/job', methods = ["POST", "GET"])
def job():
    recom_job()
    return render_template('Job.html', jobDict = com_pos.jobDict)
    
if __name__ == "__main__":
    app.run(debug=True)