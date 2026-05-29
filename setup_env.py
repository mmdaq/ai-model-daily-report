"""交互式配置 .env 文件（首次使用运行一次即可）"""
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"
EXAMPLE = """QQ_EMAIL={qq_email}
QQ_SMTP_AUTH_CODE={auth_code}
RECEIVER_EMAIL={receiver}
GITHUB_TOKEN={github_token}
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
"""


def main():
    print("=" * 50)
    print("  AI 模型日报 - 邮箱配置向导")
    print("=" * 50)
    print()
    print("请提前在 QQ 邮箱开启 SMTP 并获取授权码：")
    print("  QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP → 开启")
    print()

    qq_email = input("发送邮箱（QQ邮箱）: ").strip()
    auth_code = input("SMTP 授权码（不是QQ密码）: ").strip()
    receiver = input("接收邮箱（直接回车=发给自己）: ").strip() or qq_email
    github_token = input("GitHub Token（可选，直接回车跳过）: ").strip()

    if not qq_email or not auth_code:
        print("\n错误：发送邮箱和授权码不能为空！")
        return

    content = EXAMPLE.format(
        qq_email=qq_email,
        auth_code=auth_code,
        receiver=receiver,
        github_token=github_token,
    )
    ENV_PATH.write_text(content, encoding="utf-8")
    print(f"\n配置已保存到: {ENV_PATH}")
    print("下一步：双击「发送日报.bat」测试发送")


if __name__ == "__main__":
    main()
