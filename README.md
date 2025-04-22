# Dummy Mail GUI

A graphical SMTP server application for testing email sending in a local environment without actually sending emails to real recipients.

## Overview

Dummy Mail GUI is a PyQt5-based application that provides a local SMTP server with a graphical user interface. It's designed for developers who need to test email functionality in their applications without sending actual emails. The application captures all outgoing emails and displays them in a user-friendly interface, allowing you to verify that your application is sending emails correctly.

## Features

- Graphical user interface for easy monitoring of test emails
- Runs a local SMTP server on 127.0.0.1:25
- Captures all outgoing emails
- Displays email details in a structured format:
  - Sender information
  - Recipient information
  - Subject line (with proper decoding of various character sets)
  - Email body content (both plain text and HTML)
- Handles multipart messages
- Supports various character encodings including ISO-2022-JP
- View raw email messages
- Real-time email reception and display

## Screenshots

(Screenshots would be placed here)

## Requirements

- Python 3.6 or higher
- PyQt5
- aiosmtpd package

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/tthogho1/dummyMailSvr.git
   cd dummyMailSvr
   ```

2. Install the required dependencies:
   ```
   pip install PyQt5 aiosmtpd
   ``` 

## Usage

### Starting the Application

Run the following command to start the application:

```
python src/dummyMailGUI.py
```

### Using the Application

1. Click the "サーバー開始" (Start Server) button to start the SMTP server
2. The server will start listening on 127.0.0.1:25
3. Configure your application to use this SMTP server (see below)
4. Send test emails from your application
5. Received emails will appear in the left panel
6. Click on an email to view its details in the right panel
7. Click "Raw メッセージを表示" (Show Raw Message) to see the raw email content
8. Click "サーバー停止" (Stop Server) when you're done

### Configuring Your Application

Configure your application to use the following SMTP settings:

- SMTP Server: 127.0.0.1
- Port: 25
- Authentication: None required
- TLS/SSL: Not required

### Example: Sending a Test Email with Python

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create a multipart message
msg = MIMEMultipart()
msg['From'] = 'sender@example.com'
msg['To'] = 'recipient@example.com'
msg['Subject'] = 'Test Email'

# Add body text
text = "Hello, this is a test email sent to the dummy mail server."
msg.attach(MIMEText(text, 'plain'))

# Add HTML content
html = """
<html>
  <body>
    <h1>Test Email</h1>
    <p>This is a <b>test email</b> sent to the dummy mail server.</p>
  </body>
</html>
"""
msg.attach(MIMEText(html, 'html'))

# Connect to the server and send the email
try:
    server = smtplib.SMTP('127.0.0.1', 25)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
```

## Project Structure

```
src/
├── dummyMailGUI.py       # Main application file with GUI implementation
├── handler/
│   ├── Handler.py        # SMTP server handler for processing emails
│   ├── sharedSignals.py  # Signal definitions for communication between components
│   
```

## Troubleshooting

### Port 25 Already in Use

If you see an error like "Address already in use", it means that port 25 is already being used by another application. You can:

1. Stop the other application using port 25
2. Modify the code in `dummyMailGUI.py` to use a different port:
   ```python
   self.server_controller = Controller(handler, hostname='127.0.0.1', port=2525)  # Change to a different port
   ```
   Remember to update your application's SMTP configuration to use the new port.

### Permission Issues

On some systems, binding to ports below 1024 (like port 25) requires administrative privileges. If you encounter permission issues:

1. Run the script with administrative privileges, or
2. Modify the code to use a port above 1024 (e.g., 2525)

### PyQt5 Installation Issues

If you encounter issues installing PyQt5, you may need to install additional system dependencies. Refer to the PyQt5 documentation for your specific operating system.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
