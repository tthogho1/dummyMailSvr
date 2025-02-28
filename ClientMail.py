import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content('This is a test email.')
msg['Subject'] = 'Test Email'
msg['From'] = 'sender@example.com'
msg['To'] = 'recipient@example.com'

with smtplib.SMTP('127.0.0.1', 25) as s:
    s.send_message(msg)
