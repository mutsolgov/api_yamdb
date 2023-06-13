import uuid

from django.core.mail import send_mail

from api_yamdb.settings import EMAIL


def generate_confirmation_code():
    code = str(uuid.uuid4().int)[:6]
    return code


def send_confirmation_email(email, confirmation_code):
    """Отправление сообщения с кодом на почту пользователю."""
    subject = 'Confirmation Code'
    message = f'Your confirmation code is: {confirmation_code}'
    from_email = EMAIL
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)
