from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.config.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME='Contacts App',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three arguments:
            -email: the user's email address, which is used as a subject for the token and also as a recipient of the message
            -username: this is used in both places where we need to display information about who we are sending this message to
            -host: This is needed so that we can create an absolute URL using FastAPI
    
    :param email: EmailStr: Make sure that the email is a valid email address
    :param username: str: Pass the username of the user to be registered
    :param host: str: Pass the host of the website to the template
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({'sub': email})
        message = MessageSchema(
            subject='Confirm your email',
            recipients=[email],
            template_body={'host': host, 'username': username, 'token': token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='email_template.html')
    except ConnectionErrors as err:
        print(err)
