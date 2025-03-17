import asyncio
import email
from email.header import decode_header
from email.utils import parseaddr
from aiosmtpd.controller import Controller

class Handler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        print('Received message from:', envelope.mail_from)
        print('Message for:', envelope.rcpt_tos)
        print('Message data:')
        
        msg = email.message_from_bytes(envelope.content)
        
        subject = msg['subject']
        if subject:
            decoded_subject = decode_header(subject)
            subject_text = ''.join([
                part.decode(encoding or 'ascii', errors='replace') if isinstance(part, bytes) else part
                for part, encoding in decoded_subject
            ])
            print(f"Subject: {subject_text}")

        # Decode sender
        sender = msg['from']
        if sender:
            sender_name, sender_email = parseaddr(sender)
            decoded_sender = decode_header(sender_name)
            sender_text = ''.join([
                part.decode(encoding or 'ascii', errors='replace') if isinstance(part, bytes) else part
                for part, encoding in decoded_sender
            ])
            print(f"From: {sender_text} <{sender_email}>")

        # Decode body
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'iso-2022-jp'
                    try:
                        decoded_text = payload.decode(charset, errors='replace')
                        print(f"Content ({content_type}):")
                        print(decoded_text)
                    except Exception as e:
                        print(f"Error decoding {content_type}: {e}")
        else:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'iso-2022-jp'
            try:
                decoded_text = payload.decode(charset, errors='replace')
                print("Content:")
                print(decoded_text)
            except Exception as e:
                print(f"Error decoding content: {e}")

        print('End of message')
        return '250 Message accepted for delivery'

if __name__ == '__main__':
    handler = Handler()
    controller = Controller(handler, hostname='127.0.0.1', port=25)
    controller.start()
    print(f"Mail server started on 127.0.0.1:25")
    
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
