import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import QQ_EMAIL, QQ_SMTP_AUTH_CODE, RECEIVER_EMAIL

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465


def send_html_email(subject: str, html_body: str) -> None:
    if not QQ_EMAIL or not QQ_SMTP_AUTH_CODE:
        raise ValueError("请在 .env 中配置 QQ_EMAIL 和 QQ_SMTP_AUTH_CODE")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = QQ_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(QQ_EMAIL, QQ_SMTP_AUTH_CODE)
        server.sendmail(QQ_EMAIL, [RECEIVER_EMAIL], msg.as_string())

    logger.info("Email sent to %s: %s", RECEIVER_EMAIL, subject)


def send_html_email_if_configured(subject: str, html_body: str) -> bool:
    """配置了邮箱则发送，未配置则跳过。返回是否已发送。"""
    if not QQ_EMAIL or not QQ_SMTP_AUTH_CODE:
        logger.info("邮箱未配置，跳过邮件发送")
        return False
    send_html_email(subject, html_body)
    return True
