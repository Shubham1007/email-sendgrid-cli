import os
import re
from src.allto import allto
import click
import sendgrid
import six
from pyconfigstore import ConfigStore
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
                        style_from_dict)
from sendgrid.helpers.mail import *

from pyfiglet import figlet_format
try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None


conf = ConfigStore("EmailCLI")

style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})



class EmailValidator(Validator):
    pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"

    def validate(self, email):
        if len(email.text):
            if re.match(self.pattern, email.text):
                return True
            else:
                raise ValidationError(
                    message="Invalid email",
                    cursor_position=len(email.text))
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(email.text))

class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


class FilePathValidator(Validator):
    def validate(self, value):
        if len(value.text):
            if os.path.isfile(value.text):
                return True
            else:
                raise ValidationError(
                    message="File not found",
                    cursor_position=len(value.text))
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


class APIKEYValidator(Validator):
    def validate(self, value):
        if len(value.text):
            sg = sendgrid.SendGridAPIClient(
                api_key=value.text)
            try:
                response = sg.client.api_keys._(value.text).get()
                if response.status_code == 200:
                    return True
            except:
                raise ValidationError(
                    message="There is an error with the API Key!",
                    cursor_position=len(value.text))
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


def askAPIKEY():
    questions = [
        {
            'type': 'input',
            'name': 'api_key',
            'message': 'Enter SendGrid API Key (Only needed to provide once)',
            'validate': APIKEYValidator,
        },
    ]
    answers = prompt(questions, style=style)
    return answers

def askEmailInformation():
   
    questions = [
        {
            'type': 'input',
            'name': 'from_email',
            'message': 'From Email',
            'default': allto.getDefaultEmail,
            'validate': EmailValidator
        },
        {
            'type': 'input',
            'name': 'to_email',
            'message': 'To Email',
            'validate': EmailValidator
        },
        {
            'type': 'input',
            'name': 'subject',
            'message': 'Subject',
            'validate': EmptyValidator
        },
        {
            'type': 'list',
            'name': 'content_type',
            'message': 'Content Type:',
            'choices': ['Text', 'HTML'],
            'filter': lambda val: val.lower()
        },
        {
            'type': 'input',
            'name': 'content',
            'message': 'Enter plain text:',
            'when': lambda answers: getContentType(answers, "text"),
            'validate': EmptyValidator
        },
        {
            'type': 'confirm',
            'name': 'confirm_content',
            'message': 'Do you want to send an html file',
            'when': lambda answers: allto.getContentType(answers, "html")

        },
        {
            'type': 'input',
            'name': 'content',
            'message': 'Enter html:',
            'when': lambda answers: not answers.get("confirm_content", True),
            'validate': EmptyValidator
        },
        {
            'type': 'input',
            'name': 'content',
            'message': 'Enter html path:',
            'validate': FilePathValidator,
            'filter': lambda val: open(val).read(),
            'when': lambda answers: answers.get("confirm_content", False)
        },
        {
            'type': 'confirm',
            'name': 'send',
            'message': 'Do you want to send now'
        }
    ]

    answers = prompt(questions, style=style)
    return answers


@click.command()
def main():
    """
    Simple CLI for sending emails using SendGrid
    """
    allto.log("Email CLI", color="blue", figlet=True)
    allto.log("Welcome to Email CLI", "green")
    try:
        api_key = conf.get("api_key")
    except KeyError:
        api_key = askAPIKEY()
        conf.set(api_key)
    
    mailinfo = askEmailInformation()
    if mailinfo.get("send", False):
        conf.set("from_email", mailinfo.get("from_email"))
        try:
            response = allto.sendMail(mailinfo)
        except Exception as e:
            raise Exception("An error occured: %s" % (e))
        
        if response.status_code == 202:
            allto.log("Mail sent successfully", "blue")
        else:
            allto.log("An error while trying to send", "red")

if __name__ == '__main__':
    main()