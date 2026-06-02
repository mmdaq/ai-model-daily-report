import os

import requests

from config import REQUEST_TIMEOUT


def get_http_session() -> requests.Session:
    """
    默认不使用系统代理，避免本机 127.0.0.1:7890 等失效代理导致采集为空。
    需要代理时在 .env 设置 USE_PROXY=1
    """
    session = requests.Session()
    if os.getenv("USE_PROXY", "0") != "1":
        session.trust_env = False
    return session


def http_get(url: str, **kwargs) -> requests.Response:
    session = get_http_session()
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    return session.get(url, **kwargs)


def http_put(url: str, **kwargs) -> requests.Response:
    session = get_http_session()
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    return session.put(url, **kwargs)
