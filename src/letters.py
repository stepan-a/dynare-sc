import csv
import jinja2
import os
from jinja2 import Template
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formatdate
import yaml

def printstudentlist(database):
    with open(database, newline='') as csvfile:
        tmp = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in tmp:
            print(', '.join(row))

def lastname(student):
    return student["LASTNAME"].replace(' ', '-')

def setbasefilename(student, type):
    return lastname(student)+'-'+type

def setfilename(basefilename, ext):
    return basefilename+'.'+ext

# Set-up templating system for LaTeX files.
latex_jinja_env = jinja2.Environment(
    block_start_string = '@{',
    block_end_string = '}@',
    variable_start_string = ':{',
    variable_end_string = '}:',
    comment_start_string = '\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('/')))

def writeletters(database, t1, *t2):
    # Select template.
    if not t2:
        template = latex_jinja_env.get_template(os.path.realpath('templates/'+t1+'-letter.tex'))
    else:
        template = latex_jinja_env.get_template(os.path.realpath('templates/'+t1+'-'+t2[0]+'-letter.tex'))
    # Write letter (pdf)
    with open(database, newline='', encoding='utf-8') as csvfile:
        tmp = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in tmp:
            student = {}
            student["FIRSTNAME"] = row[0]
            student["LASTNAME"] = row[1]
            student["EMAIL"] = row[2]
            renderer_template = template.render(**student)
            basefilename = setbasefilename(student, t1)
            with open('build/'+setfilename(basefilename, 'tex'), "w") as f:
                f.write(renderer_template)
            os.chdir('./build')
            os.system('pdflatex ' + basefilename)
            for ext in ['tex', 'aux', 'log', 'out']:
                os.remove(setfilename(basefilename, ext))
            os.chdir('../')

def attendance(student):
    msg = """Dear %s,

Please find enclosed an attendance certificate in case you need it.

I hope you enjoyed your stay in Paris and the summer school.

Best,
Stéphane.

--
Stéphane Adjemian
In charge of the Dynare project""" % (student["FIRSTNAME"])
    return msg

def acceptance(student):
    msg = """Dear %s,

I am pleased to inform you that you have been accepted in the next Dynare Summer School. A formal invitation is enclosed to this email (with the dates, location and the fee that will be charged to you). We will contact you very soon to inform you of the week's agenda and for payment formalities.

I hope you will enjoy your stay in Paris and the summer school.

Best,
Stéphane.

--
Stéphane Adjemian
In charge of the Dynare project""" % (student["FIRSTNAME"])
    return msg

def reject(student):
    msg = """Dear %s,

I am sorry to inform you that your application has not been accepted.
Due to the limited number of places we had to reject potentially
interesting applications (around 25 percent).

We wish you all the best for your research.

On behalf of the Dynare team,
Stéphane Adjemian

--
Stéphane Adjemian
In charge of the Dynare project""" % (student["FIRSTNAME"])
    return msg


def sendemail(student, message, enclosedfile, FromEmail, ServerName, UserLogin, UserPassword):
    msg = MIMEMultipart()
    msg['From'] = FromEmail
    msg['To'] = student["EMAIL"]
    msg['Cc'] = 'school@dynare.org'
    msg['Subject'] = "Dynare Summer School"
    msg['Date'] = formatdate(localtime=True)
    body =  message(student)
    msg.attach(MIMEText(body, 'plain','utf-8'))
    if enclosedfile!='':
        attachment = open("build/"+enclosedfile, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % enclosedfile)
        msg.attach(part)
    server = smtplib.SMTP(ServerName, 587)
    server.starttls()
    server.login(UserLogin, UserPassword)
    text = msg.as_string()
    server.sendmail(FromEmail, [student["EMAIL"], ' school@dynare.org'], text)
    server.quit()

def sendallemails(database, t1, *t2):
    # Select template if needed
    if t1!='reject':
        if not t2:
            template = latex_jinja_env.get_template(os.path.realpath('templates/'+t1+'-letter.tex'))
        else:
            template = latex_jinja_env.get_template(os.path.realpath('templates/'+t1+'-'+t2[0]+'-letter.tex'))
    # Read database line by line, write and send emails
    with open(database, newline='', encoding='utf-8') as csvfile:
        tmp = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in tmp:
            student = {}
            student["FIRSTNAME"] = row[0]
            student["LASTNAME"] = row[1]
            student["EMAIL"] = row[2]
            if t1!='reject':
                renderer_template = template.render(**student)
                basefilename = setbasefilename(student, t1)
                with open('build/'+setfilename(basefilename, 'tex'), "w") as f:
                    f.write(renderer_template)
                os.chdir('./build')
                os.system('pdflatex ' + basefilename)
                for ext in ['tex', 'aux', 'log', 'out']:
                    os.remove(setfilename(basefilename, ext))
                os.chdir('../')
                sendemail(student, eval(t1), setfilename(basefilename, 'pdf'), UserEmail, ServerName, UserLogin, UserPassword)
            else:
                sendemail(student, eval(t1), '', UserEmail, ServerName, UserLogin, UserPassword)

# Read configuration file
with open("configuration.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

ServerName = config['ServerName']
UserEmail = config['UserEmail']
UserLogin = config['UserLogin']
UserPassword = config['UserPassword']
