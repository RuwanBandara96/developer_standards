# ==============================================================================
#  DEVELOPER STANDARDS & DEVELOPMENT WORKFLOW — INTERACTIVE EXAM EDITION
#  Login + Graded Exam (multi-set, random pool) + Submission Storage + Admin Console
# ------------------------------------------------------------------------------
#  Run with:   streamlit run developer.py
#  Requires:   streamlit, pandas, numpy, plotly
#
#  Credentials are NOT stored in this file. They live in .streamlit/secrets.toml
#  Question pool is stored in questions_pool.py (and overridden by exam_bank.json).
#
#  Sessions survive browser refresh via a signed token in the URL
#  (?session=...). Set [session] secret in secrets.toml for production.
# ==============================================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
import os
import json
import time
import random
import hmac
import hashlib
import base64
import html as html_lib
from datetime import datetime
from posts import init_posts_state, s_posts_hub, s_posts_management
from questions_pool import QUESTION_POOL

# ------------------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Developer Standards — Exam",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# GLOBAL STYLE
# ------------------------------------------------------------------------------
st.markdown(
    """
<style>
:root{
  --navy:#0B3C5D; --teal:#1D7874; --gold:#D9A441; --red:#C0392B; --green:#1E8449;
  --ink:#2B3A4A; --muted:#5A7184; --line:#E1E8EE; --bg:#F7FAFC;
}
.block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1300px;}
h1,h2,h3,h4{color:var(--navy);}
hr{border:none;border-top:1px solid var(--line);margin:18px 0;}

.card, .card *, .kpi, .kpi *, .tree, .tree *,
.do-box, .do-box *, .dont-box, .dont-box *,
.quiz-box, .quiz-box *, .pr-card, .pr-card *,
.exam-card, .exam-card *, .exam-meta, .exam-meta * {
    color: #2B3A4A !important;
}
.card h4, .kpi .v, .quiz-box h4, .tree b,
.card b, .card strong, .pr-card b, .pr-card strong,
.exam-card b, .exam-card strong { color: #0B3C5D !important; }
.do-box h5   { color: #14615E !important; }
.dont-box h5 { color: #9B2C2C !important; }
.card i, .card em, .kpi .l, .pr-card i { color: #5A7184 !important; }
.card code, .do-box code, .dont-box code, .quiz-box code,
.tree code, .pr-card code, .exam-card code {
    background: #EEF2F6 !important; color: #0B3C5D !important;
    padding: 1px 6px; border-radius: 4px; font-size: .85em;
}
.chip      { color: #14615E !important; }
.chip-navy { color: #0B3C5D !important; }
.chip-gold { color: #8A6512 !important; }
.chip-red  { color: #9B2C2C !important; }

.hero{
  background:linear-gradient(120deg,#0B3C5D 0%,#1D7874 100%);
  border-radius:18px;padding:46px 42px;color:#fff;margin-bottom:22px;
  box-shadow:0 10px 28px rgba(11,60,93,.25);
}
.hero-kicker{font-size:.82rem;letter-spacing:3px;text-transform:uppercase;opacity:.85;font-weight:600;}
.hero-title{font-size:2.85rem;font-weight:800;margin:10px 0 6px 0;line-height:1.08;}
.hero-sub{font-size:1.06rem;opacity:.92;font-weight:400;}

.slide-title{font-size:1.85rem;font-weight:800;color:var(--navy);margin:0 0 2px 0;line-height:1.15;}
.slide-sub{font-size:.94rem;color:var(--muted);margin:0 0 16px 0;}

/* ---------- STICKY PAGE HEADER ---------- */
.page-header{
  position: sticky;
  top: 4rem;                 /* sits below Streamlit's top bar */
  z-index: 200;
  padding: 16px 0 14px 0;
  margin: 0 0 12px 0;
  border-bottom: 2px solid var(--line);
  backdrop-filter: blur(6px);
}
.page-header .sec-num{ margin: 0 0 10px 0; }
.page-header .slide-title{ margin: 0; }
.page-header .slide-sub{ margin: 2px 0 0 0; }

.sec-num{
  display:inline-block;
  background:var(--teal);
  color:#fff;
  font-size:.7rem;
  font-weight:800;
  padding:5px 14px;
  border-radius:20px;
  letter-spacing:1.2px;
  margin:0 0 10px 0;
  line-height:1;
}

.card{
  background:#fff;border:1px solid var(--line);border-left:5px solid var(--teal);
  border-radius:10px;padding:15px 18px;margin-bottom:12px;
  box-shadow:0 1px 3px rgba(11,60,93,.06);
}
.card h4{margin:0 0 6px 0;font-size:1rem;}
.card p{margin:0;font-size:.88rem;line-height:1.55;}
.card-gold{border-left-color:var(--gold);}
.card-navy{border-left-color:var(--navy);}
.card-red{border-left-color:var(--red);}

.pr-card{
  background:#fff;border:1px solid var(--line);border-radius:12px;
  padding:20px 24px;font-family:"SF Mono",Menlo,Consolas,monospace;
  font-size:.85rem;line-height:1.8;box-shadow:0 2px 6px rgba(11,60,93,.06);
}
.pr-card .pr-title{font-size:1.05rem;font-weight:800;margin-bottom:10px;}
.pr-card .pr-badge{
  display:inline-block;padding:3px 10px;border-radius:14px;font-size:.72rem;
  font-weight:800;letter-spacing:.5px;margin-right:6px;
}
.badge-red{background:#FDECEC;color:#9B2C2C;border:1px solid #F5C6C6;}
.badge-green{background:#E8F6EE;color:#14615E;border:1px solid #BFE0DD;}
.badge-gold{background:#FDF4E3;color:#8A6512;border:1px solid #F0D9A8;}
.badge-navy{background:#E9EFF5;color:#0B3C5D;border:1px solid #C6D6E4;}

.chip{
  display:inline-block;background:#E8F3F2;color:#14615E;border:1px solid #BFE0DD;
  border-radius:20px;padding:5px 13px;margin:4px 5px 4px 0;font-size:.79rem;font-weight:600;
}
.chip-gold{background:#FDF4E3;color:#8A6512;border-color:#F0D9A8;}
.chip-navy{background:#E9EFF5;color:#0B3C5D;border-color:#C6D6E4;}
.chip-red{background:#FDECEC;color:#9B2C2C;border-color:#F5C6C6;}

.vflow{display:flex;flex-direction:column;align-items:center;gap:2px;margin:12px 0;}
.fbox{
  background:var(--navy);color:#fff;border-radius:9px;padding:10px 20px;text-align:center;
  font-weight:700;font-size:.85rem;min-width:230px;
}
.fbox-light{background:#fff;color:var(--navy);border:2px solid var(--teal);}
.fbox-teal{background:var(--teal);}
.fbox-gold{background:var(--gold);color:#3A2A05;}
.fbox-red{background:var(--red);}
.farrow{color:var(--teal);font-size:1.15rem;font-weight:800;line-height:1;}

.hflow{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:12px 0;}
.hbox{
  background:#fff;border:2px solid var(--teal);color:var(--navy);border-radius:9px;
  padding:9px 15px;font-weight:700;font-size:.82rem;
}
.hbox-navy{background:var(--navy);border-color:var(--navy);color:#fff;}
.hbox-gold{background:var(--gold);border-color:var(--gold);color:#3A2A05;}
.harrow{color:var(--teal);font-weight:800;font-size:1rem;}

.kpi{
  background:#fff;border:1px solid var(--line);border-radius:11px;padding:16px 12px;
  text-align:center;box-shadow:0 1px 3px rgba(11,60,93,.05);height:100%;
}
.kpi .v{font-size:1.4rem;font-weight:800;color:var(--navy);line-height:1.15;}
.kpi .l{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:700;}

.do-box{background:#E8F6EE;border-left:5px solid var(--green);border-radius:8px;padding:14px 16px;margin-bottom:12px;}
.do-box h5{color:#14615E;margin:0 0 8px 0;font-size:.95rem;}
.dont-box{background:#FDECEC;border-left:5px solid var(--red);border-radius:8px;padding:14px 16px;margin-bottom:12px;}
.dont-box h5{color:#9B2C2C;margin:0 0 8px 0;font-size:.95rem;}
.do-box ul,.dont-box ul{margin:0;padding-left:20px;}
.do-box li,.dont-box li{font-size:.85rem;color:var(--ink);line-height:1.7;}

.quiz-box{
  background:linear-gradient(135deg,#F0F7FB 0%,#EAF3F1 100%);
  border:2px solid #BFE0DD;border-radius:12px;padding:18px 22px;margin:10px 0;
}
.quiz-box h4{color:var(--navy);margin:0 0 10px 0;font-size:.95rem;}
.quiz-box .q{color:var(--ink);font-size:.9rem;line-height:1.6;}

.score-pill{
  display:inline-block;padding:5px 14px;border-radius:20px;font-weight:800;font-size:.8rem;margin-left:8px;
}
.pill-pass{background:#E8F6EE;color:#14615E;border:1px solid #BFE0DD;}
.pill-fail{background:#FDECEC;color:#9B2C2C;border:1px solid #F5C6C6;}
.pill-mid{background:#FDF4E3;color:#8A6512;border:1px solid #F0D9A8;}

.login-card{
  background:#fff;border:1px solid var(--line);border-radius:16px;padding:26px 26px 10px 26px;
  box-shadow:0 12px 34px rgba(11,60,93,.12);
}
.login-note{font-size:.76rem;color:#5A7184;line-height:1.5;}

.exam-card{
  background:#fff;border:1px solid var(--line);border-left:6px solid var(--navy);
  border-radius:12px;padding:20px 24px;box-shadow:0 3px 10px rgba(11,60,93,.08);
}
.exam-meta{
  background:#F3F7FA;border:1px dashed #C6D6E4;border-radius:10px;
  padding:10px 14px;font-size:.8rem;color:#2B3A4A;margin-bottom:14px;
}
.timer-box{
  display:inline-block;background:#0B3C5D;color:#fff !important;padding:9px 20px;border-radius:10px;
  font-weight:800;font-size:1.05rem;letter-spacing:1.5px;box-shadow:0 3px 10px rgba(11,60,93,.25);
}
.timer-warn{background:#C0392B !important;animation:pulse 1.2s infinite;}
@keyframes pulse{0%{opacity:1}50%{opacity:.6}100%{opacity:1}}
.qnum{
  display:inline-block;background:#1D7874;color:#fff;font-size:.7rem;font-weight:800;
  padding:3px 12px;border-radius:20px;letter-spacing:1px;
}
.user-badge{
  background:rgba(255,255,255,.12);border-radius:10px;padding:10px 12px;margin-bottom:10px;
  border:1px solid rgba(255,255,255,.18);
}
.set-badge{
  display:inline-block;background:#E9EFF5;color:#0B3C5D;border:1px solid #C6D6E4;
  border-radius:20px;padding:4px 12px;font-size:.72rem;font-weight:700;letter-spacing:.5px;
  margin-left:6px;
}

section[data-testid="stSidebar"]{background:#0B3C5D;}
section[data-testid="stSidebar"] *{color:#EAF2F8 !important;}
section[data-testid="stSidebar"] .stButton>button{
  width:100%;text-align:left;background:transparent;border:1px solid rgba(255,255,255,.18);
  color:#EAF2F8 !important;font-size:.76rem;padding:5px 10px;margin-bottom:3px;border-radius:7px;
}
section[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.4);
}
section[data-testid="stSidebar"] .stButton>button:focus{box-shadow:none;}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------------
def chips(items, cls="chip"):
    return "".join(f'<span class="{cls}">{i}</span>' for i in items)


def hflow(items, navy_idx=(), gold_idx=()):
    parts = []
    for i, it in enumerate(items):
        if i in gold_idx:
            cls = "hbox hbox-gold"
        elif i in navy_idx:
            cls = "hbox hbox-navy"
        else:
            cls = "hbox"
        parts.append(f'<span class="{cls}">{it}</span>')
        if i < len(items) - 1:
            parts.append('<span class="harrow">→</span>')
    return f'<div class="hflow">{"".join(parts)}</div>'


def vflow(items, styles=None):
    styles = styles or [""] * len(items)
    parts = []
    for i, it in enumerate(items):
        parts.append(f'<div class="fbox {styles[i]}">{it}</div>')
        if i < len(items) - 1:
            parts.append('<div class="farrow">▼</div>')
    return f'<div class="vflow">{"".join(parts)}</div>'


def header(title, sub="", num=""):
    n = f'<div class="sec-num">{num}</div>' if num else ""
    st.markdown(
        f'<div class="page-header">'
        f'{n}'
        f'<div class="slide-title">{title}</div>'
        f'<div class="slide-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def card(title, body, variant=""):
    st.markdown(
        f'<div class="card {variant}"><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def kpi_row(items):
    cols = st.columns(len(items))
    for c, (label, value) in zip(cols, items):
        c.markdown(
            f'<div class="kpi"><div class="v">{value}</div><div class="l">{label}</div></div>',
            unsafe_allow_html=True,
        )


def do_dont(do_items, dont_items):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div class="do-box"><h5>✅ Do</h5><ul>'
            + "".join(f"<li>{i}</li>" for i in do_items)
            + "</ul></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="dont-box"><h5>⛔ Do not</h5><ul>'
            + "".join(f"<li>{i}</li>" for i in dont_items)
            + "</ul></div>",
            unsafe_allow_html=True,
        )


def score_pill(score, total):
    pct = score / total if total else 0
    if pct >= 0.8:
        cls = "pill-pass"
    elif pct >= 0.5:
        cls = "pill-mid"
    else:
        cls = "pill-fail"
    return f'<span class="score-pill {cls}">{score} / {total}</span>'


def valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))


def slugify(name: str) -> str:
    """Turn a human name into a URL-safe id."""
    s = re.sub(r"[^a-zA-Z0-9]+", "_", (name or "").strip().lower()).strip("_")
    return s or "exam"

# ------------------------------------------------------------------------------
# LIVE COUNTDOWN TIMER (JavaScript-driven, ticks every second)
# ------------------------------------------------------------------------------
def _live_timer_html(remaining_seconds: int, exam_name: str = "", warn: bool = False) -> str:
    """Build the HTML+JS for a live ticking countdown timer."""
    name_escaped = html_lib.escape(exam_name or "")
    warn_style = "background:#C0392B;animation:dvtpulse 1.2s infinite;" if warn else "background:#0B3C5D;"
    return f"""
    <style>
      @keyframes dvtpulse {{0%{{opacity:1}}50%{{opacity:.6}}100%{{opacity:1}}}}
      html, body {{ margin:0; padding:0; background:transparent; overflow:hidden; }}
      .dvt-wrap {{ display:flex; align-items:center; gap:6px; padding:2px 0; }}
      .dvt-clock {{
        display:inline-block;
        {warn_style}
        color:#ffffff;
        padding:9px 20px;
        border-radius:10px;
        font-weight:800;
        font-size:1.05rem;
        letter-spacing:1.5px;
        box-shadow:0 3px 10px rgba(11,60,93,.25);
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        min-width:105px;
        text-align:center;
      }}
      .dvt-set {{
        display:inline-block;
        background:#E9EFF5;
        color:#0B3C5D;
        border:1px solid #C6D6E4;
        border-radius:20px;
        padding:4px 12px;
        font-size:.72rem;
        font-weight:700;
        letter-spacing:.5px;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
        max-width:340px;
      }}
    </style>
    <div class="dvt-wrap">
      <span id="dvt-clock" class="dvt-clock">&#9201; 00:00</span>
      <span class="dvt-set">{name_escaped}</span>
    </div>
    <script>
    (function() {{
      var remaining = {int(max(0, remaining_seconds))};
      var el = document.getElementById('dvt-clock');
      function fmt(s) {{
        var m = Math.floor(s / 60);
        var ss = s % 60;
        return (m < 10 ? '0' : '') + m + ':' + (ss < 10 ? '0' : '') + ss;
      }}
      function tick() {{
        if (remaining <= 0) {{
          el.innerHTML = '&#9201; 00:00';
          el.style.background = '#C0392B';
          el.style.animation = 'dvtpulse 1.2s infinite';
          // Trigger a Python rerun so the exam can be graded
          try {{ window.parent.location.reload(); }} catch(e) {{}}
          return;
        }}
        el.innerHTML = '&#9201; ' + fmt(remaining);
        if (remaining <= 300) {{
          el.style.background = '#C0392B';
          el.style.animation = 'dvtpulse 1.2s infinite';
        }}
        remaining -= 1;
      }}
      tick();
      setInterval(tick, 1000);
    }})();
    </script>
    """


def _render_live_timer(remaining_seconds: int, exam_name: str = "", warn: bool = False, height: int = 48):
    """Render the live ticking countdown timer inside an iframe."""
    components.html(
        _live_timer_html(remaining_seconds, exam_name, warn),
        height=height,
        scrolling=False,
    )


# ==============================================================================
# AUTHENTICATION  (all credentials come from .streamlit/secrets.toml)
# ==============================================================================
ADMIN_ROLES = ("examiner", "admin", "super_admin")


def _get_exam_access_code() -> str:
    try:
        code = st.secrets.get("exam", {}).get("access_code")
        if code:
            return str(code)
    except Exception:
        pass
    return os.getenv("EXAM_ACCESS_CODE", "")


def _get_users_from_secrets() -> dict:
    users = {}
    try:
        secret_users = st.secrets.get("users", {})
        for username, data in dict(secret_users).items():
            users[str(username).strip().lower()] = dict(data)
    except Exception:
        pass
    return users


def users_configured() -> bool:
    users = _get_users_from_secrets()
    if not users:
        return False
    return any((u.get("role") or "").lower() == "super_admin" for u in users.values())


def load_users() -> dict:
    users = _get_users_from_secrets()
    users.update(st.session_state.get("registered_users", {}))
    return users


# ------------------------------------------------------------------------------
# SESSION PERSISTENCE — survive browser refresh via a signed URL token
# ------------------------------------------------------------------------------
def _login_secret() -> str:
    """
    Secret used to sign session tokens.
    Order of precedence: st.secrets['session']['secret'] → env → dev fallback.
    Set a real secret in production, or tokens can be forged.
    """
    try:
        s = st.secrets.get("session", {}).get("secret")
        if s:
            return str(s)
    except Exception:
        pass
    return os.getenv("SESSION_SECRET", "dev-only-change-me")


def _make_token(username: str) -> str:
    """Create a signed, URL-safe token for a username."""
    secret = _login_secret().encode()
    uname = (username or "").strip().lower()
    sig = hmac.new(secret, uname.encode(), hashlib.sha256).hexdigest()
    raw = f"{uname}:{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _verify_token(token: str):
    """Return the username if the token is valid, else None."""
    if not token:
        return None
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        uname, sig = raw.split(":", 1)
    except Exception:
        return None
    secret = _login_secret().encode()
    expected = hmac.new(secret, uname.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(sig, expected):
        return uname
    return None


def _clear_session_token():
    """Remove the session token from the URL."""
    try:
        if "session" in st.query_params:
            del st.query_params["session"]
    except Exception:
        pass


def _restore_session_from_url() -> bool:
    """
    If a valid session token is present in the URL, restore the user.
    Returns True if the user is authenticated after this call.
    """
    if st.session_state.get("authenticated"):
        return True

    try:
        token = st.query_params.get("session")
    except Exception:
        token = None

    if not token:
        return False

    uname = _verify_token(token)
    if not uname:
        _clear_session_token()
        return False

    users = load_users()
    if uname not in users:
        _clear_session_token()
        return False

    # Rebuild the session as if the user had just logged in
    st.session_state.authenticated = True
    st.session_state.user = {
        "username": uname,
        "name": users[uname].get("name", uname),
        "email": users[uname].get("email", ""),
        "role": (users[uname].get("role") or "developer").lower(),
    }
    st.session_state.login_time = datetime.now().isoformat(timespec="seconds")
    return True


def login_page():
    st.markdown(
        """
        <div class="hero" style="padding:38px 34px;">
            <div class="hero-kicker">Secure Access</div>
            <div class="hero-title" style="font-size:2.3rem;">Developer Standards — Exam Portal</div>
            <div class="hero-sub">Sign in to take the graded assessment.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not users_configured():
        st.error(
            "⚠️ **No accounts are configured.** Add a `.streamlit/secrets.toml` file "
            "next to this script with at least one `super_admin` account. See the schema below."
        )
        with st.expander("📄 Required `.streamlit/secrets.toml` schema", expanded=True):
            st.markdown(
                "The file must define an `[exam]` section (for self-registration) and "
                "at least one account under `[users.<username>]` with the role "
                "`super_admin`. Replace every `<placeholder>` with your own values."
            )
            st.code(
                """# .streamlit/secrets.toml

[exam]
access_code = "<your-access-code>"      # share only with real candidates

[session]
secret = "<a-long-random-string>"       # signs session tokens for refresh-persistence

[users.<username>]
password = "<strong-password>"
name     = "<full-name>"
email    = "<email-address>"
role     = "super_admin"                # required — the app will not start without this

# Optional — add as many additional accounts as you need:
# [users.<another-username>]
# password = "<strong-password>"
# name     = "<full-name>"
# email    = "<email-address>"
# role     = "<role>"                   # developer | qa | examiner | admin""",
                language="toml",
            )
            st.markdown(
                "**Available roles**  \n"
                "`super_admin` — full access, creates other admins  \n"
                "`admin` / `examiner` — view submissions, manage exams & questions  \n"
                "`developer` / `qa` — take the exam only"
            )
            st.caption(
                "Save the file, stop the Streamlit process (Ctrl + C), and start it again — "
                "`secrets.toml` is only read at startup."
            )
        st.stop()

    _, mid, _ = st.columns([1, 1.35, 1])
    with mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        tab_in, tab_reg = st.tabs(["🔐 Sign in", "📝 Register"])

        with tab_in:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                st.checkbox("Keep me signed in for this session", value=True)
                submit = st.form_submit_button("Sign in", type="primary", use_container_width=True)

            if submit:
                users = load_users()
                u = (username or "").strip().lower()
                if not u or not password:
                    st.error("Please enter both username and password.")
                elif u in users and users[u].get("password") == password:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "username": u,
                        "name": users[u].get("name", u),
                        "email": users[u].get("email", ""),
                        "role": (users[u].get("role") or "developer").lower(),
                    }
                    st.session_state.login_time = datetime.now().isoformat(timespec="seconds")

                    # Persist across browser refresh: store a signed token in the URL
                    try:
                        st.query_params["session"] = _make_token(u)
                    except Exception:
                        pass

                    st.success(f"Welcome, {st.session_state.user['name']}!")
                    time.sleep(0.4)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        with tab_reg:
            with st.form("register_form", clear_on_submit=False):
                r_name = st.text_input("Full name")
                r_email = st.text_input("Email address")
                r_user = st.text_input("Choose a username")
                r_pass = st.text_input("Choose a password", type="password")
                r_code = st.text_input("Exam access code", type="password")
                st.caption("New registrations are always created with the **developer** role.")
                r_submit = st.form_submit_button("Create account", type="primary", use_container_width=True)

            if r_submit:
                errs = []
                if not r_name.strip():
                    errs.append("Full name is required.")
                if not valid_email(r_email):
                    errs.append("A valid email address is required.")
                if len(r_user.strip()) < 3:
                    errs.append("Username must be at least 3 characters.")
                if len(r_pass) < 6:
                    errs.append("Password must be at least 6 characters.")
                if r_code.strip() != _get_exam_access_code():
                    errs.append("Invalid exam access code.")
                if r_user.strip().lower() in load_users():
                    errs.append("That username is already taken.")

                if errs:
                    for e in errs:
                        st.error(f"❌ {e}")
                else:
                    st.session_state.registered_users[r_user.strip().lower()] = {
                        "password": r_pass,
                        "name": r_name.strip(),
                        "email": r_email.strip(),
                        "role": "developer",
                    }
                    st.success("✅ Account created. Switch to the **Sign in** tab and log in.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;margin-top:26px;color:#5A7184;font-size:.8rem;">'
        "Developer Standards &amp; Development Workflow · Mandatory for all team members"
        "</div>",
        unsafe_allow_html=True,
    )


