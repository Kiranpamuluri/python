import smtplib
import getpass

host_name = "smtp.gmail.com"
port = 465

sender = 'sandeep23@aaa.ca'
receiver = 'devops_global@aaa.ca'

password = getpass.getpass()
msg = """\
Subject: Test Mail
Hello from Sender !!"""

s = smtplib.SMTP_SSL(host_name, port)
s.login(sender, password)
s.sendmail(sender, receiver, msg)
s.quit()

print("Test mail")