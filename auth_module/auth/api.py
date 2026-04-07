"""认证 API：注册、登录、忘记密码、重置密码、获取用户"""
import json
import random
import secrets
import threading
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.database import get_db
from auth.models import User
from auth.schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from auth.security import hash_password
from auth.redis_client import get_redis
from auth.config import settings
from auth.rate_limit import protect_endpoint, record_login_failure, clear_login_failures, check_rate_limit
from auth.deps import get_current_user

router = APIRouter()


def _user_to_response(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "gender": user.gender,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "age": user.age,
        "occupation": user.occupation,
        "hometown": user.hometown,
        "current_city": user.current_city,
        "interests": user.interests,
        "is_admin": bool(user.is_admin),
        "created_at": user.created_at,
    }


def _send_reset_email(to_email: str, reset_token: str) -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        return False
    reset_url = f"{settings.SITE_URL.rstrip('/')}/#/reset-password/{reset_token}"
    html_body = f"""
    <div style="max-width:480px;margin:20px auto;font-family:-apple-system,sans-serif;background:#1e1f22;color:#f2f3f5;border-radius:12px;overflow:hidden">
        <div style="background:linear-gradient(135deg,#5865f2,#7289da);padding:24px;text-align:center">
            <h2 style="margin:0;color:#fff;font-size:20px">密码重置</h2>
        </div>
        <div style="padding:24px">
            <p style="color:#949ba4;font-size:14px;line-height:1.6">你好，</p>
            <p style="color:#949ba4;font-size:14px;line-height:1.6">我们收到了你的密码重置请求。点击下方按钮设置新密码：</p>
            <div style="text-align:center;margin:24px 0">
                <a href="{reset_url}" style="display:inline-block;background:#5865f2;color:#fff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px">重置密码</a>
            </div>
            <p style="color:#6d6f78;font-size:12px;line-height:1.5">此链接 30 分钟内有效。如果不是你本人操作，请忽略此邮件。</p>
            <p style="color:#6d6f78;font-size:12px">也可以复制链接到浏览器：<br><span style="color:#5865f2;word-break:break-all">{reset_url}</span></p>
        </div>
        <div style="padding:12px 24px;background:#16171a;text-align:center">
            <p style="color:#6d6f78;font-size:11px;margin:0">{settings.SMTP_FROM_NAME}</p>
        </div>
    </div>
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{settings.SMTP_FROM_NAME}] 密码重置"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(f"点击链接重置密码: {reset_url}", "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        if settings.SMTP_USE_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception:
        return False


def _client_ip(request: Request) -> str:
    return request.headers.get("X-Real-IP", request.client.host if request.client else "unknown")


@router.post("/register", status_code=201)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    """用户注册"""
    ip = _client_ip(request)
    protection = protect_endpoint("register", ip, behavior_token=user_data.behavior_token)
    if not protection["allowed"]:
        if protection.get("reason") == "need_verify":
            return {"need_verify": True, "challenge": protection.get("challenge"), "message": protection.get("message")}
        raise HTTPException(status_code=429, detail=protection.get("message", "操作过于频繁"))
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    avatar_url = user_data.avatar_url
    if not avatar_url:
        gender = (user_data.gender or "other").lower()
        if gender == "male":
            style = random.choice(["avataaars", "adventurer", "big-smile", "micah"])
        elif gender == "female":
            style = random.choice(["avataaars", "adventurer", "lorelei", "micah"])
        else:
            style = random.choice(["avataaars", "bottts", "shapes", "identicon"])
        seed = f"{user_data.username}_{user_data.nickname or ''}_{random.randint(1000, 9999)}"
        avatar_url = f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        gender=user_data.gender or "other",
        nickname=user_data.nickname or user_data.username,
        avatar_url=avatar_url,
        bio=user_data.bio,
        age=user_data.age,
        occupation=user_data.occupation,
        hometown=user_data.hometown,
        current_city=user_data.current_city,
        interests=json.dumps(user_data.interests or [], ensure_ascii=False),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_to_response(user)


@router.post("/login")
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    """用户登录 — 返回用户信息；若配置 JWT_SECRET 则同时返回 access_token"""
    ip = _client_ip(request)
    protection = protect_endpoint("login", ip, behavior_token=login_data.behavior_token)
    if not protection["allowed"]:
        if protection.get("reason") == "need_verify":
            return {"need_verify": True, "challenge": protection.get("challenge"), "message": protection.get("message")}
        raise HTTPException(status_code=429, detail=protection.get("message", "操作过于频繁"))
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not user.verify_password(login_data.password):
        record_login_failure(ip)
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    clear_login_failures(ip)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    out = _user_to_response(user)
    if settings.JWT_SECRET:
        try:
            from auth.security import create_access_token
            out["access_token"] = create_access_token(str(user.id))
            out["token_type"] = "bearer"
        except Exception:
            pass
    return out


@router.get("/me", response_model=UserResponse)
async def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前登录用户信息（需 JWT）"""
    return _user_to_response(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """根据 ID 获取用户公开信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _user_to_response(user)


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """忘记密码 — 发送重置邮件（需 Redis + SMTP）"""
    ip = _client_ip(request)
    allowed, _ = check_rate_limit("forgot_pwd", ip)
    if not allowed:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    r = get_redis()
    if not r:
        raise HTTPException(status_code=503, detail="服务暂时不可用，请稍后再试")

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"ok": True, "message": "如果该邮箱已注册，你将收到一封重置邮件"}

    reset_token = secrets.token_urlsafe(32)
    r.setex(f"pwd_reset:{reset_token}", 1800, str(user.id))
    threading.Thread(target=_send_reset_email, args=(data.email, reset_token), daemon=True).start()
    return {"ok": True, "message": "如果该邮箱已注册，你将收到一封重置邮件"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """重置密码 — 验证 token 并设置新密码"""
    if not data.token or not data.new_password:
        raise HTTPException(status_code=400, detail="参数不完整")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")

    r = get_redis()
    if not r:
        raise HTTPException(status_code=503, detail="服务暂时不可用")
    user_id = r.get(f"pwd_reset:{data.token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="重置链接已过期或无效，请重新申请")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    user.password_hash = User.hash_password(data.new_password)
    db.commit()
    r.delete(f"pwd_reset:{data.token}")
    return {"ok": True, "message": "密码已重置，请使用新密码登录"}


@router.get("/check-reset-token/{token}")
async def check_reset_token(token: str):
    """检查重置 token 是否有效（前端跳转前调用）"""
    r = get_redis()
    if r and r.get(f"pwd_reset:{token}"):
        return {"valid": True}
    return {"valid": False}
