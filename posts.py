# ==============================================================================
#  posts.py — Standalone module for Standards & Blog posts
# ------------------------------------------------------------------------------
#  Adds:
#    • A public "Standards & Blog" hub where every signed-in user can browse
#      posts, filtered by category (Standards / Blog / Announcement) and tags.
#    • A "Post Management" console where admin / super_admin can create, edit,
#      publish, pin, and delete posts.
#
#  Storage: posts.json (created automatically on first save)
#
#  Wiring (in developer.py, AFTER the auth gate):
#      from posts import init_posts_state, s_posts_hub, s_posts_management
#      init_posts_state()
#      # in the slide registry:
#      SLIDES.append(("📚 Standards & Blog", s_posts_hub))
#      if role in ("admin", "super_admin"):
#          SLIDES.append(("19. Post Management", s_posts_management))
# ==============================================================================

import streamlit as st
import pandas as pd
import os
import json
import re
import html as html_lib
from datetime import datetime

# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------
POSTS_PATH = "posts.json"
ADMIN_ROLES = ("examiner", "admin", "super_admin")
EDITOR_ROLES = ("admin", "super_admin")          # who can create/edit/delete
CATEGORIES = ["Standards", "Blog", "Announcement"]

SESSION_KEY = "posts_state"                       # key used in st.session_state
CSS_FLAG = "_posts_css_loaded"


# ------------------------------------------------------------------------------
# CSS  (self-contained, matches the main app's theme)
# ------------------------------------------------------------------------------
_POSTS_CSS = """
<style>
.post-card{
  background:#fff;border:1px solid #E1E8EE;border-left:5px solid #1D7874;
  border-radius:12px;padding:18px 22px;margin-bottom:14px;
  box-shadow:0 2px 6px rgba(11,60,93,.06);
  transition:box-shadow .15s ease;
}
.post-card:hover{box-shadow:0 6px 18px rgba(11,60,93,.12);}
.post-card.post-pinned{border-left-color:#D9A441;background:#FFFDF8;}
.post-card.post-draft{border-left-color:#C0392B;opacity:.85;}
.post-card .post-title{
  font-size:1.1rem;font-weight:800;color:#0B3C5D;margin:0 0 4px 0;line-height:1.3;
}
.post-card .post-meta{
  font-size:.74rem;color:#5A7184;letter-spacing:.3px;margin-bottom:10px;
}
.post-card .post-summary{
  font-size:.88rem;color:#2B3A4A;line-height:1.6;margin:6px 0 10px 0;
}
.post-card .post-body{
  font-size:.9rem;color:#2B3A4A;line-height:1.75;
  border-top:1px dashed #E1E8EE;padding-top:12px;margin-top:6px;
}
.post-chip{
  display:inline-block;background:#E8F3F2;color:#14615E;border:1px solid #BFE0DD;
  border-radius:20px;padding:3px 11px;margin:3px 5px 3px 0;font-size:.72rem;font-weight:600;
}
.post-chip.cat{background:#E9EFF5;color:#0B3C5D;border-color:#C6D6E4;}
.post-chip.pinned{background:#FDF4E3;color:#8A6512;border-color:#F0D9A8;}
.post-chip.draft{background:#FDECEC;color:#9B2C2C;border-color:#F5C6C6;}
.post-chip.tag{background:#F3F7FA;color:#5A7184;border-color:#E1E8EE;}

.post-hero{
  background:linear-gradient(120deg,#0B3C5D 0%,#1D7874 100%);
  border-radius:16px;padding:26px 30px;color:#fff;margin-bottom:20px;
  box-shadow:0 8px 22px rgba(11,60,93,.22);
}
.post-hero h1{color:#fff !important;margin:0 0 6px 0;font-size:1.8rem;line-height:1.15;}
.post-hero p{margin:0;opacity:.92;font-size:.95rem;}

section[data-testid="stSidebar"] .stButton>button:focus{box-shadow:none;}
</style>
"""


def _inject_css():
    if CSS_FLAG not in st.session_state:
        st.markdown(_POSTS_CSS, unsafe_allow_html=True)
        st.session_state[CSS_FLAG] = True