# ==============================================================================
# DATA STORAGE  (Submissions + Exam Bank)
# ==============================================================================
SUBMISSIONS_PATH = "exam_submissions.json"
EXAM_BANK_PATH = "exam_bank.json"
LEGACY_QUESTIONS_PATH = "exam_questions.json"   # old single-set file (auto-migrated)

DEFAULT_EXAM_ID = "default"
DEFAULT_EXAM_NAME = "Developer Standards — Default Exam"
DEFAULT_EXAM_DURATION = 30
DEFAULT_EXAM_PASS_MARK = 0.80
DEFAULT_QUESTIONS_TO_PICK = 30    # how many of the pool to sample per candidate


def save_submission(record: dict) -> bool:
    try:
        data = []
        if os.path.exists(SUBMISSIONS_PATH):
            with open(SUBMISSIONS_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        data.append(record)
        with open(SUBMISSIONS_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)
        return True
    except Exception:
        return False


def load_submissions():
    if not os.path.exists(SUBMISSIONS_PATH):
        return []
    try:
        with open(SUBMISSIONS_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []


def _default_exam_dict():
    """Wrap the imported QUESTION_POOL into a single default exam set."""
    pool = globals().get("DEFAULT_EXAM_QUESTIONS", [])
    return {
        DEFAULT_EXAM_ID: {
            "name": DEFAULT_EXAM_NAME,
            "duration_minutes": DEFAULT_EXAM_DURATION,
            "pass_mark": DEFAULT_EXAM_PASS_MARK,
            "questions_to_pick": DEFAULT_QUESTIONS_TO_PICK,
            "questions": pool,
        }
    }


def load_exam_bank() -> dict:
    """
    Load the full exam bank. Order of precedence:
      1. exam_bank.json (new format, dict of exams)
      2. exam_questions.json (legacy flat list → auto-migrated)
      3. Built-in defaults
    """
    # 1. New format
    if os.path.exists(EXAM_BANK_PATH):
        try:
            with open(EXAM_BANK_PATH, "r", encoding="utf-8") as fh:
                bank = json.load(fh)
            if isinstance(bank, dict) and bank:
                return bank
        except Exception:
            pass

    # 2. Legacy flat list → migrate
    if os.path.exists(LEGACY_QUESTIONS_PATH):
        try:
            with open(LEGACY_QUESTIONS_PATH, "r", encoding="utf-8") as fh:
                legacy = json.load(fh)
            if isinstance(legacy, list) and legacy:
                migrated = {
                    DEFAULT_EXAM_ID: {
                        "name": DEFAULT_EXAM_NAME,
                        "duration_minutes": DEFAULT_EXAM_DURATION,
                        "pass_mark": DEFAULT_EXAM_PASS_MARK,
                        "questions_to_pick": DEFAULT_QUESTIONS_TO_PICK,
                        "questions": legacy,
                    }
                }
                try:
                    with open(EXAM_BANK_PATH, "w", encoding="utf-8") as fh:
                        json.dump(migrated, fh, indent=2)
                except Exception:
                    pass
                return migrated
        except Exception:
            pass

    # 3. Built-in defaults
    return _default_exam_dict()


def save_exam_bank(bank: dict) -> bool:
    try:
        with open(EXAM_BANK_PATH, "w", encoding="utf-8") as fh:
            json.dump(bank, fh, indent=2)
        return True
    except Exception:
        return False


def get_exam(bank: dict, exam_id: str) -> dict:
    """Return the exam dict for the given id (or an empty shell)."""
    return (bank or {}).get(exam_id) or {
        "name": exam_id, "duration_minutes": 30, "pass_mark": 0.80, "questions": []
    }


def list_exams(bank: dict):
    """Return a list of (exam_id, exam_name, question_count) tuples."""
    out = []
    for eid, edata in (bank or {}).items():
        out.append((eid, edata.get("name", eid), len(edata.get("questions", []))))
    return out


# ==============================================================================
# SESSION STATE
# ==============================================================================
_defaults = {
    "slide": 0,
    "scores": {},
    "dev_checklist": {},
    "final_checklist": {},
    "dev_notes": "",
    "final_notes": "",
    "wf_clicked": [],
    "scenario_state": {},
    "pr_selected": set(),
    "review_selected": set(),
    "celebrated": {"dev": False, "final": False},
    # auth
    "authenticated": False,
    "user": None,
    "registered_users": {},
    "login_time": None,
    # exam bank + selected set
    "exam_bank": {},
    "active_exam_id": None,
    # exam runtime
    "exam_started": False,
    "exam_submitted": False,
    "exam_paper": [],
    "exam_answers": {},
    "exam_idx": 0,
    "exam_start_ts": None,
    "exam_end_ts": None,
    "exam_results": [],
    "exam_score": 0,
    "exam_attempts": 0,
    "exam_agree": False,
    "exam_review_mode": False,
    # admin page helpers
    "admin_selected_exam": None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def record_score(key, value, total):
    st.session_state.scores[key] = {"value": value, "total": total}


def total_score():
    earned = sum(v["value"] for v in st.session_state.scores.values())
    possible = sum(v["total"] for v in st.session_state.scores.values())
    return earned, possible


# ==============================================================================
# DEFAULT EXAM QUESTIONS — imported from questions_pool.py
# ==============================================================================
DEFAULT_EXAM_QUESTIONS = QUESTION_POOL


# --- Load the exam bank now that DEFAULT_EXAM_QUESTIONS is defined ---
if not st.session_state.exam_bank:
    st.session_state.exam_bank = load_exam_bank()

# Set a sane default active exam
if not st.session_state.active_exam_id:
    _bank_ids = list(st.session_state.exam_bank.keys())
    if _bank_ids:
        st.session_state.active_exam_id = _bank_ids[0]


# ==============================================================================
# EXAM HELPERS (multi-set, random pool)
# ==============================================================================
EXAM_CONFIG = {
    "shuffle_questions": True,
    "shuffle_options": True,
}


def _active_exam() -> dict:
    """Return the currently selected exam dict (or an empty shell)."""
    bank = st.session_state.exam_bank or {}
    eid = st.session_state.active_exam_id
    if not eid or eid not in bank:
        if bank:
            eid = next(iter(bank.keys()))
            st.session_state.active_exam_id = eid
        else:
            return {"name": "(no exams configured)", "duration_minutes": 30, "pass_mark": 0.80, "questions": []}
    return bank[eid]


def _active_exam_questions() -> list:
    return list(_active_exam().get("questions", []))


def _active_duration_minutes() -> int:
    return int(_active_exam().get("duration_minutes", 30))


def _active_pass_mark() -> float:
    return float(_active_exam().get("pass_mark", 0.80))


def _active_questions_to_pick() -> int:
    """How many questions to sample for one candidate. 0 = use the whole pool."""
    exam = _active_exam()
    try:
        n = int(exam.get("questions_to_pick", 0) or 0)
    except Exception:
        n = 0
    pool_size = len(exam.get("questions", []))
    if n <= 0 or n > pool_size:
        return pool_size
    return n


def _build_exam_paper():
    """
    Build the exam paper for the current candidate:
      1. Take the full question pool for the active exam.
      2. Randomly sample `questions_to_pick` of them (or all if 0).
      3. Shuffle the options inside each sampled question.
      4. Shuffle the order of the sampled questions.
    Two candidates sitting at the same time will get different papers.
    """
    pool = _active_exam_questions()
    if not pool:
        return []

    pick_n = _active_questions_to_pick()
    # random.sample guarantees unique questions and a fresh pick per call.
    selected = random.sample(pool, pick_n)

    paper = []
    for q in selected:
        opts = list(q["options"])
        if EXAM_CONFIG["shuffle_options"]:
            random.shuffle(opts)
        paper.append({**q, "options": opts})

    if EXAM_CONFIG["shuffle_questions"]:
        random.shuffle(paper)

    return paper


def _exam_remaining_seconds():
    if not st.session_state.exam_started or not st.session_state.exam_start_ts:
        return _active_duration_minutes() * 60
    elapsed = time.time() - st.session_state.exam_start_ts
    return max(0, _active_duration_minutes() * 60 - elapsed)


def _reset_exam():
    st.session_state.exam_started = False
    st.session_state.exam_submitted = False
    st.session_state.exam_paper = []
    st.session_state.exam_answers = {}
    st.session_state.exam_idx = 0
    st.session_state.exam_start_ts = None
    st.session_state.exam_end_ts = None
    st.session_state.exam_results = []
    st.session_state.exam_score = 0
    st.session_state.exam_agree = False
    st.session_state.exam_review_mode = False


def _grade_exam():
    paper = st.session_state.exam_paper
    answers = st.session_state.exam_answers
    exam_id = st.session_state.active_exam_id
    exam_name = _active_exam().get("name", exam_id)

    results = []
    for i, q in enumerate(paper):
        given = answers.get(q["id"])
        correct = (given == q["answer"])
        results.append({
            "n": i + 1,
            "id": q["id"],
            "section": q["section"],
            "question": q["question"],
            "given": given,
            "answer": q["answer"],
            "correct": correct,
            "explanation": q["explanation"],
        })
    score = sum(1 for r in results if r["correct"])
    st.session_state.exam_results = results
    st.session_state.exam_score = score
    st.session_state.exam_submitted = True
    st.session_state.exam_end_ts = time.time()
    st.session_state.exam_attempts += 1
    record_score("exam", score, len(results))

    duration = st.session_state.exam_end_ts - (st.session_state.exam_start_ts or st.session_state.exam_end_ts)
    save_submission({
        "user": st.session_state.user,
        "exam_id": exam_id,
        "exam_name": exam_name,
        "submitted_at": datetime.now().isoformat(timespec="seconds"),
        "score": score,
        "total": len(results),
        "percent": round(score / len(results) * 100, 2) if results else 0,
        "attempt": st.session_state.exam_attempts,
        "duration_seconds": int(duration),
        "answers": [{"id": r["id"], "given": r["given"], "correct": r["correct"]} for r in results],
    })
    return results, score


# ==============================================================================
# EXAM SLIDE
# ==============================================================================
def s_exam():
    header(
        "Final Exam — Developer Standards",
        "Graded assessment · pick a question set, then sit the exam",
        "EXAM",
    )

    if st.session_state.exam_submitted:
        _render_exam_results()
        return
    if not st.session_state.exam_started:
        _render_exam_intro()
        return
    _render_exam_running()


def _render_exam_intro():
    bank = st.session_state.exam_bank or {}
    available = list_exams(bank)

    if not available:
        st.error("No exams are configured. An administrator must create at least one exam set.")
        return

    # ---- exam set picker ----
    st.markdown("### 🗂 Choose a question set")
    if len(available) == 1:
        eid, ename, qcount = available[0]
        st.session_state.active_exam_id = eid
        st.info(f"Only one exam set is available — **{ename}** ({qcount} questions in the pool).")
    else:
        options = {f"{ename}  ·  {qcount} questions": eid for eid, ename, qcount in available}
        current = st.session_state.active_exam_id
        current_label = next((k for k, v in options.items() if v == current), list(options.keys())[0])
        default_idx = list(options.keys()).index(current_label)

        pick = st.selectbox(
            "Which exam set do you want to take?",
            list(options.keys()),
            index=default_idx,
            key="exam_set_picker",
        )
        st.session_state.active_exam_id = options[pick]

    exam = _active_exam()
    questions = exam.get("questions", [])
    pool_size = len(questions)
    pick_n = _active_questions_to_pick()
    total = pick_n                                       # number the candidate will actually see
    duration_min = int(exam.get("duration_minutes", 30))
    pass_mark_pct = int(exam.get("pass_mark", 0.80) * 100)

    st.markdown("### 📋 Exam instructions")
    c1, c2 = st.columns([1.25, 1])
    with c1:
        st.markdown(
            f"""
            <div class="exam-card">
              <h4 style="color:#0B3C5D;margin-top:0;">Before you begin</h4>
              <ul style="font-size:.88rem;line-height:1.85;margin:0;padding-left:20px;">
                <li><b>Exam set:</b> {html_lib.escape(exam.get('name','—'))}</li>
                <li>You will be asked <b>{total} multiple-choice questions</b>, randomly selected from a pool of <b>{pool_size}</b>.</li>
                <li>You have <b>{duration_min} minutes</b>. The exam auto-submits when the timer reaches zero.</li>
                <li>The pass mark is <b>{pass_mark_pct}%</b>. Each question is worth one mark.</li>
                <li>Questions <b>and answer options</b> are shuffled for every attempt.</li>
                <li>You can move backwards and forwards and change answers until you submit.</li>
                <li>No negative marking — always answer every question.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        kpi_row([("Questions", f"{total} / {pool_size}"), ("Duration", f"{duration_min} min")])
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        kpi_row([("Pass mark", f"{pass_mark_pct}%"), ("Attempts", str(st.session_state.exam_attempts))])

    st.markdown("---")
    st.markdown("#### ✍️ Candidate")
    u = st.session_state.user or {}
    kpi_row([
        ("Name", u.get("name", "—")),
        ("Username", u.get("username", "—")),
        ("Email", u.get("email", "—")),
        ("Role", (u.get("role") or "—").upper()),
    ])

    st.markdown("---")
    agree = st.checkbox(
        "I confirm I am taking this exam as myself and I have read the instructions.",
        key="exam_agree",
    )
    c1, c2 = st.columns([1, 3])
    with c1:
        start = st.button(
            "🚀 Start exam",
            type="primary",
            use_container_width=True,
            disabled=(not agree) or (total == 0),
        )
    with c2:
        if pool_size == 0:
            st.warning("This exam set has no questions. Ask an administrator to add some.")
        elif st.session_state.exam_attempts > 0:
            st.caption(f"You have completed {st.session_state.exam_attempts} attempt(s). Retaking is allowed; your latest score is recorded.")

    if start:
        st.session_state.exam_paper = _build_exam_paper()
        st.session_state.exam_answers = {}
        st.session_state.exam_idx = 0
        st.session_state.exam_started = True
        st.session_state.exam_submitted = False
        st.session_state.exam_start_ts = time.time()
        st.session_state.exam_review_mode = False
        st.rerun()


def _render_exam_running():
    paper = st.session_state.exam_paper
    total = len(paper)
    exam_name = _active_exam().get("name", "—")

    # ---- timer (Python-side auto-grade check) ----
    remaining = _exam_remaining_seconds()
    if remaining <= 0:
        _grade_exam()
        st.warning("⏰ Time is up — your exam was submitted automatically.")
        st.rerun()

    mins, secs = divmod(int(remaining), 60)
    answered_count = sum(1 for q in paper if st.session_state.exam_answers.get(q["id"]))

    c1, c2, c3 = st.columns([1.4, 1, 1])
    with c1:
        # Live ticking timer in an iframe — updates every second in the browser
        _render_live_timer(
            remaining_seconds=int(remaining),
            exam_name=exam_name,
            warn=(remaining < 300),
        )
    with c2:
        st.markdown(
            f'<div class="kpi"><div class="v">{answered_count} / {total}</div>'
            f'<div class="l">Answered</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        label = "Review" if st.session_state.exam_review_mode else f"{st.session_state.exam_idx + 1} / {total}"
        st.markdown(
            f'<div class="kpi"><div class="v">{label}</div>'
            f'<div class="l">Current</div></div>',
            unsafe_allow_html=True,
        )

    st.progress(answered_count / total if total else 0)

    # ---- review mode ----
    if st.session_state.exam_review_mode:
        st.markdown("---")
        st.markdown("### 📋 Review your answers")

        unanswered = [i for i, qq in enumerate(paper) if not st.session_state.exam_answers.get(qq["id"])]
        if unanswered:
            st.warning(
                f"⚠️ You have **{len(unanswered)}** unanswered question(s): "
                + ", ".join(str(i + 1) for i in unanswered)
            )
        else:
            st.success("✅ All questions answered.")

        rows = []
        for i, qq in enumerate(paper):
            given = st.session_state.exam_answers.get(qq["id"])
            rows.append({
                "#": i + 1,
                "Section": qq["section"],
                "Your answer": given or "— not answered —",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

        confirm = st.checkbox(
            "I understand that once submitted my answers are final.",
            key="exam_confirm_final",
        )
        cc1, cc2 = st.columns([1, 1])
        with cc1:
            if st.button("✅ Submit exam", type="primary", use_container_width=True, disabled=not confirm):
                _grade_exam()
                st.rerun()
        with cc2:
            if st.button("↩ Back to questions", use_container_width=True):
                st.session_state.exam_review_mode = False
                if st.session_state.exam_idx >= total:
                    st.session_state.exam_idx = max(0, total - 1)
                st.rerun()
        return

    # ---- normal question mode ----
    idx = st.session_state.exam_idx
    if idx < 0:
        idx = 0
    if idx >= total:
        idx = total - 1
    st.session_state.exam_idx = idx

    st.markdown("---")
    st.markdown("##### Question navigator")
    nav_cols = st.columns(min(12, total))
    for i in range(total):
        qid = paper[i]["id"]
        is_answered = st.session_state.exam_answers.get(qid) is not None
        label = f"{'✓' if is_answered else '○'} {i+1}"
        if nav_cols[i % len(nav_cols)].button(
            label,
            key=f"pal_{i}",
            use_container_width=True,
            type="primary" if i == idx else "secondary",
        ):
            st.session_state.exam_idx = i
            st.rerun()

    st.markdown("---")

    q = paper[idx]
    st.markdown(
        f'<div class="exam-card">'
        f'<span class="qnum">QUESTION {idx + 1} OF {total}</span>'
        f'<div style="font-size:.72rem;color:#5A7184;letter-spacing:1px;margin-top:8px;'
        f'text-transform:uppercase;font-weight:700;">{html_lib.escape(q["section"])}</div>'
        f'<div style="font-size:1.05rem;font-weight:700;color:#0B3C5D;margin-top:8px;line-height:1.5;">'
        f'{html_lib.escape(q["question"])}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    prev_answer = st.session_state.exam_answers.get(q["id"])
    opts = q["options"]
    default_index = opts.index(prev_answer) if prev_answer in opts else None

    choice = st.radio(
        "Select one answer",
        opts,
        index=default_index,
        key=f"exam_radio_{q['id']}",
        label_visibility="collapsed",
    )
    st.session_state.exam_answers[q["id"]] = choice

    st.markdown("---")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        if st.button("⬅ Previous", use_container_width=True, disabled=idx == 0):
            st.session_state.exam_idx = max(0, idx - 1)
            st.rerun()
    with c2:
        if st.button("Next ➡", use_container_width=True, disabled=idx >= total - 1):
            st.session_state.exam_idx = min(total - 1, idx + 1)
            st.rerun()
    with c3:
        if st.button("🧹 Clear answer", use_container_width=True):
            st.session_state.exam_answers[q["id"]] = None
            st.rerun()
    with c4:
        if st.button("📋 Review & submit", use_container_width=True, type="primary"):
            st.session_state.exam_review_mode = True
            st.rerun()


def _render_exam_results():
    results = st.session_state.exam_results
    score = st.session_state.exam_score
    total = len(results)
    pct = score / total * 100 if total else 0
    pass_mark_pct = int(_active_pass_mark() * 100)
    passed = pct >= pass_mark_pct

    exam_name = _active_exam().get("name", "—")

    duration_secs = int((st.session_state.exam_end_ts or 0) - (st.session_state.exam_start_ts or 0))
    duration_txt = f"{duration_secs // 60} min {duration_secs % 60} sec"

    if passed:
        st.success(f"🏆 **PASSED** — {score}/{total} ({pct:.1f}%). Excellent work.")
        st.balloons()
    else:
        st.error(f"❌ **NOT PASSED** — {score}/{total} ({pct:.1f}%). The pass mark is {pass_mark_pct}%.")

    kpi_row([
        ("Exam set", exam_name),
        ("Score", f"{score} / {total}"),
        ("Percentage", f"{pct:.1f}%"),
        ("Time taken", duration_txt),
    ])

    st.progress(min(pct / 100, 1.0))
    st.markdown("---")

    df = pd.DataFrame(results)
    sec = (
        df.groupby("section")
          .agg(Correct=("correct", "sum"), Total=("correct", "count"))
          .reset_index()
          .rename(columns={"section": "Section"})
    )
    sec["Percent"] = (sec["Correct"] / sec["Total"] * 100).round(1)
    sec["Status"] = sec["Percent"].apply(lambda v: "✅ Pass" if v >= 80 else ("⚠️ Partial" if v >= 50 else "❌ Weak"))

    c1, c2 = st.columns([1, 1.15])
    with c1:
        st.markdown("#### Performance by section")
        st.dataframe(sec, hide_index=True, use_container_width=True)
    with c2:
        st.markdown("#### Section chart")
        fig = go.Figure(
            go.Bar(
                x=sec["Section"],
                y=sec["Percent"],
                text=[f"{p:.0f}%" for p in sec["Percent"]],
                textposition="outside",
                marker_color=["#1E8449" if p >= 80 else ("#D9A441" if p >= 50 else "#C0392B") for p in sec["Percent"]],
            )
        )
        fig.add_hline(y=pass_mark_pct, line_dash="dash", line_color="#0B3C5D", annotation_text=f"Pass {pass_mark_pct}%")
        fig.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(range=[0, 110], title="% correct"),
            xaxis=dict(tickangle=-25),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📥 Download your results")
    st.caption("Download your results below and submit them to your examiner or administrator.")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    username = (st.session_state.user or {}).get("username", "candidate")

    export = {
        "candidate": st.session_state.user,
        "exam_id": st.session_state.active_exam_id,
        "exam_name": exam_name,
        "submitted_at": datetime.now().isoformat(timespec="seconds"),
        "score": score,
        "total": total,
        "percent": round(pct, 2),
        "passed": passed,
        "duration_seconds": duration_secs,
        "attempt": st.session_state.exam_attempts,
        "results": results,
    }

    txt_lines = [
        "DEVELOPER STANDARDS — FINAL EXAM SUBMISSION",
        "=" * 52,
        f"Exam set  : {exam_name}",
        f"Candidate : {(st.session_state.user or {}).get('name','')}",
        f"Username  : {username}",
        f"Email     : {(st.session_state.user or {}).get('email','')}",
        f"Submitted : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Time taken: {duration_txt}",
        f"Score     : {score}/{total} ({pct:.1f}%) — {'PASS' if passed else 'FAIL'}",
        "",
        "QUESTION-BY-QUESTION",
        "-" * 52,
    ]
    for r in results:
        txt_lines += [
            f"{r['n']}. [{r['section']}] {r['question']}",
            f"   Given  : {r['given'] or '— not answered —'}",
            f"   Correct: {r['answer']}",
            f"   Result : {'CORRECT' if r['correct'] else 'INCORRECT'}",
            "",
        ]
    txt_body = "\n".join(txt_lines)

    csv_df = pd.DataFrame([
        {
            "No": r["n"],
            "Section": r["section"],
            "Question": r["question"],
            "Given": r["given"] or "",
            "Correct answer": r["answer"],
            "Result": "Correct" if r["correct"] else "Incorrect",
        }
        for r in results
    ])

    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "📥 Download TXT",
            data=txt_body,
            file_name=f"exam_{st.session_state.active_exam_id}_{username}_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "📥 Download CSV",
            data=csv_df.to_csv(index=False),
            file_name=f"exam_{st.session_state.active_exam_id}_{username}_{ts}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with d3:
        st.download_button(
            "📥 Download JSON",
            data=json.dumps(export, indent=2, default=str),
            file_name=f"exam_{st.session_state.active_exam_id}_{username}_{ts}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")
    with st.expander("🔍 Full question-by-question review", expanded=False):
        for r in results:
            if r["correct"]:
                st.success(f"✅ **Q{r['n']} · {r['section']}** — {r['question']}\n\nYour answer: **{r['given']}**")
            else:
                st.error(
                    f"❌ **Q{r['n']} · {r['section']}** — {r['question']}\n\n"
                    f"Your answer: **{r['given'] or '— not answered —'}**  \n"
                    f"Correct answer: **{r['answer']}**  \n\n_{r['explanation']}_"
                )

    st.markdown("---")
    if st.button("🔄 Retake exam", use_container_width=True):
        _reset_exam()
        st.rerun()


# ==============================================================================
# EXAMINER / ADMIN — VIEW SUBMISSIONS
# ==============================================================================
def s_submissions():
    header("Exam Submissions", "Recorded exam attempts (admin / examiner view)", "ADMIN")

    role = (st.session_state.user or {}).get("role")
    if role not in ADMIN_ROLES:
        st.error("🚫 Access denied. This section is only available to administrators.")
        return

    data = load_submissions()
    if not data:
        st.info("No submissions have been recorded on this server yet.")
        return

    rows = []
    for d in data:
        u = d.get("user") or {}
        rows.append({
            "Submitted": d.get("submitted_at", ""),
            "Exam set": d.get("exam_name", d.get("exam_id", "—")),
            "Name": u.get("name", ""),
            "Username": u.get("username", ""),
            "Email": u.get("email", ""),
            "Score": f"{d.get('score')}/{d.get('total')}",
            "Percent": d.get("percent"),
            "Attempt": d.get("attempt"),
        })
    df = pd.DataFrame(rows)

    # ---- filters ----
    st.markdown("### Filters")
    c1, c2 = st.columns(2)
    with c1:
        exam_filter = st.selectbox(
            "Exam set",
            ["All"] + sorted(df["Exam set"].unique().tolist()),
            key="sub_exam_filter",
        )
    with c2:
        user_filter = st.selectbox(
            "Candidate",
            ["All"] + sorted(df["Username"].unique().tolist()),
            key="sub_user_filter",
        )

    view = df.copy()
    if exam_filter != "All":
        view = view[view["Exam set"] == exam_filter]
    if user_filter != "All":
        view = view[view["Username"] == user_filter]

    # ---- summary stats ----
    total_subs = len(view)
    unique_users = view["Username"].nunique() if "Username" in view else 0
    pass_count = int((view["Percent"] >= 80).sum()) if "Percent" in view else 0
    avg_pct = float(view["Percent"].mean()) if "Percent" in view else 0.0

    kpi_row([
        ("Submissions", str(total_subs)),
        ("Unique candidates", str(unique_users)),
        ("Passed (≥80%)", f"{pass_count}/{total_subs}"),
        ("Average %", f"{avg_pct:.1f}%"),
    ])

    st.markdown("---")
    st.markdown("### Submissions")
    st.dataframe(view, hide_index=True, use_container_width=True)

    st.download_button(
        "📥 Download view (CSV)",
        data=view.to_csv(index=False),
        file_name=f"exam_submissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

    # ---- candidate drill-down ----
    st.markdown("---")
    st.markdown("### Candidate detail")
    candidates = sorted(view["Username"].unique().tolist()) if not view.empty else []
    if candidates:
        pick = st.selectbox("Select a candidate", ["— select —"] + candidates, key="sub_pick")
        if pick and pick != "— select —":
            matching = [d for d in reversed(data) if (d.get("user") or {}).get("username") == pick]
            if exam_filter != "All":
                matching = [d for d in matching if d.get("exam_name") == exam_filter]
            sub = matching[0] if matching else None
            if sub:
                u = sub.get("user") or {}
                st.markdown(
                    f"**{u.get('name','')}** · {u.get('email','')}  \n"
                    f"Exam: **{sub.get('exam_name', sub.get('exam_id','—'))}**  \n"
                    f"Submitted: `{sub.get('submitted_at','')}`  \n"
                    f"Score: **{sub.get('score')}/{sub.get('total')}** ({sub.get('percent')}%)  \n"
                    f"Attempt: {sub.get('attempt')}"
                )
                ans_rows = []
                for a in sub.get("answers", []):
                    ans_rows.append({
                        "Question ID": a.get("id"),
                        "Given": a.get("given") or "—",
                        "Correct?": "✅" if a.get("correct") else "❌",
                    })
                st.dataframe(pd.DataFrame(ans_rows), hide_index=True, use_container_width=True)

    # ---- danger zone ----
    st.markdown("---")
    with st.expander("⚠️ Danger zone"):
        st.caption("Deleting submissions is permanent and affects every administrator.")
        confirm = st.checkbox("I understand this will permanently delete all recorded submissions.", key="wipe_confirm")
        if st.button("🗑 Delete ALL submissions", disabled=not confirm, type="secondary"):
            try:
                if os.path.exists(SUBMISSIONS_PATH):
                    os.remove(SUBMISSIONS_PATH)
                st.success("All submissions deleted.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not delete submissions: {exc}")


# ==============================================================================
# ADMIN — EXAM & QUESTION MANAGEMENT (multi-set, random pool)
# ==============================================================================
def s_question_management():
    header(
        "Exam & Question Management",
        "Create exam sets and manage the questions inside each one",
        "ADMIN",
    )

    role = (st.session_state.user or {}).get("role")
    if role not in ("admin", "super_admin"):
        st.error("🚫 Access denied. Only administrators can manage exams and questions.")
        return

    bank = st.session_state.exam_bank
    st.info(
        "Changes made here are saved to `exam_bank.json` and take effect for all future exam attempts. "
        "Each **exam set** is a pool of questions — candidates receive a **random sample** of the pool, "
        "with options shuffled. Two candidates sitting at the same time see different papers."
    )

    tab_sets, tab_questions = st.tabs(["🗂 Exam Sets", "❓ Questions"])

    # =========================================================================
    # TAB 1 — EXAM SETS
    # =========================================================================
    with tab_sets:
        st.markdown("### Existing exam sets")

        if not bank:
            st.warning("No exam sets exist yet. Create one below.")
        else:
            summary_rows = []
            for eid, edata in bank.items():
                pool_n = len(edata.get("questions", []))
                pick_n = edata.get("questions_to_pick", 0) or 0
                if pick_n <= 0 or pick_n > pool_n:
                    pick_n = pool_n
                summary_rows.append({
                    "Exam ID": eid,
                    "Name": edata.get("name", eid),
                    "Pool Size": pool_n,
                    "Picked per Candidate": pick_n,
                    "Duration (min)": edata.get("duration_minutes", 30),
                    "Pass mark": f"{int(edata.get('pass_mark', 0.80) * 100)}%",
                })
            st.dataframe(pd.DataFrame(summary_rows), hide_index=True, use_container_width=True)

            st.markdown("---")
            st.markdown("#### Edit an exam set")
            edit_id = st.selectbox(
                "Select an exam set to edit",
                ["— select —"] + list(bank.keys()),
                key="exam_edit_select",
            )
            if edit_id and edit_id != "— select —":
                edata = bank[edit_id]
                pool_n = len(edata.get("questions", []))

                with st.form(f"edit_exam_{edit_id}"):
                    new_name = st.text_input("Exam name", value=edata.get("name", edit_id))
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        new_duration = st.number_input(
                            "Duration (minutes)",
                            min_value=1, max_value=300,
                            value=int(edata.get("duration_minutes", 30)),
                            step=1,
                        )
                    with cc2:
                        new_pass = st.number_input(
                            "Pass mark (%)",
                            min_value=1, max_value=100,
                            value=int(edata.get("pass_mark", 0.80) * 100),
                            step=1,
                        )
                    new_pick = st.number_input(
                        "Questions to pick per candidate (0 = use all)",
                        min_value=0, max_value=1000,
                        value=int(edata.get("questions_to_pick", 0)),
                        step=1,
                        help=f"Currently the pool has {pool_n} questions. "
                             f"Candidates will be given a random sample of this size.",
                    )
                    save_edit = st.form_submit_button("💾 Save changes", type="primary", use_container_width=True)

                if save_edit:
                    edata["name"] = new_name.strip() or edit_id
                    edata["duration_minutes"] = int(new_duration)
                    edata["pass_mark"] = round(float(new_pass) / 100.0, 4)
                    edata["questions_to_pick"] = int(new_pick)
                    if save_exam_bank(bank):
                        st.success(f"✅ Updated **{edata['name']}**.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save changes.")

                # Delete exam set
                st.markdown("---")
                st.markdown("#### ⚠️ Delete this exam set")
                st.caption("This permanently removes the exam set and every question inside it.")
                confirm_del = st.checkbox(
                    f"I understand this will delete **{edata.get('name', edit_id)}** and all its questions.",
                    key=f"confirm_del_{edit_id}",
                )
                if st.button("🗑 Delete exam set", disabled=not confirm_del, type="secondary"):
                    bank.pop(edit_id, None)
                    if save_exam_bank(bank):
                        if st.session_state.active_exam_id == edit_id:
                            st.session_state.active_exam_id = next(iter(bank.keys()), None)
                        st.success("Exam set deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to save after deletion.")

        # ---- Create new exam set ----
        st.markdown("---")
        st.markdown("### ➕ Create a new exam set")
        with st.form("create_exam_form", clear_on_submit=True):
            n_name = st.text_input("Exam name", placeholder="e.g. Exam 02 — Advanced Standards")
            n_desc = st.text_input("Description (optional)", placeholder="e.g. Advanced SQL and review scenarios")
            cc1, cc2 = st.columns(2)
            with cc1:
                n_duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30, step=1)
            with cc2:
                n_pass = st.number_input("Pass mark (%)", min_value=1, max_value=100, value=80, step=1)
            n_pick = st.number_input(
                "Questions to pick per candidate (0 = use all)",
                min_value=0, max_value=1000, value=DEFAULT_QUESTIONS_TO_PICK, step=1,
                help="Candidates receive this many questions randomly sampled from the pool.",
            )
            created = st.form_submit_button("➕ Create exam set", type="primary", use_container_width=True)

        if created:
            if not n_name.strip():
                st.error("❌ Exam name is required.")
            else:
                base_id = slugify(n_name)
                new_id = base_id
                suffix = 2
                while new_id in bank:
                    new_id = f"{base_id}_{suffix}"
                    suffix += 1

                bank[new_id] = {
                    "name": n_name.strip(),
                    "description": n_desc.strip(),
                    "duration_minutes": int(n_duration),
                    "pass_mark": round(float(n_pass) / 100.0, 4),
                    "questions_to_pick": int(n_pick),
                    "questions": [],
                }
                if save_exam_bank(bank):
                    st.session_state.admin_selected_exam = new_id
                    st.success(f"✅ Exam set **{n_name.strip()}** created (`{new_id}`). Add questions in the Questions tab.")
                    st.rerun()
                else:
                    st.error("❌ Failed to save the new exam set.")

    # =========================================================================
    # TAB 2 — QUESTIONS
    # =========================================================================
    with tab_questions:
        if not bank:
            st.warning("Create an exam set first (see the **Exam Sets** tab).")
            return

        # ---- pick which exam we're editing ----
        exam_ids = list(bank.keys())
        if st.session_state.admin_selected_exam not in exam_ids:
            st.session_state.admin_selected_exam = exam_ids[0]

        current_exam_id = st.selectbox(
            "Exam set",
            exam_ids,
            index=exam_ids.index(st.session_state.admin_selected_exam),
            format_func=lambda eid: f"{bank[eid].get('name', eid)} ({len(bank[eid].get('questions', []))} questions)",
            key="qmgmt_exam_picker",
        )
        st.session_state.admin_selected_exam = current_exam_id
        edata = bank[current_exam_id]
        questions = edata.get("questions", [])

        # ---- list current questions ----
        st.markdown(f"### Questions in **{edata.get('name', current_exam_id)}** ({len(questions)})")
        if not questions:
            st.info("No questions yet in this exam set. Add one below.")
        else:
            for i, q in enumerate(questions):
                with st.expander(f"{(q.get('id') or f'Q{i+1:02d}')}  ·  {q.get('section', 'Uncategorized')}  —  {q.get('question','')[:70]}..."):
                    st.markdown(f"**Question:** {q.get('question','')}")
                    for o in q.get("options", []):
                        prefix = "✅" if o == q.get("answer") else "○"
                        st.markdown(f"{prefix} {o}")
                    st.caption(f"**Explanation:** {q.get('explanation','')}")

                    if st.button("🗑 Delete this question", key=f"del_q_{current_exam_id}_{i}"):
                        questions.pop(i)
                        edata["questions"] = questions
                        if save_exam_bank(bank):
                            st.success("Question deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to save after deletion.")

        # ---- add new question ----
        st.markdown("---")
        st.markdown(f"### ➕ Add a question to **{edata.get('name', current_exam_id)}**")
        with st.form(f"add_question_form_{current_exam_id}", clear_on_submit=True):
            q_section = st.text_input("Section", value="1. Purpose & Governance")
            q_text = st.text_area("Question text", height=90)

            st.markdown("**Options** — all four are required")
            cc1, cc2 = st.columns(2)
            with cc1:
                q_opt1 = st.text_input("Option A")
                q_opt3 = st.text_input("Option C")
            with cc2:
                q_opt2 = st.text_input("Option B")
                q_opt4 = st.text_input("Option D")

            options = [q_opt1.strip(), q_opt2.strip(), q_opt3.strip(), q_opt4.strip()]
            valid_options = [o for o in options if o]
            q_ans = st.selectbox(
                "Correct answer",
                valid_options if valid_options else ["— fill options first —"],
            )
            q_exp = st.text_area("Explanation", height=70)
            add_btn = st.form_submit_button("➕ Add question", type="primary", use_container_width=True)

        if add_btn:
            errs = []
            if not q_text.strip():
                errs.append("Question text is required.")
            if any(not o for o in options):
                errs.append("All four options are required.")
            if not q_ans or q_ans == "— fill options first —":
                errs.append("You must select a correct answer.")
            if not q_section.strip():
                errs.append("Section is required.")

            if errs:
                for e in errs:
                    st.error(f"❌ {e}")
            else:
                # per-exam question id counter
                existing_ids = [q.get("id", "") for q in questions if q.get("id", "").startswith("Q")]
                nums = []
                for eid in existing_ids:
                    m = re.match(r"^Q(\d+)$", eid)
                    if m:
                        nums.append(int(m.group(1)))
                next_num = (max(nums) + 1) if nums else 1
                new_qid = f"Q{next_num:02d}"

                new_q = {
                    "id": new_qid,
                    "section": q_section.strip(),
                    "question": q_text.strip(),
                    "options": options,
                    "answer": q_ans,
                    "explanation": q_exp.strip(),
                }
                questions.append(new_q)
                edata["questions"] = questions
                if save_exam_bank(bank):
                    st.success(f"✅ Question {new_qid} added to **{edata.get('name', current_exam_id)}**.")
                    st.rerun()
                else:
                    st.error("❌ Failed to save the question.")


# ==============================================================================
# SUPER ADMIN — MANAGE ADMIN ACCOUNTS
# ==============================================================================
def s_admin_management():
    header(
        "Admin Management",
        "Create and review administrator accounts (super-admin only)",
        "SUPER ADMIN",
    )

    if (st.session_state.user or {}).get("role") != "super_admin":
        st.error("🚫 Access denied. Only the super administrator may manage admin accounts.")
        return

    st.info(
        "Only the **super administrator** can create administrator accounts. "
        "Regular users who register through the login screen are always assigned the "
        "**developer** role — they can never create or log in as an administrator."
    )

    st.markdown("### Existing administrator accounts")
    users = load_users()
    admin_rows = []
    for uname, u in users.items():
        role = (u.get("role") or "").lower()
        if role in ADMIN_ROLES:
            admin_rows.append({
                "Username": uname,
                "Name": u.get("name", ""),
                "Email": u.get("email", ""),
                "Role": role,
            })
    if admin_rows:
        st.dataframe(pd.DataFrame(admin_rows), hide_index=True, use_container_width=True)
    else:
        st.info("No administrator accounts found.")

    st.markdown("---")
    st.markdown("### Create a new administrator account")
    with st.form("create_admin_form", clear_on_submit=True):
        a_name = st.text_input("Full name")
        a_email = st.text_input("Email address")
        a_user = st.text_input("Username", placeholder="e.g. examiner01")
        a_pass = st.text_input("Password", type="password")
        a_role = st.selectbox("Role", ["examiner", "admin"])
        submitted = st.form_submit_button("Create admin account", type="primary", use_container_width=True)

    if submitted:
        errs = []
        if not a_name.strip():
            errs.append("Full name is required.")
        if not valid_email(a_email):
            errs.append("A valid email address is required.")
        if len(a_user.strip()) < 3:
            errs.append("Username must be at least 3 characters.")
        if len(a_pass) < 6:
            errs.append("Password must be at least 6 characters.")
        if a_user.strip().lower() in load_users():
            errs.append("That username already exists.")
        if a_role not in ("examiner", "admin"):
            errs.append("Role must be 'examiner' or 'admin'.")

        if errs:
            for e in errs:
                st.error(f"❌ {e}")
        else:
            st.session_state.registered_users[a_user.strip().lower()] = {
                "password": a_pass,
                "name": a_name.strip(),
                "email": a_email.strip(),
                "role": a_role,
            }
            st.success(
                f"✅ Admin account created: **{a_user.strip().lower()}** with role **{a_role}**. "
                "It is active immediately — the user can now sign in with the credentials you set."
            )
            st.rerun()

    st.markdown("---")
    st.caption(
        "ℹ️ Accounts created here live in this Streamlit session only. "
        "To persist them across restarts, add them under `[users.<username>]` in `.streamlit/secrets.toml`."
    )


# ==============================================================================
# SLIDE 1 — TITLE
# ==============================================================================
def s_title():
    u = st.session_state.user or {}
    total_qs = sum(len(e.get("questions", [])) for e in (st.session_state.exam_bank or {}).values())
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">Interactive Technical Standards</div>
            <div class="hero-title">Developer Standards &amp; Development Workflow</div>
            <div class="hero-sub">Welcome, <b>{html_lib.escape(u.get('name',''))}</b> — play through the simulators, then sit the graded final exam.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    kpi_row(
        [
            ("Status", "MANDATORY"),
            ("Exam Sets", str(len(st.session_state.exam_bank or {}))),
            ("Total Questions", str(total_qs)),
            ("Pass Mark", "80% (default)"),
        ]
    )
    st.markdown("---")
    c1, c2 = st.columns([1.15, 1])
    with c1:
        card(
            "What makes this different",
            "Each section includes a <b>hands-on activity</b> — paste real TypeScript to scan for `any`, "
            "simulate a Git branch flow, triage a failing test, order the workflow, and more.",
            "card-gold",
        )
        card(
            "Graded final exam",
            f"<b>{len(st.session_state.exam_bank or {})} exam set(s)</b> available. "
            "A random subset of the pool is served to each candidate, "
            "with questions and options shuffled, auto-submit on timeout, and a per-section breakdown. "
            "Your results are <b>recorded locally and can be downloaded</b>.",
            "card-navy",
        )
        st.success("👉 Use the sidebar to jump around, or click **Next** to walk through in order.")
    with c2:
        st.markdown("#### What you'll interact with")
        st.markdown(
            chips(
                [
                    "Type Detective (paste code)",
                    "Knowledge quizzes",
                    "Branch Flow Simulator",
                    "PR Review Simulator",
                    "Live testing checklist",
                    "SQL Plan Inspector",
                    "Real PR Review",
                    "Failure Triage",
                    "Order the Workflow",
                    "Scenario Simulator",
                    "Final Compliance Checklist",
                    "Graded Final Exam (random pool)",
                    "Progress Dashboard",
                ],
                "chip chip-navy",
            ),
            unsafe_allow_html=True,
        )


# ==============================================================================
# SLIDE 2 — PURPOSE
# ==============================================================================
def s_purpose():
    header("Purpose & Objectives", "Why these standards exist and what they achieve", "SECTION 1")
    c1, c2 = st.columns([1, 1])
    with c1:
        card(
            "Purpose",
            "All developers must follow the agreed development standards throughout implementation, "
            "testing, code review, and deployment.",
            "card-navy",
        )
        card(
            "Core Objective",
            "Maintain code quality, improve application performance, reduce defects, and ensure all "
            "changes are ready for QA and automated testing.",
            "card-gold",
        )
    with c2:
        st.markdown("#### What these standards achieve")
        st.markdown(
            chips(
                [
                    "Better code quality",
                    "Type safety",
                    "Maintainability",
                    "Fewer runtime errors",
                    "Faster SQL",
                    "Consistent Git flow",
                    "Developer ownership of testing",
                    "QA-ready deliveries",
                    "Less QA rework",
                ]
            ),
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.info("These practices are **mandatory** for all new development work and applicable maintenance changes.")
    st.markdown("#### Quick warm-up question")
    with st.form("warmup"):
        answer = st.radio(
            "Who is responsible for verifying a developer's own implementation before PR or QA handover?",
            [
                "The QA team — that's their job",
                "The technical lead reviewing the PR",
                "The developer who wrote the code",
                "Nobody — automated tests catch everything",
            ],
            index=None,
        )
        submitted = st.form_submit_button("Check answer")
        if submitted:
            if answer == "The developer who wrote the code":
                st.success("✅ Correct! **Developer testing is a mandatory pre-PR step.**")
                record_score("warmup", 1, 1)
            elif answer:
                st.error("❌ Not quite. The **developer** owns verification before review or QA handover.")
                record_score("warmup", 0, 1)
            else:
                st.warning("Pick an option first.")


# ==============================================================================
# SLIDE 3 — TYPE DETECTIVE
# ==============================================================================
def s_type_detective():
    header(
        "TypeScript Type Safety — Type Detective",
        "Paste TypeScript code and let the app scan for `any` usage",
        "SECTION 2.1",
    )
    do_dont(
        do_items=[
            "Use correct primitives, interfaces, and domain-specific types.",
            "Define explicit types for params, return values, and API responses.",
            "Use `unknown` when a value's type is genuinely unknown — validate before use.",
            "Reuse existing type definitions where applicable.",
        ],
        dont_items=[
            "Use `any` to bypass TypeScript errors.",
            "Use `any` just because defining the correct type takes effort.",
            "Ignore type errors to make lint or build checks pass.",
            "Introduce unnecessary type assertions without validating data.",
        ],
    )
    st.markdown("---")
    st.markdown("### 🔍 Type Detective — paste your code below")
    default_code = """async function getLoan(id: any): Promise<any> {
    const res: any = await fetch(`/api/loans/${id}`);
    const data = await res.json() as any;
    const items: any[] = data.items;
    return items.map((x: any) => x.balance);
}
"""
    code = st.text_area("TypeScript / JavaScript code", value=default_code, height=180, key="detective_code")
    if st.button("🕵️ Analyze code", type="primary"):
        patterns = {
            "`: any`": r":\s*any\b",
            "`<any>`": r"<\s*any\s*>",
            "`as any`": r"\bas\s+any\b",
            "`any[]`": r"\bany\s*\[\s*\]",
            "`Array<any>`": r"Array\s*<\s*any\s*>",
            "`Promise<any>`": r"Promise\s*<\s*any\s*>",
            "bare `any`": r"(?<![\w.])any(?![\w])",
        }
        found = {}
        for label, pat in patterns.items():
            matches = re.findall(pat, code)
            if matches:
                found[label] = len(matches)
        total_any = sum(found.values())
        lines = len([l for l in code.splitlines() if l.strip()])
        density = (total_any / lines * 100) if lines else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("`any` Occurrences", total_any)
        c2.metric("Lines of code", lines)
        c3.metric("Density", f"{density:.1f}%")
        if total_any == 0:
            st.success("🎉 Excellent — no `any` types detected. Type-safe code.")
            record_score("type_detective", 5, 5)
        elif total_any <= 2:
            st.warning("⚠️ Minor `any` usage — review and replace with specific types where reasonable.")
            record_score("type_detective", 3, 5)
        else:
            st.error("❌ Significant `any` usage. Replace with specific types, `unknown`, or existing interfaces.")
            record_score("type_detective", 1, 5)
        if found:
            st.markdown("#### Breakdown")
            df = pd.DataFrame([{"Pattern": k, "Count": v} for k, v in found.items()]).sort_values("Count", ascending=False)
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.markdown("#### Suggested replacements")
            st.markdown(
                """
                - `: any` → define an interface or type alias for the shape
                - `Promise<any>` → `Promise<LoanResponse>` (typed API contract)
                - `as any` → `unknown` + type guard / validator
                - `any[]` → `Loan[]` with a proper element type
                - `data.items` — validate with a schema before use
                """
            )
        st.caption("Only **documented, boundary-limited** `any` usage is acceptable.")


# ==============================================================================
# SLIDE 4 — TYPE SAFETY QUIZ
# ==============================================================================
def s_type_quiz():
    header(
        "TypeScript Type Safety — Knowledge Check",
        "Three quick questions to lock in the standard",
        "SECTION 2.2",
    )
    questions = [
        {
            "q": "Which is the **correct** alternative to `any` when a value's type is genuinely unknown?",
            "options": ["`never`", "`unknown`", "`object`", "`{}`"],
            "answer": 1,
            "explain": "`unknown` is the type-safe counterpart of `any`. It forces you to validate or narrow the type before using it.",
        },
        {
            "q": "Before requesting a PR review, which of these is NOT a required check?",
            "options": [
                "TypeScript type checks pass",
                "Relevant lint checks pass",
                "Every single function has a unit test",
                "API request / response types match actual data structures",
            ],
            "answer": 2,
            "explain": "100% unit-test coverage is not required. However, meaningful tests covering business rules, edge cases and error scenarios ARE expected.",
        },
        {
            "q": "If `any` is genuinely required, what is the correct behaviour?",
            "options": [
                "Just use it — no explanation needed",
                "Document the reason and keep usage limited to the relevant boundary",
                "Replace it with `object` to silence the linter",
                "Add `// @ts-ignore` instead",
            ],
            "answer": 1,
            "explain": "Documented, boundary-limited `any` is acceptable. Undocumented, spread-out `any` is not.",
        },
    ]
    for i, item in enumerate(questions):
        with st.expander(f"Q{i+1}: {item['q']}", expanded=(i == 0)):
            choice = st.radio("Select an answer", item["options"], index=None, key=f"typeq_{i}", label_visibility="collapsed")
            if st.button("Submit answer", key=f"typeq_btn_{i}"):
                if choice is None:
                    st.warning("Pick an option first.")
                elif choice == item["options"][item["answer"]]:
                    st.success(f"✅ Correct! {item['explain']}")
                    st.session_state[f"typeq_ok_{i}"] = True
                else:
                    st.error(f"❌ Not quite. {item['explain']}")
                    st.session_state[f"typeq_ok_{i}"] = False
    answered = sum(1 for i in range(len(questions)) if f"typeq_ok_{i}" in st.session_state)
    if answered == len(questions):
        correct = sum(1 for i in range(len(questions)) if st.session_state[f"typeq_ok_{i}"])
        st.markdown(f"**Score:** {score_pill(correct, len(questions))}", unsafe_allow_html=True)
        record_score("type_quiz", correct, len(questions))
        if correct == len(questions):
            st.balloons()


# ==============================================================================
# SLIDE 5 — BRANCH FLOW SIMULATOR
# ==============================================================================
def s_branch_sim():
    header(
        "Git Branch Flow Simulator",
        "Choose the right branch name, base branch, and PR target — get graded instantly",
        "SECTION 3",
    )

    st.markdown("#### Branch naming convention")
    st.dataframe(
        pd.DataFrame(
            [
                ["Feature", "feature/<issue-id>", "feature/1234"],
                ["Bug fix", "bugfix/<issue-id>", "bugfix/1234"],
            ],
            columns=["Branch Type", "Naming Convention", "Example"],
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("---")

    st.markdown("### 🎮 Scenario")
    st.info(
        "You've just been assigned **issue #4471** — a new loan report. "
        "Your team uses the standard promotion flow: **Working Branch → DEV → QA**. "
        "Decide how you'd branch, name it, and open the PR."
    )

    st.markdown("#### 🗺️ Available branches")
    c1, c2, c3, c4 = st.columns(4)
    branch_cards = [
        (c1, "origin/main", "Production, protected", "card-navy", "#0B3C5D"),
        (c2, "origin/dev", "Integration (latest)", "card-gold", "#8A6512"),
        (c3, "origin/qa", "QA testing", "card-navy", "#0B3C5D"),
        (c4, "feature/4001", "Stale local (3 wks)", "card-red", "#9B2C2C"),
    ]
    for col, name, sub, cls, colour in branch_cards:
        with col:
            st.markdown(
                f'<div class="card {cls}" style="text-align:center;padding:12px;">'
                f'<div style="font-weight:800;color:{colour};font-size:.9rem;">{name}</div>'
                f'<div style="font-size:.75rem;color:#5A7184;">{sub}</div>'
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### 🧩 Make your three decisions")

    c1, c2, c3 = st.columns(3)
    with c1:
        branch_name = st.text_input(
            "1️⃣ Branch name",
            placeholder="e.g. feature/1234",
            key="bs_name_input",
            help="Use the convention feature/<issue-id> or bugfix/<issue-id>.",
        )
        if branch_name.strip():
            if branch_name.strip() == "feature/4471":
                st.markdown('<div style="color:#1E8449;font-weight:700;font-size:.82rem;">✅ Correct naming convention</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#C0392B;font-weight:700;font-size:.82rem;">❌ Does not follow the convention</div>', unsafe_allow_html=True)

    with c2:
        base = st.selectbox(
            "2️⃣ Create working branch from…",
            ["— select —", "main", "dev", "qa", "feature/4001 (stale)"],
            index=0,
            key="bs_base_input",
        )
        if base != "— select —":
            if base == "dev":
                st.markdown('<div style="color:#1E8449;font-weight:700;font-size:.82rem;">✅ Latest approved base</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#C0392B;font-weight:700;font-size:.82rem;">❌ Not the correct base</div>', unsafe_allow_html=True)

    with c3:
        target = st.selectbox(
            "3️⃣ Initial PR targets…",
            ["— select —", "main", "dev", "qa"],
            index=0,
            key="bs_target_input",
        )
        if target != "— select —":
            if target == "dev":
                st.markdown('<div style="color:#1E8449;font-weight:700;font-size:.82rem;">✅ Correct PR target</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#C0392B;font-weight:700;font-size:.82rem;">❌ Wrong PR target</div>', unsafe_allow_html=True)

    if branch_name.strip() and base != "— select —" and target != "— select —":
        st.markdown("---")
        st.markdown("#### 🔎 Your chosen flow")
        st.markdown(
            vflow([base, branch_name.strip(), f"PR → {target}"], ["fbox-navy", "fbox-teal", "fbox-gold"]),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        grade = st.button("✅ Grade my choices", type="primary", use_container_width=True)
    with c2:
        reveal = st.button("🔑 Show correct answer", use_container_width=True)

    if grade:
        score = 0
        feedback = []
        if branch_name.strip() == "feature/4471":
            score += 1
            feedback.append(("success", "✅ **Branch name** — `feature/4471` follows the `feature/<issue-id>` convention."))
        else:
            feedback.append(("error", f"❌ **Branch name** — expected `feature/4471`, got `{branch_name.strip() or '—'}`."))

        if base == "dev":
            score += 2
            feedback.append(("success", "✅ **Base branch** — `dev` is the latest approved integration branch for feature work."))
        elif base == "main":
            feedback.append(("error", "❌ **Base branch** — `main` is production. Features must branch from the latest `dev`."))
        elif base == "qa":
            feedback.append(("error", "❌ **Base branch** — `qa` is a promotion target, not a source for feature branches."))
        elif base == "feature/4001 (stale)":
            feedback.append(("error", "❌ **Base branch** — never branch from a stale local branch. Run `git pull origin dev` first."))
        else:
            feedback.append(("warning", "⚠️ **Base branch** — pick one."))

        if target == "dev":
            score += 2
            feedback.append(("success", "✅ **PR target** — the initial PR must go to `dev`. Direct PRs to QA are prohibited."))
        elif target == "qa":
            feedback.append(("error", "❌ **PR target** — direct feature → QA merges are not permitted under the standard workflow."))
        elif target == "main":
            feedback.append(("error", "❌ **PR target** — `main` is not the initial PR target for features."))
        else:
            feedback.append(("warning", "⚠️ **PR target** — pick one."))

        record_score("branch_sim", score, 5)
        st.markdown(f"**Score:** {score_pill(score, 5)}", unsafe_allow_html=True)
        for kind, msg in feedback:
            getattr(st, kind)(msg)
        if score == 5:
            st.success("🏆 Perfect — you've mastered the branch workflow.")
            st.balloons()

    if reveal:
        st.markdown("---")
        st.markdown("### 🔑 Correct answers")
        kpi_row([("Branch name", "feature/4471"), ("Base branch", "dev"), ("Initial PR target", "dev")])
        st.markdown("#### ✅ Correct flow")
        st.markdown(
            vflow(["dev (pull latest)", "feature/4471", "PR → dev"], ["fbox-navy", "fbox-teal", "fbox-gold"]),
            unsafe_allow_html=True,
        )
        st.markdown("#### 📜 Exact Git commands")
        st.code(
            """# 1. Update dev and branch from it
git fetch origin
git checkout dev
git pull origin dev
git checkout -b feature/4471

# 2. Implement, then commit
git add .
git commit -m "feat(loan-report): add paginated loan report (#4471)"

# 3. Stay in sync with dev
git fetch origin
git rebase origin/dev

# 4. Run all checks before pushing
#    lint · type-check · build · tests · EXPLAIN ANALYZE if SQL changed

# 5. Push
git push -u origin feature/4471

# 6. Open PR on GitHub with:
#      base:    dev
#      compare: feature/4471""",
            language="bash",
        )

    st.markdown("---")
    st.markdown("### 🚀 Two-stage promotion: feature → dev → qa")
    st.caption("The feature PR stops at `dev`. A separate promotion PR later moves `dev` → `qa`.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Stage 1 — Feature merge**")
        st.markdown(hflow(["feature/4471", "dev"], gold_idx=(1,)), unsafe_allow_html=True)
        st.caption("Squash-merge after reviews and CI pass.")
    with c2:
        st.markdown("**Stage 2 — Release promotion**")
        st.markdown(hflow(["dev", "qa"], gold_idx=(1,)), unsafe_allow_html=True)
        st.caption("A separate batch PR promotes `dev` → `qa` when a release is ready.")
    st.error("**Never merge `feature/4471` directly into `qa`.** Only `dev` → `qa` promotions are permitted.")


# ==============================================================================
# SLIDE 6 — PR REVIEW SIMULATOR
# ==============================================================================
def s_pr_sim():
    header(
        "PR Review Simulator",
        "A teammate submitted a PR. Tick every requirement that this PR actually satisfies.",
        "SECTION 3.4",
    )
    st.markdown("### 📄 Sample PR")
    st.markdown(
        """
        <div class="pr-card">
        <div class="pr-title">PR #812 — "Quick loan export fix"</div>
        Target branch: <code>qa</code><br>
        Linked issue: <i>none</i><br><br>
        <b>Description:</b><br>
        fixed the export thing, should work now. tested locally 👌<br><br>
        <b>Files changed:</b> 14 files, +623 −482<br>
        <b>Checks:</b> ❌ lint failed · ⚠️ 3 TypeScript errors ignored with <code>as any</code><br>
        <b>Reviewers:</b> 0 approvals
        </div>
        """,
        unsafe_allow_html=True,
    )
    requirements = [
        ("Target the correct branch", False, "Targets `qa` — should be `dev`."),
        ("Reference the relevant issue or task", False, "No linked issue."),
        ("Clearly describe the implementation and its purpose", False, "Description is vague and informal."),
        ("Include sufficient testing details and evidence", False, "Only says 'tested locally' — no evidence."),
        ("Address relevant acceptance criteria", None, "Unclear — no AC mentioned."),
        ("Pass required automated and manual checks", False, "Lint failed; TypeScript errors bypassed."),
        ("Receive the required reviewer approvals", False, "0 approvals."),
        ("Contain no unresolved lint or TypeScript errors", False, "Lint failed and `as any` was used to bypass errors."),
    ]
    st.markdown("### ✅ Which requirements does this PR satisfy?")
    selected = set()
    cols = st.columns(2)
    for i, (req, _, _) in enumerate(requirements):
        with cols[i % 2]:
            if st.checkbox(req, key=f"pr_{i}"):
                selected.add(i)
    if st.button("🔍 Compare with correct answer", type="primary"):
        correct_indices = {i for i, (_, ok, _) in enumerate(requirements) if ok is True}
        user_correct = selected & correct_indices
        user_wrong = selected - correct_indices
        missed = correct_indices - selected
        score = len(user_correct)
        total = len(requirements)
        record_score("pr_sim", score, total)
        st.markdown(f"**Score:** {score_pill(score, total)}", unsafe_allow_html=True)
        st.markdown("#### Verdict on each requirement")
        for i, (req, ok, why) in enumerate(requirements):
            if ok is True:
                st.success(f"✅ **{req}** — {why or 'satisfied.'}")
            elif ok is False:
                st.error(f"❌ **{req}** — {why}")
            else:
                st.warning(f"⚠️ **{req}** — {why}")
        if user_wrong:
            st.info(f"You incorrectly marked **{len(user_wrong)}** item(s) as satisfied.")
        if missed:
            st.info(f"You missed **{len(missed)}** item(s) that were actually fine.")
        if score == total:
            st.balloons()


# ==============================================================================
# SLIDE 7 — DEVELOPER TESTING CHECKLIST
# ==============================================================================
def s_dev_checklist():
    header(
        "Developer Testing Checklist",
        "The pre-handover gate — tick every item, add notes, and track your progress",
        "SECTION 4",
    )
    items = [
        "All requirements and acceptance criteria have been reviewed",
        "The implementation satisfies the expected functionality",
        "Required field validations and error scenarios have been tested",
        "API requests and responses have been verified",
        "Database operations and returned data have been validated",
        "Relevant permissions and access restrictions have been tested",
        "Edge cases and regression scenarios have been considered",
        "Relevant automated tests have been executed",
        "Lint checks pass without outstanding errors introduced by the change",
        "TypeScript checks pass without outstanding errors introduced by the change",
        "The build completes successfully where applicable",
        "The code has been reviewed for maintainability and performance",
        "PR details, issue references, and testing evidence are provided",
        "Required reviews and approvals have been obtained before merging",
    ]
    st.markdown("### 4.1 Testing Before PR Creation")
    st.markdown(
        chips(
            [
                "Review requirements",
                "Understand business logic",
                "Test main functionality",
                "Verify validations & errors",
                "Check API req/res",
                "Validate DB operations",
                "Check permissions",
                "Test edge cases",
                "Run lint / type / build / test",
            ]
        ),
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 4.2 Interactive Checklist")
    c1, c2 = st.columns(2)
    done = 0
    for i, item in enumerate(items):
        with (c1 if i % 2 == 0 else c2):
            checked = st.checkbox(item, key=f"dev_ck_{i}", value=st.session_state.dev_checklist.get(i, False))
            st.session_state.dev_checklist[i] = checked
            if checked:
                done += 1
    total = len(items)
    st.progress(done / total)
    c1, c2, c3 = st.columns(3)
    c1.metric("Completed", f"{done} / {total}")
    c2.metric("Remaining", total - done)
    c3.metric("Status", "READY" if done == total else "IN PROGRESS")
    if done == total and not st.session_state.celebrated["dev"]:
        st.success("🎉 All checks passed — you're ready for PR and QA handover.")
        st.balloons()
        st.session_state.celebrated["dev"] = True
    record_score("dev_checklist", done, total)
    st.markdown("---")
    st.markdown("### 4.3 Evidence / Notes")
    st.session_state.dev_notes = st.text_area(
        "Paste test evidence, links, or notes (optional)",
        value=st.session_state.dev_notes,
        height=120,
        key="dev_notes_ta",
    )
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("🔄 Reset checklist", key="reset_dev"):
            st.session_state.dev_checklist = {}
            st.session_state.celebrated["dev"] = False
            st.rerun()
    with col_b:
        if done == total:
            st.download_button(
                "📥 Download evidence",
                data=f"Developer Testing Evidence\n\nCompleted: {done}/{total}\n\nNotes:\n{st.session_state.dev_notes}",
                file_name="dev_testing_evidence.txt",
                mime="text/plain",
            )
    st.error("**Do not rely on QA to discover defects that could reasonably have been identified during development.**")


# ==============================================================================
# SLIDE 8 — SQL PLAYGROUND
# ==============================================================================
def s_sql_playground():
    header(
        "SQL Performance — Plan Inspector & A/B Quiz",
        "Read execution plans, spot red flags, and pick the faster query",
        "SECTION 5 & 6",
    )
    tab1, tab2 = st.tabs(["🔎 Plan Inspector", "⚡ A/B Query Comparison"])
    with tab1:
        st.markdown("### 5.1 Analyze Query Execution Plans")
        queries = {
            "Loan list — offset pagination": {
                "sql": "SELECT id, customer_id, balance FROM loans ORDER BY created_at DESC LIMIT 20 OFFSET 500000;",
                "plan": [
                    ("type", "ALL"),
                    ("possible_keys", "idx_created_at"),
                    ("key", "NULL"),
                    ("rows", "2,847,312"),
                    ("Extra", "Using filesort"),
                ],
                "issues": [
                    "Full table scan (`type: ALL`) — index not being used.",
                    "`OFFSET 500000` forces the DB to scan and discard 500k rows.",
                    "`Using filesort` — sorting 2.8M rows in memory.",
                ],
                "fix": "Use keyset pagination (WHERE created_at < :last_seen), and force index usage for the ORDER BY + LIMIT.",
            },
            "Loan summary — aggregated per branch": {
                "sql": "SELECT b.name, COUNT(*) c, SUM(l.balance) total FROM loans l JOIN branches b ON b.id = l.branch_id GROUP BY b.id;",
                "plan": [
                    ("type", "ALL (l) / eq_ref (b)"),
                    ("key", "NULL / PRIMARY"),
                    ("rows", "2,847,312"),
                    ("Extra", "Using temporary; Using filesort"),
                ],
                "issues": [
                    "Full scan on `loans` — no usable index for the join or group.",
                    "`Using temporary` — GROUP BY spilling to disk.",
                    "No filtering — aggregates the entire loans table.",
                ],
                "fix": "Add an index on `loans(branch_id)`, consider a covering index `(branch_id, balance)`, and pre-aggregate via a summary table for large volumes.",
            },
            "Customer statement — filtered by customer": {
                "sql": "SELECT t.* FROM transactions t WHERE t.customer_id = ? AND t.txn_date BETWEEN ? AND ? ORDER BY t.txn_date DESC;",
                "plan": [
                    ("type", "range"),
                    ("key", "idx_customer_date"),
                    ("rows", "412"),
                    ("Extra", "Using index condition"),
                ],
                "issues": [],
                "fix": "This is healthy — it uses the composite index `(customer_id, txn_date)` and a range scan on 412 rows.",
            },
        }
        choice = st.selectbox("Pick a query to inspect", list(queries.keys()), key="plan_choice")
        q = queries[choice]
        st.markdown("**SQL**")
        st.code(q["sql"], language="sql")
        st.markdown("**Simulated execution plan**")
        st.dataframe(pd.DataFrame(q["plan"], columns=["Attribute", "Value"]), hide_index=True, use_container_width=True)
        st.markdown("**What do you notice?**")
        if q["issues"]:
            st.error("🔴 Red flags detected")
            for issue in q["issues"]:
                st.markdown(f"- {issue}")
            st.info(f"**Suggested fix:** {q['fix']}")
        else:
            st.success("🟢 This plan is healthy — index used, range scan, small row count.")
            st.info(f"**Why it's good:** {q['fix']}")
        st.markdown("---")
        st.markdown("#### 5.3 Recommended test data size for performance analysis")
        records = st.slider("How many dummy records should you prepare for a meaningful performance test?", 0, 10000, 1000, step=500)
        if 2000 <= records <= 3000:
            st.success(f"✅ {records:,} — right in the recommended band (2,000–3,000).")
        elif records < 2000:
            st.warning(f"⚠️ {records:,} may not be enough for meaningful performance analysis. Target 2,000–3,000.")
        else:
            st.info(f"ℹ️ {records:,} is generous — fine, but larger datasets or load testing may be required for high-volume queries.")

    with tab2:
        st.markdown("### 6.1 Which query is faster for large datasets?")
        st.caption("Same business result — very different data retrieval strategy.")
        pairs = [
            {
                "name": "Loan list endpoint — 100 rows, large table",
                "a": (
                    "TypeORM QueryBuilder with .leftJoinAndSelect()",
                    """const loans = await repo
  .createQueryBuilder('loan')
  .leftJoinAndSelect('loan.customer', 'customer')
  .leftJoinAndSelect('loan.branch', 'branch')
  .leftJoinAndSelect('loan.product', 'product')
  .getMany();""",
                ),
                "b": (
                    "Raw SQL — select only needed columns",
                    """SELECT l.id, l.balance, l.status,
       c.name AS customer_name
FROM loans l
JOIN customers c ON c.id = l.customer_id
WHERE l.status = 'active'
ORDER BY l.created_at DESC
LIMIT 100;""",
                ),
                "winner": "B",
                "explain": "Raw SQL retrieves only the required columns with controlled joins and LIMIT. TypeORM eager-loading hydrates complete entities across multiple joins — far more data than needed.",
            },
            {
                "name": "Monthly interest report",
                "a": (
                    "Fetch all rows, aggregate in application",
                    """const all = await repo.find();
const byBranch = {};
for (const r of all) {
  byBranch[r.branchId] = (byBranch[r.branchId] || 0) + r.interest;
}"""
                ),
                "b": (
                    "Database-side aggregation",
                    """SELECT branch_id, SUM(interest) AS total
FROM loans
WHERE txn_date BETWEEN :start AND :end
GROUP BY branch_id;"""
                ),
                "winner": "B",
                "explain": "Aggregate in the database. Fetching all rows to sum them in the application transfers massive amounts of data unnecessarily.",
            },
        ]
        for i, pair in enumerate(pairs):
            st.markdown(f"#### Q{i+1}. {pair['name']}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Option A** — " + pair["a"][0])
                st.code(pair["a"][1], language="typescript" if "await" in pair["a"][1] else "sql")
            with c2:
                st.markdown("**Option B** — " + pair["b"][0])
                st.code(pair["b"][1], language="sql")
            choice = st.radio("Which is faster?", ["A", "B"], index=None, key=f"ab_{i}", horizontal=True, label_visibility="collapsed")
            if st.button("Check", key=f"ab_btn_{i}"):
                if choice == pair["winner"]:
                    st.success(f"✅ Correct! {pair['explain']}")
                    st.session_state[f"ab_ok_{i}"] = True
                elif choice:
                    st.error(f"❌ Not quite. {pair['explain']}")
                    st.session_state[f"ab_ok_{i}"] = False
                else:
                    st.warning("Pick an option.")
        answered = sum(1 for i in range(len(pairs)) if f"ab_ok_{i}" in st.session_state)
        if answered == len(pairs):
            correct = sum(1 for i in range(len(pairs)) if st.session_state[f"ab_ok_{i}"])
            st.markdown(f"**Score:** {score_pill(correct, len(pairs))}", unsafe_allow_html=True)
            record_score("sql_ab", correct, len(pairs))


# ==============================================================================
# SLIDE 9 — REAL PR REVIEW
# ==============================================================================
def s_review_game():
    header(
        "Code Review — Real PR Edition",
        "Compare a non-compliant PR against your compliant PawningAuctioneer service",
        "SECTION 7",
    )

    st.markdown("### 📋 Business context")
    st.info(
        "**Feature:** `retrievePawnAuctioneers` — paginated auctioneer list with search across "
        "name / NIC / company / license. Both implementations return the same data. "
        "**One complies with every Developer Standard; the other violates eight.** "
        "Your job as reviewer: identify every violation in the non-compliant PR."
    )

    BAD_CODE = '''// services/pawning-auctioneer.service.ts   <-- Non-compliant PR
import Context from '@common/context'
import Decimal from 'decimal.js'

export default class PawningAuctioneerService {
  constructor(private context: Context) {}

  public async retrievePawnAuctioneers(params: any): Promise<any> {
    const search = params.search || ''

    const auctioneers = await this.context.queryRunner.query(
      `SELECT * FROM pw_auctioneers a
       WHERE a.name LIKE '%${search}%'
          OR a.nic LIKE '%${search}%'
          OR a.company_name LIKE '%${search}%'
          OR a.license_number LIKE '%${search}%'
       ORDER BY a.created_at DESC`
    )

    const result: any[] = []
    for (const row of auctioneers) {
      const detail = await this.context.queryRunner.query(
        `SELECT * FROM pw_auction_events WHERE auctioneer_id = ${row.id}`
      )
      result.push({
        ...row,
        auctionEvents: detail,
        balance: new Decimal(row.balance || 0).toNumber()
      })
    }
    return result
  }

  public async retrievePawnAuctioneer(id: any): Promise<any> {
    const result: any = await this.context.queryRunner.query(
      `SELECT * FROM pw_auctioneers WHERE id = ${id}`
    )
    return result[0]
  }
}
'''

    GOOD_CODE = '''// services/PawningAuctioneerReadPlatformService.ts   <-- Compliant version
import Context from '@common/context'
import { withOptionalCheckBigInt, withOptionalCheckDecimal } from '@common/withOptionalCheck'
import Decimal from 'decimal.js'

import PawnAuctioneerData from '../data/PawnAuctioneerData'
import PawnAuctioneerNotFoundException from '../exception/PawnAuctioneerNotFoundException'

export interface ListPawningAuctioneerParams {
  offset?: number
  limit?: number
  search?: string
}

interface PawningAuctioneerRow {
  id: bigint
  name: string
  nic: string
  license_number: string
  license_expiry_date: Date
  company_name: string
  business_registration_number: string
  contact_number: string
  email: string
  account_holder_name: string
  tax_identification_number: string
  bank_name: string
  bank_account_number: string
  bank_branch: string
  status: string
  created_by: bigint
  created_at: Date
  updated_by: bigint
  updated_at: Date
  auction_event_id: string
  auction_date: Date
  location: string
  total_assign_items: number
  total_sell_items: number
  auctioneer_commission_charge: Decimal
  auction_event_status: string
}

export default class PawningAuctioneerReadPlatformService {
  private readonly context: Context

  constructor(context: Context) {
    this.context = context
  }

  static PawningAuctioneer = class {
    public schema: string
    public query: string

    constructor() {
      this.schema = `
        a.id, a.name, a.nic, a.license_number, a.license_expiry_date,
        a.company_name, a.business_registration_number, a.contact_number,
        a.email, a.account_holder_name, a.tax_identification_number,
        a.bank_name, a.bank_account_number, a.bank_branch, a.status,
        a.created_by, a.created_at, a.updated_by, a.updated_at
      FROM pw_auctioneers a
      `
      this.query = `
        ae.auction_event_id AS auction_event_id,
        ae.auction_date AS auction_date,
        ae.location_address AS location,
        COUNT(aea.id) AS total_assign_items,
        SUM(CASE WHEN aea.article_status = 'SOLD' THEN 1 ELSE 0 END) AS total_sell_items,
        c.commission_amount AS auctioneer_commission_charge,
        ae.status AS auction_event_status
    FROM pw_auction_events ae
    LEFT JOIN pw_auction_event_articles aea ON aea.auction_event_id = ae.id
    LEFT JOIN pw_auction_event_charges  c   ON c.auction_event_id   = ae.id
      `
    }

    mapRow(row: PawningAuctioneerRow) {
      return new PawnAuctioneerData({ /* fully typed */ } as any)
    }
  }

  public async retrievePawnAuctioneers(
    params: ListPawningAuctioneerParams
  ): Promise<{ data: PawnAuctioneerData[]; total: number }> {
    const { limit, offset, search } = params
    const Mapper = new PawningAuctioneerReadPlatformService.PawningAuctioneer()
    const searchFilter = `%${search ?? ''}%`

    const countQuery = `
      SELECT COUNT(*) AS count FROM pw_auctioneers a
      WHERE (a.name LIKE ? OR a.nic LIKE ? OR a.company_name LIKE ? OR a.license_number LIKE ?)
    `
    const countResult = (await this.context.queryRunner.query(countQuery, [
      searchFilter, searchFilter, searchFilter, searchFilter,
    ])) as { count: number }[]
    const total = Number(countResult[0]?.count ?? 0)

    let sql = `
      SELECT ${Mapper.schema}
      WHERE (a.name LIKE ? OR a.nic LIKE ? OR a.company_name LIKE ? OR a.license_number LIKE ?)
      ORDER BY a.created_at DESC
    `
    const paramsArray: any[] = [searchFilter, searchFilter, searchFilter, searchFilter]
    if (limit  !== undefined) { sql += ` LIMIT ?`;  paramsArray.push(limit) }
    if (offset !== undefined) { sql += ` OFFSET ?`; paramsArray.push(offset) }

    const rows = (await this.context.queryRunner.query(sql, paramsArray)) as PawningAuctioneerRow[]
    return { data: rows.map((row) => Mapper.mapRow(row)), total }
  }

  public async retrievePawnAuctioneer(auctioneerId: bigint): Promise<PawnAuctioneerData> {
    try {
      const Mapper = new PawningAuctioneerReadPlatformService.PawningAuctioneer()
      const query = `SELECT ${Mapper.schema} WHERE a.id = ?`
      const result = (await this.context.queryRunner.query(query, [auctioneerId])) as PawningAuctioneerRow[]
      return Mapper.mapRow(result[0])
    } catch (error) {
      throw new PawnAuctioneerNotFoundException(auctioneerId)
    }
  }
}
'''

    tab1, tab2, tab3 = st.tabs([
        "❌ Non-compliant PR (review this)",
        "✅ Compliant version (reference)",
        "🎯 Spot the violations",
    ])

    with tab1:
        st.markdown("### Reviewer's inbox")
        st.markdown(
            """
            <div class="pr-card" style="margin-bottom:14px;">
            <div class="pr-title">PR #1104 — "Add auctioneer listing endpoint"</div>
            <span class="pr-badge badge-red">❌ Lint failed</span>
            <span class="pr-badge badge-red">❌ TS errors suppressed</span>
            <span class="pr-badge badge-gold">⚠️ 0 approvals</span>
            <span class="pr-badge badge-navy">Target: dev</span>
            <br><br>
            <b>Author comment:</b> <i>"Works locally. Bigger PR than expected — but returns the data."</i>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.code(BAD_CODE, language="typescript")

    with tab2:
        st.markdown("### The compliant version — real production code")
        st.success(
            "This is the approach that meets every Developer Standard: "
            "typed rows, parameterised queries, explicit column selection, "
            "separate COUNT query, bounded pagination, domain exception, "
            "raw SQL for performance (as required by Section 6.1 for large datasets)."
        )
        st.code(GOOD_CODE, language="typescript")

    with tab3:
        st.markdown("### 🎯 Which violations does the non-compliant PR have?")
        st.caption(
            "Tick every real violation. **Beware of traps** — some patterns in the bad PR "
            "are actually *compliant* with the standards (e.g., using raw SQL)."
        )

        violations = [
            ("Uses `any` for params and return types (`params: any`, `Promise<any>`)",
             True,
             "Section 2.1 — no typed input/output contract. Correct: use `ListPawningAuctioneerParams` and a typed return."),
            ("SQL injection risk via string interpolation (`'%${search}%'`, `= ${row.id}`, `= ${id}`)",
             True,
             "Security violation. Correct: use parameterised queries with `?` placeholders."),
            ("Uses `SELECT *` on `pw_auctioneers` — retrieves every column",
             True,
             "Section 6.2 — retrieve only the required columns. Correct: list the columns explicitly via a mapper schema."),
            ("N+1 query loop — one query per auctioneer inside a `for` loop",
             True,
             "Section 6.2 — avoid excessive data retrieval. Correct: a single JOIN or a batched `IN (...)` query."),
            ("No error handling on `retrievePawnAuctioneer` — no domain-specific exception",
             True,
             "Section 4.1 — verify error scenarios. Correct: `try/catch` + `throw new PawnAuctioneerNotFoundException(id)`."),
            ("No pagination enforcement — `limit` / `offset` are ignored, unbounded result set",
             True,
             "Section 6.2 — bound large result sets. Correct: `LIMIT ?` / `OFFSET ?` parameters plus a COUNT query."),
            ("Decimal precision lost via `new Decimal(...).toNumber()`",
             True,
             "Correct: keep it as Decimal and pass through `withOptionalCheckDecimal` — never cast Decimal to number."),
            ("No typed row interface or mapper — bypasses `withOptionalCheckBigInt` / `withOptionalCheckDecimal`",
             True,
             "Section 2.1 — define `PawningAuctioneerRow`, and map with the standard type-safe helpers."),
            ("Uses raw MySQL queries instead of an ORM (TypeORM repository)",
             False,
             "✅ **Compliant** — Section 6.1 explicitly prefers raw SQL for performance-sensitive queries."),
            ("Uses a class-based service with dependency injection for the Context",
             False,
             "✅ **Compliant** — this pattern is fine and matches the compliant version."),
            ("Adds `ORDER BY a.created_at DESC` to the query",
             False,
             "✅ **Compliant** — correct business logic. The compliant version does this too."),
        ]

        selected = set()
        cols = st.columns(2)
        for i, (text, _, _) in enumerate(violations):
            with cols[i % 2]:
                if st.checkbox(text, key=f"rev_{i}"):
                    selected.add(i)

        if st.button("🔍 Reveal reviewer verdict", type="primary"):
            real = {i for i, (_, is_v, _) in enumerate(violations) if is_v}
            hits = selected & real
            false_positives = selected - real
            missed = real - selected

            st.markdown("#### Verdict on each item")
            for i, (text, is_v, why) in enumerate(violations):
                if is_v:
                    st.error(f"🔴 **{text}**\n\n{why}")
                else:
                    st.success(f"🟢 **{text}**\n\n{why}")

            score = max(0, len(hits) - len(false_positives))
            total = len(real)
            record_score("review_game", score, total)

            st.markdown(f"**Score:** {score_pill(score, total)}", unsafe_allow_html=True)
            if false_positives:
                st.warning(
                    f"⚠️ You flagged **{len(false_positives)}** compliant item(s) as violations — "
                    "reviewers must be precise, not trigger-happy."
                )
            if missed:
                st.info(f"ℹ️ You missed **{len(missed)}** real violation(s).")

            if score == total and not false_positives:
                st.success("🏆 Perfect review — no false positives, no missed issues.")
                st.balloons()

        st.markdown("---")
        st.markdown("#### 💡 Reviewer's summary")
        st.markdown(
            """
            <div class="dont-box">
            <h5>⛔ Reject — this PR violates</h5>
            <ul>
                <li>Section 2.1 — Type safety (`any` everywhere)</li>
                <li>Section 6.2 — Excessive data retrieval (`SELECT *`, N+1)</li>
                <li>Section 4.1 — Missing error handling</li>
                <li>Section 6.2 — No pagination bounds</li>
                <li>Security — SQL injection via string interpolation</li>
            </ul>
            </div>
            <div class="do-box">
            <h5>✅ Request changes — point the author to</h5>
            <ul>
                <li><code>PawningAuctioneerReadPlatformService.ts</code> as the reference implementation</li>
                <li>Parameterised queries (<code>?</code> placeholders)</li>
                <li>Typed row interface + <code>withOptionalCheckBigInt</code> / <code>withOptionalCheckDecimal</code></li>
                <li>Explicit column selection through the mapper <code>schema</code></li>
                <li><code>LIMIT ?</code> / <code>OFFSET ?</code> with a separate COUNT query</li>
                <li><code>PawnAuctioneerNotFoundException</code> on miss</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# SLIDE 10 — FAILURE TRIAGE
# ==============================================================================
def s_triage():
    header(
        "Automated Testing — Failure Triage",
        "A test fails on staging. What do you do?",
        "SECTION 8",
    )
    st.markdown(
        vflow(
            [
                "Automated test fails",
                "Investigate & identify root cause",
                "Is it implementation / test / config / env?",
                "Fix underlying problem",
                "Rerun relevant tests",
                "Verify no regressions introduced",
                "Suite passes → proceed",
            ],
            ["fbox-red", "fbox-light", "fbox-light", "fbox-light", "fbox-light", "fbox-teal", "fbox-gold"],
        ),
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🎮 Scenario")
    st.info(
        "Your integration test `LoanService.getLoanDetails` failed on staging with a timeout after 30 seconds. "
        "The same test passed locally. The staging database has 2.8M loan rows. "
        "**What is the most appropriate next step?**"
    )
    options = [
        "Increase the test timeout to 120 seconds and re-run.",
        "Ignore it — staging is flaky, QA will rerun.",
        "Profile the query with EXPLAIN ANALYZE on staging data and look for a missing index or full scan.",
        "Open a ticket for QA and move on to the next task.",
        "Disable the test until someone else looks at it.",
    ]
    choice = st.radio("Choose one:", options, index=None, key="triage_choice")
    if st.button("Submit answer", type="primary"):
        if choice is None:
            st.warning("Pick an option first.")
        elif choice == options[2]:
            st.success(
                "✅ Correct! The failure is almost certainly a **performance issue masked by small local data**. "
                "Analyze the plan on realistic staging data, add/fix the index, then re-run."
            )
            record_score("triage", 1, 1)
            st.balloons()
        elif choice == options[0]:
            st.error("❌ Increasing the timeout treats a symptom, not the cause. Investigate first.")
            record_score("triage", 0, 1)
        elif choice in (options[1], options[3]):
            st.error("❌ **Developers own their failures.** Handing to QA is not acceptable.")
            record_score("triage", 0, 1)
        elif choice == options[4]:
            st.error("❌ Disabling tests is never the correct response to a real failure.")
            record_score("triage", 0, 1)


# ==============================================================================
# SLIDE 11 — ORDER THE WORKFLOW
# ==============================================================================
def s_workflow_game():
    header(
        "Order the Development Workflow",
        "Click the 8 steps in the correct order. You'll be graded when all are selected.",
        "SECTION 9",
    )
    STEPS = [
        "Requirement Analysis",
        "Branch Preparation",
        "Implementation",
        "Developer Validation",
        "Pull Request to DEV",
        "Merge to DEV",
        "QA Promotion",
        "Automated Testing & Staging",
    ]
    DISPLAY_ORDER = [3, 0, 6, 2, 7, 1, 5, 4]
    st.markdown("### Click the steps in the correct sequence")
    cols = st.columns(2)
    for pos, step_idx in enumerate(DISPLAY_ORDER):
        with cols[pos % 2]:
            already = step_idx in st.session_state.wf_clicked
            label = f"✓ {STEPS[step_idx]}" if already else STEPS[step_idx]
            if st.button(
                label,
                key=f"wf_btn_{step_idx}",
                use_container_width=True,
                disabled=already,
                type="primary" if already else "secondary",
            ):
                st.session_state.wf_clicked.append(step_idx)
                st.rerun()
    st.markdown("---")
    if st.session_state.wf_clicked:
        st.markdown("#### Your order so far")
        sequence = " → ".join(STEPS[i] for i in st.session_state.wf_clicked)
        st.markdown(f"**{sequence}**")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔄 Reset order"):
            st.session_state.wf_clicked = []
            st.rerun()
    if len(st.session_state.wf_clicked) == len(STEPS):
        correct = st.session_state.wf_clicked == list(range(len(STEPS)))
        score = sum(1 for i, v in enumerate(st.session_state.wf_clicked) if v == i)
        record_score("workflow_order", score, len(STEPS))
        if correct:
            st.success("🏆 Perfect order! You've mastered the workflow.")
            st.balloons()
        else:
            st.warning("⚠️ Not quite. Here's the correct order:")
            st.markdown(
                vflow(
                    [f"{i+1}. {s}" for i, s in enumerate(STEPS)],
                    ["fbox-navy"] + ["fbox-light"] * 6 + ["fbox-gold"],
                ),
                unsafe_allow_html=True,
            )
        st.markdown(f"**Score:** {score_pill(score, len(STEPS))}", unsafe_allow_html=True)


# ==============================================================================
# SLIDE 12 — SCENARIO SIMULATOR
# ==============================================================================
def s_scenarios():
    header(
        "Developer Accountability — Scenario Simulator",
        "Real situations. Pick what you'd actually do.",
        "SECTION 10",
    )
    scenarios = [
        {
            "title": "Scenario 1 — Deadline pressure",
            "desc": "It's 4pm Friday. Your branch has 2 lint warnings and 1 TypeScript error. The lead says 'just merge it, we'll fix Monday.' What do you do?",
            "options": [
                "Merge now — the deadline matters more.",
                "Add `// @ts-ignore` and `eslint-disable` to make it pass, then merge.",
                "Fix the warnings and type error, then merge — even if it means delaying by an hour.",
                "Push to QA directly to skip the DEV gate.",
            ],
            "correct": 2,
            "explain": "Lint and TypeScript errors introduced by your change must be resolved before merging. Deadlines do not justify bypassing required checks.",
        },
        {
            "title": "Scenario 2 — QA catches a bug you should have found",
            "desc": "QA reports that the export button fails when a customer has no transactions. Your response?",
            "options": [
                "Reply 'works on my machine' and ask them to retest.",
                "Fix it, then add a test that would have caught this, and re-do your self-testing checklist.",
                "File a new bug and let QA handle the fix priority.",
                "Blame the requirements for not mentioning this case.",
            ],
            "correct": 1,
            "explain": "Own the defect. Fix it, add regression coverage, and strengthen your own pre-handover testing so the same class of issue doesn't recur.",
        },
        {
            "title": "Scenario 3 — Performance-sensitive query",
            "desc": "You wrote a report query that runs in 200ms on dev with 500 rows. Staging has 3 million rows. What do you do before opening the PR?",
            "options": [
                "Ship it — 200ms is fine, staging is just slow.",
                "Add a cache layer and hope for the best.",
                "Run EXPLAIN ANALYZE with 2,000–3,000 representative rows, attach the evidence to the issue, and fix any bottlenecks.",
                "Move the aggregation to the application layer so the DB does less work.",
            ],
            "correct": 2,
            "explain": "Performance must be validated with realistic data. Attach the plan and query results to the issue as evidence.",
        },
        {
            "title": "Scenario 4 — Branching shortcut",
            "desc": "You've fixed an urgent bug. QA is asking for it 'now'. What branch do you open the PR against?",
            "options": [
                "qa — QA asked for it, so it's fine.",
                "main — it's urgent, main is fastest.",
                "dev — follow the standard flow. Exceptional/hotfix releases use the separately authorized process.",
                "Whatever branch is currently checked out.",
            ],
            "correct": 2,
            "explain": "Direct feature/bugfix → QA merges are not permitted. Hotfix/release exceptions must follow the separately authorized process.",
        },
    ]
    for i, sc in enumerate(scenarios):
        st.markdown(f"### {sc['title']}")
        st.info(sc["desc"])
        choice = st.radio("Your action", sc["options"], index=None, key=f"sc_{i}", label_visibility="collapsed")
        if st.button("Submit", key=f"sc_btn_{i}"):
            if choice is None:
                st.warning("Pick an option first.")
            elif sc["options"].index(choice) == sc["correct"]:
                st.success(f"✅ Correct. {sc['explain']}")
                st.session_state.scenario_state[i] = True
            else:
                st.error(f"❌ {sc['explain']}")
                st.session_state.scenario_state[i] = False
        st.markdown("---")
    answered = len(st.session_state.scenario_state)
    if answered == len(scenarios):
        correct = sum(1 for v in st.session_state.scenario_state.values() if v)
        st.markdown(f"**Score:** {score_pill(correct, len(scenarios))}", unsafe_allow_html=True)
        record_score("scenarios", correct, len(scenarios))
        if correct == len(scenarios):
            st.balloons()
    st.markdown(
        """
        <div class="dont-box">
        <h5>⛔ Never acceptable</h5>
        <ul>
            <li>Using <code>any</code> unnecessarily to bypass type safety</li>
            <li>Creating branches from outdated base branches</li>
            <li>Sending the initial PR directly to QA</li>
            <li>Merging without required approvals</li>
            <li>Skipping developer testing or acceptance-criteria verification</li>
            <li>Leaving avoidable lint or TypeScript errors unresolved</li>
            <li>Ignoring query performance on large datasets</li>
            <li>Treating QA as the first stage of meaningful testing</li>
            <li>Ignoring automated test failures or bypassing required checks</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# SLIDE 13 — FINAL COMPLIANCE CHECKLIST
# ==============================================================================
def s_final_checklist():
    header(
        "Final Compliance Checklist",
        "The gate before you say 'ready for QA' — tick all items, add notes, celebrate.",
        "SECTION 11",
    )
    items = [
        "Requirements and acceptance criteria are understood and implemented",
        "Correct feature/bugfix branch naming convention is used",
        "Working branch was created from the latest base branch",
        "TypeScript types are appropriate and unnecessary `any` types removed",
        "Relevant SQL queries have been analyzed and optimized",
        "Performance evidence added to the relevant Git issue",
        "Sufficient test data has been prepared when needed",
        "Developer testing is complete and documented",
        "Lint, TypeScript, build, and applicable test checks pass",
        "Initial PR targeted DEV and received required approvals",
        "All review comments and identified issues resolved",
        "QA promotion follows the established PR and deployment process",
        "Automated testing and staging readiness requirements satisfied",
    ]
    c1, c2 = st.columns(2)
    done = 0
    for i, item in enumerate(items):
        with (c1 if i % 2 == 0 else c2):
            checked = st.checkbox(item, key=f"final_ck_{i}", value=st.session_state.final_checklist.get(i, False))
            st.session_state.final_checklist[i] = checked
            if checked:
                done += 1
    total = len(items)
    st.progress(done / total)
    c1, c2, c3 = st.columns(3)
    c1.metric("Completed", f"{done} / {total}")
    c2.metric("Remaining", total - done)
    c3.metric("Status", "READY" if done == total else "IN PROGRESS")
    if done == total and not st.session_state.celebrated["final"]:
        st.success("🎉 All compliance checks passed — task is fully ready for QA.")
        st.balloons()
        st.session_state.celebrated["final"] = True
    record_score("final_checklist", done, total)
    st.markdown("---")
    st.markdown("### Additional notes")
    st.session_state.final_notes = st.text_area(
        "Anything blocking full compliance?",
        value=st.session_state.final_notes,
        height=100,
        key="final_notes_ta",
    )
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Reset checklist", key="reset_final"):
            st.session_state.final_checklist = {}
            st.session_state.celebrated["final"] = False
            st.rerun()
    with col_b:
        summary = f"""Final Compliance Checklist
Completed: {done}/{total}

Items checked:
""" + "\n".join(f"- [x] {items[i]}" for i in range(total) if st.session_state.final_checklist.get(i, False)) + f"""

Notes:
{st.session_state.final_notes}
"""
        st.download_button("📥 Download summary", data=summary, file_name="compliance_summary.txt", mime="text/plain")


# ==============================================================================
# SLIDE 14 — PROGRESS DASHBOARD
# ==============================================================================
def s_dashboard():
    header(
        "Your Progress Dashboard",
        "Every interactive activity is scored — see how you did",
        "SUMMARY",
    )
    activities = [
        ("warmup", "Purpose warm-up"),
        ("type_detective", "Type Detective"),
        ("type_quiz", "Type Safety Quiz"),
        ("branch_sim", "Branch Flow Simulator"),
        ("pr_sim", "PR Review Simulator"),
        ("dev_checklist", "Developer Testing Checklist"),
        ("sql_ab", "SQL A/B Quiz"),
        ("review_game", "Real PR Review"),
        ("triage", "Failure Triage"),
        ("workflow_order", "Order the Workflow"),
        ("scenarios", "Scenario Simulator"),
        ("final_checklist", "Final Compliance Checklist"),
        ("exam", "🎓 Final Exam"),
    ]
    rows = []
    for key, label in activities:
        s = st.session_state.scores.get(key)
        if s:
            pct = s["value"] / s["total"] * 100 if s["total"] else 0
            rows.append({
                "Activity": label,
                "Score": f"{s['value']} / {s['total']}",
                "Percent": round(pct, 1),
                "Status": "✅ Pass" if pct >= 80 else ("⚠️ Partial" if pct > 0 else "❌ Low"),
            })
        else:
            rows.append({"Activity": label, "Score": "—", "Percent": 0.0, "Status": "⏳ Not started"})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    earned, possible = total_score()
    pct = earned / possible * 100 if possible else 0
    kpi_row(
        [
            ("Total Score", f"{earned} / {possible}"),
            ("Overall %", f"{pct:.1f}%"),
            ("Activities Done", f"{sum(1 for r in rows if r['Score'] != '—')} / {len(activities)}"),
            ("Grade", "A" if pct >= 90 else "B" if pct >= 75 else "C" if pct >= 60 else "D" if pct >= 40 else "—"),
        ]
    )
    if pct >= 90:
        st.success("🏆 Outstanding. You know the standards inside out.")
        st.balloons()
    elif pct >= 70:
        st.info("👍 Solid. Revisit any activity under 80% to lock it in.")
    elif pct > 0:
        st.warning("📚 Keep going — revisit the slides that have unfinished or low-scoring activities.")
    else:
        st.info("👋 Start with the sidebar or click **Next** — every activity contributes to this dashboard.")

    st.markdown("---")
    st.markdown("#### Exam status")
    if st.session_state.exam_submitted:
        total_q = len(st.session_state.exam_results)
        ex = st.session_state.exam_score
        ex_pct = ex / total_q * 100 if total_q else 0
        pass_mark_pct = int(_active_pass_mark() * 100)
        st.markdown(
            f'<div class="kpi"><div class="v">{ex} / {total_q}</div>'
            f'<div class="l">Final Exam — {"PASSED" if ex_pct >= pass_mark_pct else "NOT PASSED"} ({ex_pct:.0f}%)</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("You have not taken the final exam yet. Open the **Final Exam** slide in the sidebar when you are ready.")

    st.markdown("---")
    st.markdown("#### Overall progress")
    st.progress(min(pct / 100, 1.0))
    if st.button("🔄 Reset all scores and progress", type="secondary"):
        st.session_state.scores = {}
        st.session_state.dev_checklist = {}
        st.session_state.final_checklist = {}
        st.session_state.wf_clicked = []
        st.session_state.scenario_state = {}
        st.session_state.pr_selected = set()
        st.session_state.review_selected = set()
        st.session_state.celebrated = {"dev": False, "final": False}
        _reset_exam()
        st.rerun()


# ==============================================================================
# SLIDE 15 — FINAL MESSAGE
# ==============================================================================
def s_final():
    st.markdown(
        """
        <div class="hero" style="padding:44px 40px;">
            <div class="hero-kicker">Final Note</div>
            <div class="hero-title" style="font-size:2.15rem;">Standards are mandatory —<br>not optional.</div>
            <div class="hero-sub">Own implementation quality, testing, performance, and review readiness before handing over a task.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1.1, 1])
    with c1:
        card(
            "Our objective",
            "Identify problems early, reduce avoidable defects, minimise QA rework, and deliver reliable "
            "features on time.",
            "card-gold",
        )
        card(
            "Every developer must",
            "Take ownership of <b>implementation quality</b>, <b>testing</b>, <b>performance</b>, and "
            "<b>review readiness</b> before handing over a task.",
        )
    with c2:
        st.markdown("#### The complete delivery journey")
        st.markdown(
            vflow(
                ["PLAN", "BRANCH", "IMPLEMENT", "SELF-TEST", "PR → DEV", "REVIEW", "QA", "AUTOMATED TEST"],
                ["fbox-navy", "fbox-light", "fbox-light", "fbox-teal", "fbox-teal", "fbox-gold", "fbox-gold", "fbox-red"],
            ),
            unsafe_allow_html=True,
        )
    st.markdown("---")
    earned, possible = total_score()
    pct = earned / possible * 100 if possible else 0
    kpi_row(
        [
            ("Exam Sets", str(len(st.session_state.exam_bank or {}))),
            ("Your Score", f"{earned} / {possible}"),
            ("Completion", f"{pct:.0f}%"),
        ]
    )
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎓 Go to the Final Exam", type="primary", use_container_width=True):
            st.session_state.slide = next(i for i, (t, _) in enumerate(SLIDES) if t.startswith("13."))
            st.rerun()
    with c2:
        if st.button("📊 View my dashboard", use_container_width=True):
            st.session_state.slide = next(i for i, (t, _) in enumerate(SLIDES) if "Dashboard" in t)
            st.rerun()

    st.markdown(
        '<div style="text-align:center;margin-top:28px;color:#5A7184;font-size:.85rem;">'
        "Developer Standards &amp; Development Workflow · Mandatory for all team members"
        "</div>",
        unsafe_allow_html=True,
    )


# ==============================================================================
# AUTH GATE  (with URL-token restore so refresh does not log you out)
# ==============================================================================
_restore_session_from_url()

if not st.session_state.authenticated:
    login_page()
    st.stop()

# At this point the user is authenticated — safe to initialise app modules
init_posts_state()


# ==============================================================================
# SLIDE REGISTRY
# ==============================================================================
SLIDES = [
    ("Title", s_title),
    ("1. Purpose & Objectives", s_purpose),
    ("2. TypeScript — Type Detective", s_type_detective),
    ("3. TypeScript — Quiz", s_type_quiz),
    ("4. Git — Branch Simulator", s_branch_sim),
    ("5. PR Review Simulator", s_pr_sim),
    ("6. Developer Testing Checklist", s_dev_checklist),
    ("7. SQL Playground", s_sql_playground),
    ("8. Real PR Review", s_review_game),
    ("9. Failure Triage", s_triage),
    ("10. Order the Workflow", s_workflow_game),
    ("11. Scenario Simulator", s_scenarios),
    ("12. Final Compliance Checklist", s_final_checklist),
    ("13. 🎓 Final Exam", s_exam),
    ("14. Progress Dashboard", s_dashboard),
    ("15. Final Message", s_final),
]

_user_role = (st.session_state.user or {}).get("role")

if _user_role in ADMIN_ROLES:
    SLIDES.append(("16. Exam Submissions (Admin)", s_submissions))

if _user_role in ("admin", "super_admin"):
    SLIDES.append(("17. Exam & Question Management", s_question_management))

if _user_role == "super_admin":
    SLIDES.append(("18. Admin Management (Super Admin)", s_admin_management))

SLIDES.append(("📚 Standards & Blog", s_posts_hub))
if _user_role in ("admin", "super_admin"):
    SLIDES.append(("19. Post Management", s_posts_management))

if st.session_state.slide >= len(SLIDES):
    st.session_state.slide = 0


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    u = st.session_state.user or {}
    st.markdown(
        f"""
        <div class="user-badge">
            <div style="font-size:.7rem;letter-spacing:1.2px;opacity:.8;">SIGNED IN</div>
            <div style="font-size:.95rem;font-weight:800;margin-top:2px;">{html_lib.escape(u.get('name',''))}</div>
            <div style="font-size:.7rem;opacity:.85;">{html_lib.escape(u.get('username',''))} · {html_lib.escape((u.get('role') or '').upper())}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="padding:0 2px 10px 2px;">
            <div style="font-size:1.05rem;font-weight:900;letter-spacing:.5px;">🛠️ DEV STANDARDS</div>
            <div style="font-size:.68rem;opacity:.75;letter-spacing:1.5px;">EXAM EDITION</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    progress = (st.session_state.slide + 1) / len(SLIDES)
    st.progress(progress)
    st.caption(f"Slide {st.session_state.slide + 1} of {len(SLIDES)}")

    earned, possible = total_score()
    if possible:
        pct = earned / possible * 100
        st.markdown(
            f'<div style="background:rgba(255,255,255,.12);border-radius:8px;padding:8px 10px;margin:8px 0;">'
            f'<div style="font-size:.7rem;letter-spacing:1px;opacity:.85;">YOUR SCORE</div>'
            f'<div style="font-size:1.15rem;font-weight:800;">{earned} / {possible}</div>'
            f'<div style="font-size:.7rem;opacity:.8;">{pct:.0f}% complete</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.exam_submitted:
        ex_total = len(st.session_state.exam_results)
        ex_pct = st.session_state.exam_score / ex_total * 100 if ex_total else 0
        exam_state = "PASSED" if ex_pct >= _active_pass_mark() * 100 else "NOT PASSED"
        st.markdown(
            f'<div style="background:rgba(255,255,255,.10);border-radius:8px;padding:7px 10px;margin-bottom:8px;'
            f'font-size:.72rem;">Exam: <b>{st.session_state.exam_score}/{ex_total}</b> · {exam_state}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:rgba(217,164,65,.20);border-radius:8px;padding:7px 10px;margin-bottom:8px;'
            'font-size:.72rem;">🎓 Final exam not taken yet</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    for i, (title, _) in enumerate(SLIDES):
        if st.button(title, key=f"nav_{i}"):
            st.session_state.slide = i
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Sign out", key="logout_btn"):
        _clear_session_token()
        for k in list(_defaults.keys()):
            st.session_state.pop(k, None)
        for key in list(st.session_state.keys()):
            if key.startswith(("exam_radio_", "pal_", "typeq_", "ab_", "sc_", "pr_", "rev_", "nav_", "dev_ck_", "final_ck_", "wf_btn_")):
                st.session_state.pop(key, None)
        st.rerun()


# ==============================================================================
# RENDER ACTIVE SLIDE
# ==============================================================================
SLIDES[st.session_state.slide][1]()

# ==============================================================================
# BOTTOM NAVIGATION
# ==============================================================================
st.markdown("---")
c1, c2, c3 = st.columns([1, 3, 1])

with c1:
    if st.button("⬅  Previous", use_container_width=True, disabled=st.session_state.slide == 0):
        st.session_state.slide -= 1
        st.rerun()

with c2:
    st.markdown(
        f'<div style="text-align:center;color:#5A7184;font-size:.85rem;padding-top:8px;">'
        f'<b style="color:#0B3C5D;">{SLIDES[st.session_state.slide][0]}</b> '
        f'&nbsp;·&nbsp; {st.session_state.slide + 1} / {len(SLIDES)}</div>',
        unsafe_allow_html=True,
    )

with c3:
    if st.button("Next  ➡", use_container_width=True, disabled=st.session_state.slide == len(SLIDES) - 1):
        st.session_state.slide += 1
        st.rerun()