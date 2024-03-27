import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
import csv
import pdb
import json
from collections import OrderedDict
from python_http_client.exceptions import HTTPError

emails_file = "people_12_months.csv" # ../people_12_months.csv

SENDGRID_API_KEY='YOUR API KEY HERE'

def emailsToProjectDict():
    emailDict = OrderedDict()
    nameDict = OrderedDict()
    '''reading Store Apps '''

    with open(emails_file, mode= "r") as storeAppsCSV: 
        fieldnames = ["name", "email","repo"]
        csvReader = csv.DictReader(storeAppsCSV,fieldnames)
        next(csvReader,None)
        for row in csvReader:
            email = row["email"]
            project = row["repo"]
            name = row["name"]
            if email != "" and "@" in email and "[" not in email and project != "":
                if email not in emailDict:
                    emailDict[email] = project
                    nameDict[email] = name
                else:
                    print("Email: %s - project: %s "%(email,project))
                    
    return [emailDict, nameDict]

def emailDictToToList(emailDict, nameDict):
    emailsList = []
    for email in emailDict:
        toEmail = To(email=email,substitutions={'[-project-]': emailDict[email], '[-name-]': nameDict[email]})
        emailsList.append(toEmail)
    return emailsList


def mailSender(emailsList):
    message = Mail(
        from_email='YOUR EMAIL HERE',
        to_emails=emailsList,
        subject="[ROS] Invitation to research survey on architecting ROS-based systems" ,
        html_content="<pre style=\"font-family: sans-serif;\" >Hi [-name-], <br /><br />I am a researcher at Chalmers University of Technology and we are doing a study on the architecture of ROS-based systems.<br />I am contacting you because you appear as one of the contributors of this GitHub repo: <a href='https://www.github.com/[-project-]'>https://www.github.com/[-project-]</a><br /><br />Do you have some spare time for filling out the short survey linked below?<br /><br />The on-line survey is available here: <a href='-- https://goo.gl/forms/xLhtaFIcCzZEwHSG3 SURVEY LINK HERE --'>https://goo.gl/forms/xLhtaFIcCzZEwHSG3</a><br /><br />Filling the survey will take no more than 10-15 minutes to complete. We are aiming at building a set of guidelines for testing and QA in ROS-based systems. I hope you will find our work useful.<br /><br />Thanks in advance for your help!<br /><br />   Ivano<br /><br />:::<br />Ivano Malavolta | Assistant professor | Vrije Universiteit Amsterdam, The Netherlands | <a href='http://www.ivanomalavolta.com'>http://www.ivanomalavolta.com</a><br />   </pre>",
        is_multiple=True)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except HTTPError as e:
        print(e.to_dict)

emailToProjectDict = emailsToProjectDict()[0]
nameToProjectDict = emailsToProjectDict()[1]
emailsList = emailDictToToList(emailToProjectDict, nameToProjectDict)

i = 0
while i < len(emailsList):
    mailSender(emailsList[i:1000+i])
    i += 1000
    

        
        