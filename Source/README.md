## Data I/O

If you want to send out mails on the basis of 
the generated csv table you have to add the following
environment variables to `secrets.py`:

```python

SMTP_SERVER = "..."
SMTP_PORT = 0  # Integer

OUTLOOK_CREDENTIALS_USER = "..."
OUTLOOK_CREDENTIALS_PASS = "..."
OUTLOOK_FROM_EMAIL = "..."

OUTLOOK_REPLY_TO_ADDRESS = "..."  # Optional

```