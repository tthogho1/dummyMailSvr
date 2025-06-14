import email
import time
from email.header import decode_header
from email.utils import parseaddr
from .sharedSignals import email_signals
from .sharedSignals import EmailMessage
from .sharedSignals import received_emails


# 受信したメールを保存するグローバルリスト
class Handler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        print("Received message from:", envelope.mail_from)
        print("Message for:", envelope.rcpt_tos)

        msg = email.message_from_bytes(envelope.content)

        # Subject processing
        subject = msg["subject"]
        subject_text = ""
        if subject:
            decoded_subject = decode_header(subject)
            subject_text = "".join(
                [
                    (
                        part.decode(encoding or "ascii", errors="replace")
                        if isinstance(part, bytes)
                        else part
                    )
                    for part, encoding in decoded_subject
                ]
            )
            print(f"Subject: {subject_text}")

        # Sender processing
        sender = msg["from"]
        sender_text = ""
        sender_email = ""
        if sender:
            sender_name, sender_email = parseaddr(sender)
            decoded_sender = decode_header(sender_name)
            sender_text = "".join(
                [
                    (
                        part.decode(encoding or "ascii", errors="replace")
                        if isinstance(part, bytes)
                        else part
                    )
                    for part, encoding in decoded_sender
                ]
            )
            print(f"From: {sender_text} <{sender_email}>")

        # Body and attachment processing
        content = ""
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "iso-2022-jp"
                    try:
                        decoded_text = payload.decode(charset, errors="replace")
                        content += f"Content ({content_type}):\n"
                        content += decoded_text + "\n"
                    except Exception as e:
                        content += f"Error decoding {content_type}: {e}\n"
                elif part.get("Content-Disposition") and "attachment" in part.get(
                    "Content-Disposition"
                ):
                    filename = part.get_filename()
                    payload = part.get_payload(decode=True)
                    if filename and payload:
                        attachments.append((filename, payload))
        else:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "iso-2022-jp"
            try:
                decoded_text = payload.decode(charset, errors="replace")
                content += "Content:\n"
                content += decoded_text
            except Exception as e:
                content += f"Error decoding content: {e}\n"

        # Create and emit an email message
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        email_message = EmailMessage(
            f"{sender_text} <{sender_email}>" if sender_text else sender_email,
            envelope.rcpt_tos,
            subject_text,
            content,
            timestamp,
            # envelope.content.decode('utf-8', errors='replace'),
            attachments,  # Include attachments
        )
        # email_message[attachments] = attachments

        received_emails.append(email_message)
        email_signals.new_email.emit(email_message)

        print(content)
        print("End of message")
        return "250 Message accepted for delivery"
