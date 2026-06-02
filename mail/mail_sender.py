import logging
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 优先从环境变量读取，如果没有再从 config 读取（兼容本地）
try:
    from config import QQ_EMAIL as CONFIG_QQ_EMAIL
    from config import QQ_SMTP_AUTH_CODE as CONFIG_QQ_SMTP_AUTH_CODE
    from config import RECEIVER_EMAIL as CONFIG_RECEIVER_EMAIL
except ImportError:
    CONFIG_QQ_EMAIL = None
    CONFIG_QQ_SMTP_AUTH_CODE = None
    CONFIG_RECEIVER_EMAIL = None

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465

def _get_email_config():
    """获取邮件配置，优先使用环境变量，其次使用 config"""
    qq_email = os.getenv("QQ_EMAIL") or os.getenv("EMAIL_USER") or CONFIG_QQ_EMAIL
    qq_auth = os.getenv("QQ_SMTP_AUTH_CODE") or os.getenv("EMAIL_PASSWORD") or CONFIG_QQ_SMTP_AUTH_CODE
    receiver = os.getenv("EMAIL_RECEIVER") or os.getenv("RECEIVER_EMAIL") or CONFIG_RECEIVER_EMAIL or qq_email
    
    return qq_email, qq_auth, receiver

def send_html_email(subject: str, html_body: str) -> None:
    qq_email, qq_auth, receiver = _get_email_config()
    
    if not qq_email or not qq_auth:
        raise ValueError("请配置 QQ_EMAIL 和 QQ_SMTP_AUTH_CODE 环境变量，或在 .env 文件中配置")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = qq_email
    msg["To"] = receiver
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(qq_email, qq_auth)
        server.sendmail(qq_email, [receiver], msg.as_string())

    logger.info("Email sent to %s: %s", receiver, subject)

def send_html_email_if_configured(subject: str, html_body: str) -> bool:
    """如果配置了邮件，则发送，否则跳过"""
    qq_email, qq_auth, _ = _get_email_config()
    
    if not qq_email or not qq_auth:
        logger.info("邮件未配置，跳过发送")
        return False
    
    send_html_email(subject, html_body)
    return True