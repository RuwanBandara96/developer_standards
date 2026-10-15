# ==============================================================================
#  DEVELOPER STANDARDS & DEVELOPMENT WORKFLOW — INTERACTIVE EDITION
#  Gamified, quiz-driven, scenario-based presentation
# ------------------------------------------------------------------------------
#  Run with:   streamlit run developer_standards.py
#  Requires:   streamlit, pandas, numpy, plotly
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
import random

# ------------------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Developer Standards — Interactive",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# GLOBAL STYLE  (includes dark-theme fix)
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

/* ---------- DARK-THEME PROOFING ---------- */
.card, .card *,
.kpi,  .kpi *,
.tree, .tree *,
.do-box,   .do-box *,
.dont-box, .dont-box *,
.quiz-box, .quiz-box *,
.pr-card,  .pr-card * {
    color: #2B3A4A !important;
}
.card h4, .kpi .v, .quiz-box h4, .tree b,
.card b, .card strong, .pr-card b, .pr-card strong { color: #0B3C5D !important; }
.do-box h5   { color: #14615E !important; }
.dont-box h5 { color: #9B2C2C !important; }
.card i, .card em, .kpi .l, .pr-card i { color: #5A7184 !important; }
.card code, .do-box code, .dont-box code, .quiz-box code,
.tree code, .pr-card code {
    background: #EEF2F6 !important;
    color: #0B3C5D !important;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: .85em;
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
.sec-num{
  display:inline-block;background:var(--teal);color:#fff;font-size:.7rem;font-weight:800;
  padding:3px 10px;border-radius:20px;letter-spacing:1px;margin-bottom:8px;
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
        f'{n}<div class="slide-title">{title}</div><div class="slide-sub">{sub}</div>',
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


# ------------------------------------------------------------------------------
# SESSION STATE INIT
# ------------------------------------------------------------------------------
if "slide" not in st.session_state:
    st.session_state.slide = 0
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "dev_checklist" not in st.session_state:
    st.session_state.dev_checklist = {}
if "final_checklist" not in st.session_state:
    st.session_state.final_checklist = {}
if "dev_notes" not in st.session_state:
    st.session_state.dev_notes = ""
if "final_notes" not in st.session_state:
    st.session_state.final_notes = ""
if "wf_clicked" not in st.session_state:
    st.session_state.wf_clicked = []
if "scenario_state" not in st.session_state:
    st.session_state.scenario_state = {}
if "pr_selected" not in st.session_state:
    st.session_state.pr_selected = set()
if "review_selected" not in st.session_state:
    st.session_state.review_selected = set()
if "celebrated" not in st.session_state:
    st.session_state.celebrated = {"dev": False, "final": False}


def record_score(key, value, total):
    st.session_state.scores[key] = {"value": value, "total": total}


def total_score():
    earned = sum(v["value"] for v in st.session_state.scores.values())
    possible = sum(v["total"] for v in st.session_state.scores.values())
    return earned, possible


# ==============================================================================
# SLIDE 1 — TITLE
# ==============================================================================
def s_title():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Interactive Technical Standards</div>
            <div class="hero-title">Developer Standards &amp; Development Workflow</div>
            <div class="hero-sub">Not a slideshow — an interactive experience. Play through simulators, quizzes, and checklists.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    kpi_row(
        [
            ("Status", "MANDATORY"),
            ("Slides", "15"),
            ("Interactive Activities", "12+"),
            ("Progress Tracked", "Live"),
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
            "Real PR review",
            "The Code Review slide uses <b>your actual PawningAuctioneer service</b> as the compliant "
            "reference, paired with a broken version — you spot every standard violation.",
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
                    "Final Checklist",
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
        "Choose the right base branch and PR target — get graded instantly",
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
        "You have local access to branches `main`, `dev`, `qa`, and a stale local `feature/4001` "
        "that hasn't been synced in 3 weeks. Your team uses the standard promotion flow."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        branch_name = st.text_input("1. What will you name your working branch?", value="", key="bs_name")
    with c2:
        base = st.selectbox(
            "2. Create the working branch from…",
            ["main", "dev", "qa", "feature/4001 (local, stale)"],
            index=None,
            key="bs_base",
        )
    with c3:
        target = st.selectbox(
            "3. What is the initial PR target?",
            ["main", "dev", "qa"],
            index=None,
            key="bs_target",
        )
    if st.button("✅ Grade my choices", type="primary"):
        score = 0
        feedback = []
        if branch_name.strip() == "feature/4471":
            score += 1
            feedback.append(("success", "Branch name is correct: `feature/4471` follows the convention."))
        else:
            feedback.append(("error", "Branch name should be `feature/4471` — `feature/<issue-id>`."))
        if base == "dev":
            score += 2
            feedback.append(("success", "Correct base: `dev` is the latest approved base for feature work."))
        elif base == "main":
            feedback.append(("error", "`main` is not the base for features — use the latest `dev`."))
        elif base == "qa":
            feedback.append(("error", "`qa` is a promotion target, not a feature base."))
        elif base and "stale" in base:
            feedback.append(("error", "Never branch from a stale local branch — always pull the latest."))
        else:
            feedback.append(("warning", "Pick a base branch."))
        if target == "dev":
            score += 2
            feedback.append(("success", "Correct PR target: `dev`. Direct PRs to QA are not permitted."))
        else:
            feedback.append(("error", f"Wrong target. The initial PR must go to `dev`, not `{target}`."))
        record_score("branch_sim", score, 5)
        for kind, msg in feedback:
            getattr(st, kind)(msg)
        st.markdown(f"**Score:** {score_pill(score, 5)}", unsafe_allow_html=True)
        if score == 5:
            st.success("🏆 Perfect — you've nailed the branch workflow.")
            st.balloons()
    st.markdown("---")
    st.markdown(
        f'<div class="hflow" style="justify-content:center;">'
        + '<span class="hbox">Working Branch</span><span class="harrow">→</span>'
        + '<span class="hbox hbox-navy">DEV</span><span class="harrow">→</span>'
        + '<span class="hbox hbox-gold">QA</span>'
        + "</div>",
        unsafe_allow_html=True,
    )
    st.error("**Direct merges from feature/bugfix branches into QA are not permitted under the standard workflow.**")


# ==============================================================================
# SLIDE 6 — PR REVIEW SIMULATOR (short one)
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
# SLIDE 9 — REAL PR REVIEW  (NEW — replaces "Spot the Issue")
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
      // ... type-safe mapping via withOptionalCheckBigInt / withOptionalCheckDecimal
      return new PawnAuctioneerData({ /* fully typed */ } as any)
    }
  }

  public async retrievePawnAuctioneers(
    params: ListPawningAuctioneerParams
  ): Promise<{ data: PawnAuctioneerData[]; total: number }> {
    const { limit, offset, search } = params
    const Mapper = new PawningAuctioneerReadPlatformService.PawningAuctioneer()
    const searchFilter = `%${search ?? ''}%`

    // ✅ Parameterised COUNT query
    const countQuery = `
      SELECT COUNT(*) AS count FROM pw_auctioneers a
      WHERE (a.name LIKE ? OR a.nic LIKE ? OR a.company_name LIKE ? OR a.license_number LIKE ?)
    `
    const countResult = (await this.context.queryRunner.query(countQuery, [
      searchFilter, searchFilter, searchFilter, searchFilter,
    ])) as { count: number }[]
    const total = Number(countResult[0]?.count ?? 0)

    // ✅ Parameterised SELECT with explicit columns + bounded results
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
      // ✅ Domain-specific exception
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
            ("Slides", "15"),
            ("Interactive Activities", "12+"),
            ("Your Score", f"{earned} / {possible}"),
            ("Completion", f"{pct:.0f}%"),
        ]
    )
    st.markdown(
        '<div style="text-align:center;margin-top:28px;color:#5A7184;font-size:.85rem;">'
        "Developer Standards &amp; Development Workflow · Mandatory for all team members"
        "</div>",
        unsafe_allow_html=True,
    )


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
    ("13. Progress Dashboard", s_dashboard),
    ("14. Final Message", s_final),
]

# ------------------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding:6px 2px 14px 2px;">
            <div style="font-size:1.12rem;font-weight:900;letter-spacing:.5px;">🛠️ DEV STANDARDS</div>
            <div style="font-size:.7rem;opacity:.75;letter-spacing:1.5px;">INTERACTIVE EDITION</div>
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
    st.markdown("---")
    for i, (title, _) in enumerate(SLIDES):
        if st.button(title, key=f"nav_{i}"):
            st.session_state.slide = i
            st.rerun()
    st.markdown("---")
    if st.button("🔄 Reset everything", key="global_reset"):
        st.session_state.scores = {}
        st.session_state.dev_checklist = {}
        st.session_state.final_checklist = {}
        st.session_state.scenario_state = {}
        st.session_state.pr_selected = set()
        st.session_state.review_selected = set()
        st.session_state.wf_clicked = []
        st.session_state.celebrated = {"dev": False, "final": False}
        st.rerun()

# ------------------------------------------------------------------------------
# RENDER ACTIVE SLIDE
# ------------------------------------------------------------------------------
SLIDES[st.session_state.slide][1]()

# ------------------------------------------------------------------------------
# BOTTOM NAVIGATION
# ------------------------------------------------------------------------------
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