# ------------------------------------------------------------------------------
# HELPERS  (self-contained — no dependencies on developer.py)
# ------------------------------------------------------------------------------
def _slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", (name or "").strip().lower()).strip("_")
    return s or "post"


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _fmt_dt(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%d %b %Y · %H:%M")
    except Exception:
        return iso or "—"


def _current_user() -> dict:
    u = st.session_state.get("user") or {}
    if not isinstance(u, dict):
        return {}
    return u


def _user_role() -> str:
    return (_current_user().get("role") or "").lower()


def _header(title: str, sub: str = "", badge: str = ""):
    b = f'<div class="sec-num">{badge}</div>' if badge else ""
    st.markdown(
        f'{b}<div class="slide-title">{title}</div><div class="slide-sub">{sub}</div>',
        unsafe_allow_html=True,
    )


def _kpi_row(items):
    cols = st.columns(len(items))
    for c, (label, value) in zip(cols, items):
        c.markdown(
            f'<div class="kpi"><div class="v">{value}</div><div class="l">{label}</div></div>',
            unsafe_allow_html=True,
        )


def _chips(items, cls="post-chip"):
    return "".join(f'<span class="{cls}">{html_lib.escape(str(i))}</span>' for i in items)


# ------------------------------------------------------------------------------
# STORAGE
# ------------------------------------------------------------------------------
def load_posts() -> list:
    """Return the list of posts from disk, or [] if not found / unreadable."""
    if not os.path.exists(POSTS_PATH):
        return []
    try:
        with open(POSTS_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_posts(posts: list) -> bool:
    try:
        with open(POSTS_PATH, "w", encoding="utf-8") as fh:
            json.dump(posts, fh, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def init_posts_state():
    """Call once after login. Loads posts into session_state if not already loaded."""
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = load_posts()


def _posts() -> list:
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = load_posts()
    return st.session_state[SESSION_KEY]


def _commit(posts: list) -> bool:
    st.session_state[SESSION_KEY] = posts
    return save_posts(posts)


# ------------------------------------------------------------------------------
# PUBLIC HUB  — browse posts
# ------------------------------------------------------------------------------
def s_posts_hub():
    _inject_css()

    posts = _posts()
    published = [p for p in posts if p.get("published", True)]

    st.markdown(
        """
        <div class="post-hero">
            <h1>📚 Standards &amp; Blog</h1>
            <p>Team standards, how-to guides, and blog articles — curated by the team leads.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- KPIs ----
    total = len(published)
    by_cat = {c: sum(1 for p in published if p.get("category") == c) for c in CATEGORIES}
    last = max((p.get("updated_at") or p.get("created_at") or "" for p in published), default="")
    _kpi_row([
        ("Published posts", str(total)),
        ("Standards", str(by_cat.get("Standards", 0))),
        ("Blogs", str(by_cat.get("Blog", 0))),
        ("Last updated", _fmt_dt(last) if last else "—"),
    ])

    st.markdown("---")

    # ---- filters ----
    c1, c2, c3 = st.columns([1.4, 1, 1])
    with c1:
        q = st.text_input("🔍 Search", placeholder="title, summary, or content…", key="posts_search")
    with c2:
        cat_filter = st.selectbox("Category", ["All"] + CATEGORIES, key="posts_cat_filter")
    with c3:
        sort_by = st.selectbox("Sort", ["Newest first", "Oldest first", "Title A→Z"], key="posts_sort")

    view = list(published)

    if cat_filter != "All":
        view = [p for p in view if p.get("category") == cat_filter]

    if q.strip():
        needle = q.strip().lower()
        def _matches(p):
            blob = " ".join([
                str(p.get("title", "")),
                str(p.get("summary", "")),
                str(p.get("content", "")),
                " ".join(p.get("tags", []) or []),
            ]).lower()
            return needle in blob
        view = [p for p in view if _matches(p)]

    # pinned first, then by chosen sort
    def _sort_key(p):
        pinned = 0 if p.get("pinned") else 1
        created = p.get("created_at", "")
        return (pinned, created)

    if sort_by == "Newest first":
        view.sort(key=_sort_key, reverse=False)
        view.sort(key=lambda p: (0 if p.get("pinned") else 1, _neg_iso(p.get("created_at", ""))))
    elif sort_by == "Oldest first":
        view.sort(key=lambda p: (0 if p.get("pinned") else 1, p.get("created_at", "")))
    else:
        view.sort(key=lambda p: (0 if p.get("pinned") else 1, (p.get("title") or "").lower()))

    if not view:
        st.info("No posts match your filters yet.")
        return

    # ---- category tabs ----
    tab_labels = ["All"] + CATEGORIES
    tabs = st.tabs(tab_labels)
    for tab, label in zip(tabs, tab_labels):
        with tab:
            subset = view if label == "All" else [p for p in view if p.get("category") == label]
            if not subset:
                st.caption(f"No {label.lower()} posts yet.")
                continue
            for p in subset:
                _render_post_card(p)

    st.caption("Tip: posts are managed by administrators. Ask your team lead if you need something published.")


def _neg_iso(iso: str) -> str:
    """Hack to reverse-sort by ISO string: swap with a max-bound trick."""
    # '2025-01-01...' → we want newest first, so use the negative via string trick
    # Simplest robust way: use the unix timestamp-like string but negate numerically.
    try:
        from datetime import datetime as _dt
        return f"{9999999999 - int(_dt.fromisoformat(iso).timestamp()):010d}"
    except Exception:
        return "9999999999"


def _render_post_card(post: dict):
    cat = post.get("category", "—")
    tags = post.get("tags", []) or []
    author = post.get("author_name") or post.get("author") or "—"
    created = _fmt_dt(post.get("created_at", ""))
    updated = post.get("updated_at")
    updated_html = f" · updated {_fmt_dt(updated)}" if updated and updated != post.get("created_at") else ""

    classes = "post-card"
    if post.get("pinned"):
        classes += " post-pinned"

    chips_html = _chips([cat], "post-chip cat")
    if post.get("pinned"):
        chips_html += _chips(["📌 Pinned"], "post-chip pinned")
    chips_html += "".join(_chips([t], "post-chip tag") for t in tags if t)

    summary = post.get("summary") or ""
    body = post.get("content") or ""

    st.markdown(
        f'<div class="{classes}">'
        f'<div class="post-title">{html_lib.escape(post.get("title","Untitled"))}</div>'
        f'<div class="post-meta">By <b>{html_lib.escape(author)}</b> · {created}{updated_html}</div>'
        f'<div>{chips_html}</div>'
        f'{f"<div class=\'post-summary\'>{html_lib.escape(summary)}</div>" if summary else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )
    # Full body in an expander, rendered as markdown
    if body.strip():
        with st.expander("Read full post", expanded=False):
            st.markdown(body)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# MANAGEMENT  — create / edit / delete
# ------------------------------------------------------------------------------
def s_posts_management():
    _inject_css()

    role = _user_role()
    if role not in EDITOR_ROLES:
        st.error("🚫 Access denied. Only administrators can manage posts.")
        return

    _header(
        "Post Management",
        "Create, edit, and publish standards and blog posts",
        "ADMIN",
    )

    posts = _posts()

    tab_list, tab_new, tab_edit = st.tabs(["📋 All posts", "➕ New post", "✏️ Edit post"])

    # ---------------------------------------------------------------------
    # TAB 1 — List + quick actions
    # ---------------------------------------------------------------------
    with tab_list:
        if not posts:
            st.info("No posts yet. Create the first one in the **New post** tab.")
        else:
            rows = []
            for p in posts:
                rows.append({
                    "ID": p.get("id", ""),
                    "Title": p.get("title", ""),
                    "Category": p.get("category", ""),
                    "Tags": ", ".join(p.get("tags", []) or []),
                    "Author": p.get("author_name") or p.get("author", ""),
                    "Published": "✅" if p.get("published", True) else "📝 draft",
                    "Pinned": "📌" if p.get("pinned") else "—",
                    "Updated": _fmt_dt(p.get("updated_at") or p.get("created_at", "")),
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

            st.markdown("---")
            st.markdown("#### Quick actions")
            pick_id = st.selectbox(
                "Select a post",
                ["— select —"] + [p.get("id", "") for p in posts],
                format_func=lambda pid: next(
                    (f"{p.get('title','')} ({pid})" for p in posts if p.get("id") == pid),
                    pid
                ),
                key="posts_admin_pick",
            )
            if pick_id and pick_id != "— select —":
                target = next((p for p in posts if p.get("id") == pick_id), None)
                if target:
                    cc1, cc2, cc3 = st.columns([1, 1, 1])
                    with cc1:
                        new_pub = st.toggle(
                            "Published",
                            value=bool(target.get("published", True)),
                            key=f"pub_toggle_{pick_id}",
                        )
                        if new_pub != bool(target.get("published", True)):
                            target["published"] = new_pub
                            target["updated_at"] = _now_iso()
                            if _commit(posts):
                                st.success("Visibility updated.")
                                st.rerun()
                    with cc2:
                        new_pin = st.toggle(
                            "Pinned",
                            value=bool(target.get("pinned", False)),
                            key=f"pin_toggle_{pick_id}",
                        )
                        if new_pin != bool(target.get("pinned", False)):
                            target["pinned"] = new_pin
                            target["updated_at"] = _now_iso()
                            if _commit(posts):
                                st.success("Pinned state updated.")
                                st.rerun()
                    with cc3:
                        if st.button("🗑 Delete this post", key=f"del_{pick_id}"):
                            posts = [p for p in posts if p.get("id") != pick_id]
                            if _commit(posts):
                                st.success("Post deleted.")
                                st.rerun()

    # ---------------------------------------------------------------------
    # TAB 2 — Create new post
    # ---------------------------------------------------------------------
    with tab_new:
        st.markdown("### Create a new post")
        with st.form("posts_create_form", clear_on_submit=True):
            title = st.text_input("Title *", placeholder="e.g. Standard: Handling Decimal values")
            cc1, cc2 = st.columns(2)
            with cc1:
                category = st.selectbox("Category *", CATEGORIES, index=0)
            with cc2:
                tags_raw = st.text_input("Tags (comma separated)", placeholder="typescript, decimal, money")
            summary = st.text_area(
                "Summary (shown on the card)", height=70,
                placeholder="One or two sentences describing the post.",
            )
            content = st.text_area(
                "Content (Markdown supported) *", height=260,
                placeholder="Write the full post here. **Markdown** is supported.\n\n## Headings\n- bullet points\n- `inline code`\n\n```ts\n// code blocks\n```",
            )
            cc3, cc4 = st.columns(2)
            with cc3:
                published = st.checkbox("Published", value=True)
            with cc4:
                pinned = st.checkbox("Pinned to top", value=False)

            create = st.form_submit_button("➕ Create post", type="primary", use_container_width=True)

        if create:
            errs = []
            if not title.strip():
                errs.append("Title is required.")
            if not content.strip():
                errs.append("Content is required.")
            if category not in CATEGORIES:
                errs.append("Invalid category.")

            if errs:
                for e in errs:
                    st.error(f"❌ {e}")
            else:
                # unique id from slug + counter
                base = _slugify(title)
                new_id = base
                existing_ids = {p.get("id", "") for p in posts}
                n = 2
                while new_id in existing_ids:
                    new_id = f"{base}_{n}"
                    n += 1

                user = _current_user()
                new_post = {
                    "id": new_id,
                    "title": title.strip(),
                    "category": category,
                    "tags": [t.strip() for t in tags_raw.split(",") if t.strip()],
                    "summary": summary.strip(),
                    "content": content.strip(),
                    "published": bool(published),
                    "pinned": bool(pinned),
                    "author": user.get("username", ""),
                    "author_name": user.get("name", ""),
                    "created_at": _now_iso(),
                    "updated_at": None,
                }
                posts.append(new_post)
                if _commit(posts):
                    st.success(f"✅ Post **{title.strip()}** created (`{new_id}`).")
                    st.rerun()
                else:
                    st.error("❌ Failed to save the post. Check file permissions.")

    # ---------------------------------------------------------------------
    # TAB 3 — Edit existing
    # ---------------------------------------------------------------------
    with tab_edit:
        if not posts:
            st.info("Nothing to edit yet.")
            return

        st.markdown("### Edit a post")
        edit_id = st.selectbox(
            "Select a post to edit",
            ["— select —"] + [p.get("id", "") for p in posts],
            format_func=lambda pid: next(
                (f"{p.get('title','')} ({pid})" for p in posts if p.get("id") == pid),
                pid,
            ),
            key="posts_edit_select",
        )

        if edit_id and edit_id != "— select —":
            target = next((p for p in posts if p.get("id") == edit_id), None)
            if target:
                with st.form(f"posts_edit_form_{edit_id}"):
                    e_title = st.text_input("Title *", value=target.get("title", ""))
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        cur_cat = target.get("category", CATEGORIES[0])
                        cat_index = CATEGORIES.index(cur_cat) if cur_cat in CATEGORIES else 0
                        e_category = st.selectbox("Category *", CATEGORIES, index=cat_index)
                    with cc2:
                        e_tags = st.text_input(
                            "Tags (comma separated)",
                            value=", ".join(target.get("tags", []) or []),
                        )
                    e_summary = st.text_area("Summary", value=target.get("summary", ""), height=70)
                    e_content = st.text_area("Content *", value=target.get("content", ""), height=260)
                    cc3, cc4 = st.columns(2)
                    with cc3:
                        e_published = st.checkbox("Published", value=bool(target.get("published", True)))
                    with cc4:
                        e_pinned = st.checkbox("Pinned", value=bool(target.get("pinned", False)))

                    save = st.form_submit_button("💾 Save changes", type="primary", use_container_width=True)

                if save:
                    errs = []
                    if not e_title.strip():
                        errs.append("Title is required.")
                    if not e_content.strip():
                        errs.append("Content is required.")
                    if errs:
                        for e in errs:
                            st.error(f"❌ {e}")
                    else:
                        target["title"] = e_title.strip()
                        target["category"] = e_category
                        target["tags"] = [t.strip() for t in e_tags.split(",") if t.strip()]
                        target["summary"] = e_summary.strip()
                        target["content"] = e_content.strip()
                        target["published"] = bool(e_published)
                        target["pinned"] = bool(e_pinned)
                        target["updated_at"] = _now_iso()
                        if _commit(posts):
                            st.success("✅ Post updated.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to save changes.")

                st.markdown("---")
                st.caption(
                    "Deleting is also available in the **All posts** tab (with quick toggles for "
                    "publish state and pinning)."
                )