
from flask import Flask, jsonify, request, make_response,render_template,redirect
from flask import *
import ibm_db
import uuid
import hashlib
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

app= Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'


def sendemail(email,password):

    sg = sendgrid.SendGridAPIClient(api_key="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")
    from_email = Email("gb170216@gmail.com")  
    to_email = To(str(email))  
    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "your username is " + email + " and password is " + password)
    mail = Mail(from_email, to_email, subject, content)

    mail_json = mail.get()

    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)

con = ibm_db.connect("DATABASE=bludb;HOSTNAME=3883e7e4-18f5-4afe-be8c-fa31c41761d2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31498;PROTOCOL=TCPIP;UID=vtj70373;PWD=6Xhbrq40pRTvm5sI;", "", "")
@app.route("/",methods=["GET"])
def main():

    return render_template("home.html")

@app.route("/register",methods=["POST"])
def register():
    name = request.form['name']
    dob = request.form['dob']
    phnum = request.form['phnum']
    email = request.form['email']
    password = request.form['pass']

    uniqid = uuid.uuid4().hex

    print(name,dob,phnum,email,password )

    sql = """INSERT INTO  "VTJ70373"."USER_DETAILS"  VALUES(?,?,?,?,?,?);"""
    stmt = ibm_db.prepare(con, sql)


    ibm_db.bind_param(stmt, 1, name)
    ibm_db.bind_param(stmt, 2, dob)
    ibm_db.bind_param(stmt, 3, email)
    ibm_db.bind_param(stmt, 4, phnum)
    ibm_db.bind_param(stmt, 5, uniqid)
    ibm_db.bind_param(stmt, 6, password)
    ibm_db.execute(stmt)

    sendemail(email,password)

    return render_template("register.html")

@app.route("/register",methods=["GET"])
def register_get():

    return render_template("register.html")


@app.route("/dashboard",methods=["get"])
def dashboard():
    
    hosp = request.args.get("hosp")
    loc = request.args.get("loc")
    bg = request.args.get("bg")

    

    uid = str(session.get("uniqid")+'')
    sql = f"""select * from "VTJ70373"."REQUEST" Where "UNIQID"!='{uid}' AND "status"='waiting'"""

    if(hosp != "" and hosp != None):
        sql += f""" AND "HOSP" ='{hosp}'"""
    if(loc != "" and loc != None):
        sql += f""" AND "LOC" ='{loc}' """
    if(bg != "" and bg !=None):
        sql += f""" AND "BG" ='{bg}' """

    sql += ";"



    arr = []
    larr = []
    barr = []
    harr = []

    
    sql2 = f"""select distinct loc from "VTJ70373"."REQUEST" Where "UNIQID"!='{uid}' AND "status"='waiting';"""
    sql3 = f"""select distinct hosp from "VTJ70373"."REQUEST" Where "UNIQID"!='{uid}' AND "status"='waiting';"""
    sql4 = f"""select distinct bg from "VTJ70373"."REQUEST" Where "UNIQID"!='{uid}' AND "status"='waiting';"""
    
    stmt = ibm_db.exec_immediate(con, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    while tuple != False:
        arr.append(tuple)
        tuple = ibm_db.fetch_tuple(stmt)
    
    stmt = ibm_db.exec_immediate(con, sql2)
    tuple = ibm_db.fetch_tuple(stmt)
    while tuple != False:
        larr.append(tuple)
        tuple = ibm_db.fetch_tuple(stmt)
    
    
    stmt = ibm_db.exec_immediate(con, sql3)
    tuple = ibm_db.fetch_tuple(stmt)
    while tuple != False:
        harr.append(tuple)
        tuple = ibm_db.fetch_tuple(stmt)
    
    
    stmt = ibm_db.exec_immediate(con, sql4)
    tuple = ibm_db.fetch_tuple(stmt)
    while tuple != False:
        barr.append(tuple)
        tuple = ibm_db.fetch_tuple(stmt)

    print("arr")
    print(arr)
    print(larr)
    print(harr)
    print(barr)
    return render_template("dashboard.html",requestarray=arr,locarr=larr,bgarr=barr,hosarr=harr)

@app.route("/changestatus/<id>",methods=["get"])
def chngstatus(id):

    print(id)
    uid = str(session.get("uniqid"))+""
    name = str(session.get("name"))+""
    sql = f"""UPDATE "VTJ70373"."REQUEST" SET "donorid" = '{uid}', "donorname" = '{name}',"status"='accepted' WHERE "FUNIQID" = '{id}';"""
    stmt = ibm_db.prepare(con, sql)
    ibm_db.execute(stmt)
    print("suc")

    return "success"


@app.route("/requestform",methods=["get"])
def reqform_get():
    return render_template("form.html")

@app.route("/requestform",methods=["post"])
def reqform_post():
    name = request.form['name']
    bg = request.form['bg']
    loc = request.form['loc']
    hosp = request.form['hosp']

    formid = (hashlib.sha1((uuid.uuid4().hex + session.get("uniqid")).encode())).hexdigest() + ""
    print(formid)
    uid = str(session.get("uniqid")) + ""
    
    sql = f"""INSERT INTO  "VTJ70373"."REQUEST" ("UNIQID","FUNIQID","NAME","BG","LOC","HOSP","status") VALUES('{uid}','{formid}','{name}','{bg}','{loc}','{hosp}','waiting');"""

    stmt = ibm_db.prepare(con, sql)
    ibm_db.execute(stmt)

    return redirect("/dashboard")


@app.route("/login",methods=["POST"])
def login():
    print(con)

    username = request.form['username']
    password = request.form['password']

    sql = """SELECT * FROM "VTJ70373"."USER_DETAILS" where email = '{usr}' AND passw = '{pas}';""".format(usr=username,pas=password)

    stmt = ibm_db.exec_immediate(con, sql)
    user = ""
    while ibm_db.fetch_row(stmt) != False:
        user = ibm_db.result(stmt, 2)

    name = ""
    if(user == username):

        sql1 = """SELECT * FROM "VTJ70373"."USER_DETAILS" where email = '{usr}';""".format(usr=username)
        stmt1 = ibm_db.exec_immediate(con, sql1)
        uniqid = ""
        while ibm_db.fetch_row(stmt1) != False:
            uniqid = ibm_db.result(stmt1, 4)
            name = ibm_db.result(stmt1, 0)
        print(name)
        session['username'] = username
        session['name'] = name
        session['uniqid'] = uniqid

        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/login",methods=["GET"])
def login_get():

    print(con)
    return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)