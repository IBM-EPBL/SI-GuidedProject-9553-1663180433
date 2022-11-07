
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
    from_email = Email("gb170216@gmail.com")  # Change to your verified sender
    to_email = To(str(email))  # Change to your recipient
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

    # Explicitly bind parameters
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



if __name__=="__main__":
    app.run(debug=True)