import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendEmail:
    def __init__(self, from_email, to_email):
        assert isinstance(from_email, str), "from_email must be a string"
        assert isinstance(to_email, list), "to_email must be a list"

        self.from_email = from_email
        self.to_email = to_email
        self.mailserver = smtplib.SMTP("smtp.office365.com", 587)
        self.mailserver.ehlo()
        self.mailserver.starttls()
        self.mailserver.ehlo()
        self.mailserver.login(self.from_email, "5tgb%TGB1qaz!QAZ1")

    def send_email(self, subject, body, attachments=None, embedded_image_paths=[]):
        assert isinstance(subject, str), "subject must be string"
        assert isinstance(body, str), "body must be string"

        msg = MIMEMultipart("related")
        msg["From"] = self.from_email
        msg["To"] = ", ".join(self.to_email)
        msg["Subject"] = subject
        body_text = body.replace("\n", "<br>")

        for a in attachments or []:
            with open(a, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())

                filename = os.path.basename(a)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)

        if len(embedded_image_paths) > 0:
            for index, embedded_image_path in enumerate(embedded_image_paths):
                msg_text = f'<br><img src="cid:image{index}"><br>'
                body_text = body_text.replace(f"IMAGE{index}", msg_text)

            msg.attach(MIMEText(body_text, "html"))

            for index, embedded_image_path in enumerate(embedded_image_paths):
                fp = open(embedded_image_path, "rb")
                msg_image = MIMEImage(fp.read())
                fp.close()

                msg_image.add_header("Content-ID", f"<image{index}>")
                msg.attach(msg_image)
        else:
            msg.attach(MIMEText(body_text, "html"))

        self.mailserver.sendmail(self.from_email, self.to_email, msg.as_string())
        print("E-mail sent to:", self.to_email)

    def quit_mailserver(self):
        self.mailserver.quit()


class Email:
    def __init__(self):
        self.from_email = "GasMarketUser@rystadenergy.com"
        self.mailserver = smtplib.SMTP("smtp.office365.com", 587)
        self.mailserver.ehlo()
        self.mailserver.starttls()
        self.mailserver.ehlo()
        self.mailserver.login(self.from_email, "5tgb%TGB1qaz!QAZ1")

    def send(self, subject, body, to_email, attachments=None):
        assert isinstance(to_email, list), "to_email must be a list"
        assert isinstance(subject, str), "subject must be string"
        assert isinstance(body, str), "body must be string"

        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = ", ".join(to_email)
        msg["Subject"] = subject
        msg.attach(MIMEText(body.replace("\n", "<br>"), "html"))

        for a in attachments or []:
            with open(a, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())

                filename = os.path.basename(a)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)

        self.mailserver.sendmail(self.from_email, to_email, msg.as_string())
        self.mailserver.quit()
        print("E-mail sent to:", to_email)


def exception(file, exception):
    if os.getenv("SEND_EMAIL") == "False":
        return
    se = SendEmail(
        from_email="GasMarketUser@rystadenergy.com",
        to_email=[
            "zongqiang.luo@rystadenergy.com",
            "martine.mulstad@rystadenergy.com",
            "jiamei.lin@rystadenergy.com",
            "jerry.chien@rystadenergy.com",
            "Akash.Sehgal@rystadenergy.com",
            "Sagar.Hegde@rystadenergy.com",
            "murilo.albuquerque@rystadenergy.com",
            "Jingya.Zhang@rystadenergy.com"
        ],
    )  # add 2 new people akash,sagar in email notif on 23nov,2023
    # add Jingya in email notif on 27 Sep, 2024
    subject = f"GasMarketUser ERROR: {file}"

    filename = str(file).split("\\")[-1]
    body = f"""Unexpected exception was raised in file <b>{filename}</b>:
    {exception}"""
    se.send_email(subject, body)
    se.quit_mailserver()


def Japan_exception(file, exception):
    se = SendEmail(
        from_email="GasMarketUser@rystadenergy.com",
        to_email=["Masanori.Odaka@rystadenergy.com"],
    )
    subject = f"GasMarketUser ERROR: {file}"

    filename = str(file).split("\\")[-1]
    body = f"""Unexpected exception was raised in file <b>{filename}</b>:
    {exception}"""
    se.send_email(subject, body)
    se.quit_mailserver()


def message(subject, body):
    se = SendEmail(
        from_email="GasMarketUser@rystadenergy.com",
        to_email=[
            "zongqiang.luo@rystadenergy.com",
            "martine.mulstad@rystadenergy.com",
            "jiamei.lin@rystadenergy.com",
        ],
    )
    se.send_email(subject, body)
    se.quit_mailserver()


def message_custom(to_email, subject, body, images=[]):
    """Allows developer to send an email for custom mail addresses. If images are added, add the `IMAGE{n}` text to where you want the images to show up in your email body, replacing {n} with an integer starting at 0."""

    se = SendEmail(
        from_email="GasMarketUser@rystadenergy.com",
        to_email=to_email,
    )
    se.send_email(subject, body, embedded_image_paths=images)
    se.quit_mailserver()


def new_benchmark(df, fundamental=None, country="Unknown", to_emails=[]):
    email_list = to_emails or [
        "zongqiang.luo@rystadenergy.com",
        "martine.mulstad@rystadenergy.com",
        "jiamei.lin@rystadenergy.com",
    ]
    se = SendEmail(from_email="GasMarketUser@rystadenergy.com", to_email=email_list)
    subject = f"{fundamental}: New BM for {country}"
    body = f"""{df.to_html(index=False)}"""
    se.send_email(subject, body)
    se.quit_mailserver()

def China_data(df, title, to_emails=[]):
    email_list = to_emails or [
        "zongqiang.luo@rystadenergy.com",
        "martine.mulstad@rystadenergy.com",
        "Jingya.Zhang@rystadenergy.com",
    ]
    se = SendEmail(from_email="GasMarketUser@rystadenergy.com", to_email=email_list)
    subject = title
    body = f"""{df.to_html(index=False)}"""
    se.send_email(subject, body)
    se.quit_mailserver()


def script_complete(body):
    se = SendEmail(
        from_email="GasMarketUser@rystadenergy.com",
        to_email=[
            "zongqiang.luo@rystadenergy.com",
            "martine.mulstad@rystadenergy.com",
            "jiamei.lin@rystadenergy.com",
            "jerry.chien@rystadenergy.com",
            "Akash.Sehgal@rystadenergy.com",
            "Sagar.Hegde@rystadenergy.com",
            "murilo.albuquerque@rystadenergy.com"
        ],
    )  # adding 2 new users akash,sagar in email sending module on nov 23,2023
    subject = "GasMarketUser Master Script Completed"
    body = (
        body
        + rf"""
    
    Full log available at: C:\Users\{os.getlogin()}\rystadenergy.com\rystadenergy.com - Gas\LNG\LNG_Cube\LNG_Short-term project\BenchmarkLogs"""
    )
    se.send_email(subject, body)
    se.quit_mailserver()

def script_complete_CN(body):
    se = SendEmail(
        from_email="GasMarketUser@rystadenergy.com",
        to_email=[
            "zongqiang.luo@rystadenergy.com",
            "martine.mulstad@rystadenergy.com",
            "Jingya.Zhang@rystadenergy.com"
        ],
    )
    subject = "GasMarketUser China Data Collection Script Completed"
    body = (
        body
        + rf"""
    
    Full log available at: C:\Users\{os.getlogin()}\rystadenergy.com\rystadenergy.com - GasLNG\ChinaGasSolution\DataCollectionLogs"""
    )
    se.send_email(subject, body)
    se.quit_mailserver()
