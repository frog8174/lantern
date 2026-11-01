"""OIDC（Keycloak）登入流程：不連真的 Keycloak，用假的 oauth 物件模擬 callback（docs/auth.md）。"""
from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend import config, db, main
from backend.main import app


class FakeKC:
    def __init__(self, token=None, error=None):
        self.token, self.error = token, error

    async def authorize_access_token(self, request):
        if self.error:
            raise main.OAuthError(error=self.error)
        return self.token

    async def load_server_metadata(self):
        return {"end_session_endpoint": "https://kc.test/realms/r/protocol/openid-connect/logout"}


def _oidc(monkeypatch, kc):
    monkeypatch.setattr(config, "AUTH_MODE", "oidc")
    monkeypatch.setattr(config, "OIDC_CLIENT_ID", "lantern-local")
    monkeypatch.setattr(main, "oauth", SimpleNamespace(kc=kc))


def test_livez_and_config(client):
    assert client.get("/api/livez").json() == {"ok": True}
    assert client.get("/api/auth/config").json() == {"mode": "dev", "version": config.VERSION}


def test_oidc_login_creates_user_and_session(monkeypatch):
    token = {"id_token": "idt", "userinfo": {"sub": "kc-sub-123", "name": "陳同學", "email": "a@b.tw"}}
    _oidc(monkeypatch, FakeKC(token))
    with TestClient(app) as c:
        assert c.get("/api/me").status_code == 401                      # 還沒登入
        c.cookies.set("uid", "alice")                                   # dev 的未簽章 cookie 在 oidc 模式無效
        assert c.get("/api/me").status_code == 401
        r = c.get("/api/auth/callback?code=x&state=y", follow_redirects=False)
        assert r.status_code == 302 and r.headers["location"] == "/"
        assert c.get("/api/me").json() == {"id": "kc-sub-123", "name": "陳同學"}
        assert c.get("/api/papers").json() == []                        # 新使用者：空的論文庫
        assert c.get("/api/auth/users").status_code == 404              # 測試名片清單只在 dev
        out = c.post("/api/auth/logout").json()
        assert out["logout_url"].startswith("https://kc.test/") and "id_token_hint=idt" in out["logout_url"]
        assert c.get("/api/me").status_code == 401                      # session 已清掉
    with db.conn() as conn:
        assert conn.execute("SELECT email FROM users WHERE id='kc-sub-123'").fetchone()["email"] == "a@b.tw"


def test_oidc_login_failure_redirects(monkeypatch):
    _oidc(monkeypatch, FakeKC(error="access_denied"))
    with TestClient(app) as c:
        r = c.get("/api/auth/callback?error=access_denied", follow_redirects=False)
        assert r.status_code == 302 and "login_error" in r.headers["location"]
        assert c.get("/api/me").status_code == 401
