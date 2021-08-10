import sendgrid
import os
from sendgrid.helpers.mail import *
from dotenv import load_dotenv, find_dotenv
import urllib
load_dotenv(find_dotenv())
heroku = False

def send_confirmation_email(to_email, name):
    global mail
    if heroku:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
    else:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email("no-reply@pausetobuy.com")
    to_email = To(to_email)

    mail = Mail(from_email, to_email)
    mail.template_id = "d-73555624504a474a9212dbea908ca603"
    mail.dynamic_template_data = { "first_name": name}
    # print(f'Mail: {mail}')
    response = sg.client.mail.send.post(request_body=mail.get())
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)


# send_confirmation_email("jobyid@me.com", "Joby")
