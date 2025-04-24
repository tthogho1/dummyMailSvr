import os
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content("This is a test email.")
msg["Subject"] = "Test Email"
msg["From"] = "sender@example.com"
msg["To"] = "recipient@example.com"

# 添付ファイルを追加
file_path = "example.txt"
with open(file_path, "rb") as f:
    msg.add_attachment(
        f.read(), maintype="application", subtype="text", filename="example.txt"
    )

with smtplib.SMTP("127.0.0.1", 25) as s:
    s.send_message(msg)
