from PyQt5.QtCore import QObject, pyqtSignal

class EmailMessage:
    def __init__(self, sender, recipients, subject, content, timestamp, raw_message):
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.content = content
        self.timestamp = timestamp
        self.raw_message = raw_message

class EmailSignals(QObject):
    new_email = pyqtSignal(EmailMessage)
    
email_signals = EmailSignals()

# 受信したメールを保存するグローバルリスト
received_emails = []