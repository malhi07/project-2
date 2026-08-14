import json
import os
import time
from pathlib import Path
from threading import Lock

import streamlit as st
from anthropic import Anthropic

st.set_page_config(page_title="Project Two — Writing Practice", page_icon="✍️", layout="centered")

DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_json(filename):
    with open(DATA_DIR / filename, "r") as f:
        return json.load(f)


descriptors = load_json("clb-descriptors.json")
writing_tasks = load_json("writing-tasks.json")["tasks"]
WRITING_DIMENSIONS = descriptors["writingDimensions"]


def get_owner_api_key():
    # Prefer Streamlit Cloud secrets; fall back to env var for other hosts
    if "ANTHROPIC_API_KEY" in st.secrets:
        return st.secrets["ANTHROPIC_API_KEY"]
    return os.environ.get("ANTHROPIC_API_KEY")


def build_grading_prompt(task_prompt, task_type, response_text):
    dims = "\n".join(f"- {d['name']} ({d['id']}): {d['description']}" for d in WRITING_DIMENSIONS)
    return f"""You are an expert English language assessor trained on the Canadian Language Benchmark (CLB) framework, scale 1-12. You are grading a piece of writing.

TASK TYPE: {task_type}
TASK PROMPT GIVEN TO THE WRITER:
\"\"\"
{task_prompt}
\"\"\"

WRITER'S RESPONSE:
\"\"\"
{response_text}
\"\"\"

Score the response on these four dimensions (each 1-12 on the CLB scale):
{dims}

For EACH dimension, provide:
1. A numeric CLB score (1-12)
2. A short justification (1-2 sentences)

Then provide:
- An overall CLB band (average of the four, rounded to nearest whole number)
- A list of specific issues found in the text. For each issue include: the exact quoted text/phrase that has the problem, which dimension it affects, why it lost marks, and a corrected/improved rewrite of that phrase or sentence.
- A short paragraph of "what would move you up one CLB level" advice.

Respond ONLY with valid JSON in exactly this shape, no markdown fences, no extra text:
{{
  "dimensionScores": [
    {{ "id": "content_coherence", "score": 0, "justification": "" }},
    {{ "id": "vocabulary", "score": 0, "justification": "" }},
    {{ "id": "readability", "score": 0, "justification": "" }},
    {{ "id": "task_fulfillment", "score": 0, "justification": "" }}
  ],
  "overallBand": 0,
  "issues": [
    {{ "quote": "", "dimension": "", "explanation": "", "improvedVersion": "" }}
  ],
  "levelUpAdvice": ""
}}"""


def score_writing(task_prompt, task_type, response_text, api_key):
    client = Anthropic(api_key=api_key)
    prompt = build_grading_prompt(task_prompt, task_type, response_text)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    cleaned = text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


# --- Shared global rate limiter (protects the OWNER's key, shared across all visitors) ---
# Lives in memory for as long as the app process stays awake; resets on redeploy/sleep.
# This is a lightweight safeguard, not a persistent database.
GLOBAL_DAILY_CAP = 100        # total scoring calls per day across ALL visitors using the owner's key
PER_USER_DAILY_CAP = 10       # scoring calls per browser session per day, when using the owner's key


@st.cache_resource
def get_global_counter():
    return {"lock": Lock(), "calls": []}


def global_calls_today():
    state = get_global_counter()
    now = time.time()
    day_seconds = 24 * 60 * 60
    with state["lock"]:
        state["calls"] = [t for t in state["calls"] if now - t < day_seconds]
        return len(state["calls"])


def record_global_call():
    state = get_global_counter()
    with state["lock"]:
        state["calls"].append(time.time())


# --- Per-session limiter ---
if "scoring_calls" not in st.session_state:
    st.session_state.scoring_calls = []


def session_calls_today():
    now = time.time()
    day_seconds = 24 * 60 * 60
    st.session_state.scoring_calls = [t for t in st.session_state.scoring_calls if now - t < day_seconds]
    return len(st.session_state.scoring_calls)


def record_session_call():
    st.session_state.scoring_calls.append(time.time())


# --- App state ---
if "selected_task" not in st.session_state:
    st.session_state.selected_task = None
if "result" not in st.session_state:
    st.session_state.result = None

st.title("✍️ Project Two — Writing Practice")
st.caption("Free, open-source English writing practice with AI feedback scored against CLB descriptors.")

# --- Sidebar: optional own API key ---
with st.sidebar:
    st.markdown("### API key")
    st.caption(
        "By default this app uses a shared key with a limited daily allowance. "
        "Enter your own Anthropic API key for unlimited practice — it's used only "
        "for your requests and never stored."
    )
    user_api_key = st.text_input("Your own Anthropic API key (optional)", type="password")
    if user_api_key:
        st.success("Using your own API key — no daily limit applied.")

owner_api_key = get_owner_api_key()
using_own_key = bool(user_api_key)
active_api_key = user_api_key if using_own_key else owner_api_key

if not active_api_key:
    st.warning(
        "No API key available. Either add ANTHROPIC_API_KEY under Streamlit Cloud → "
        "App settings → Secrets, or enter your own key in the sidebar."
    )

# --- Task selection ---
if st.session_state.selected_task is None:
    st.subheader("Choose a task")
    for task in writing_tasks:
        with st.container(border=True):
            st.markdown(f"**{task['title']}**")
            st.write(task["prompt"])
            st.caption(f"Time limit: {task['timeLimitMinutes']} min · Min words: {task['minWords']}")
            if st.button("Start", key=f"start-{task['id']}"):
                st.session_state.selected_task = task
                st.session_state.result = None
                st.rerun()

# --- Writing view ---
elif st.session_state.result is None:
    task = st.session_state.selected_task
    st.subheader(task["title"])
    st.write(task["prompt"])
    st.caption(f"Suggested time: {task['timeLimitMinutes']} minutes (not strictly enforced)")

    response_text = st.text_area("Your response", height=300, key="response_text")
    word_count = len(response_text.split()) if response_text.strip() else 0
    st.caption(f"Word count: {word_count} (minimum {task['minWords']})")

    if not using_own_key and active_api_key:
        st.caption(
            f"Shared key usage today — you: {session_calls_today()}/{PER_USER_DAILY_CAP}, "
            f"site-wide: {global_calls_today()}/{GLOBAL_DAILY_CAP}"
        )

    col1, col2 = st.columns(2)
    with col1:
        submit = st.button("Submit for AI feedback", type="primary", disabled=not active_api_key)
    with col2:
        if st.button("Cancel"):
            st.session_state.selected_task = None
            st.rerun()

    if submit:
        if not response_text.strip():
            st.error("Please write a response before submitting.")
        elif not using_own_key and session_calls_today() >= PER_USER_DAILY_CAP:
            st.error(
                f"You've reached today's limit ({PER_USER_DAILY_CAP} scoring calls) on the shared key. "
                "Enter your own API key in the sidebar for unlimited practice, or try again tomorrow."
            )
        elif not using_own_key and global_calls_today() >= GLOBAL_DAILY_CAP:
            st.error(
                "This app's shared daily AI budget has been used up by all visitors combined. "
                "Enter your own API key in the sidebar to keep practicing, or try again tomorrow."
            )
        else:
            with st.spinner("Scoring your response..."):
                try:
                    if not using_own_key:
                        record_session_call()
                        record_global_call()
                    result = score_writing(task["prompt"], task["type"], response_text, active_api_key)
                    st.session_state.result = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Scoring failed: {e}")

# --- Results view ---
else:
    result = st.session_state.result
    st.subheader(f"Overall CLB Band: {result['overallBand']}")

    st.markdown("### Scores by dimension")
    for d in result["dimensionScores"]:
        st.markdown(f"**{d['id'].replace('_', ' ').title()}: {d['score']}/12**")
        st.write(d["justification"])

    st.markdown("### Issues found and how to improve")
    if not result["issues"]:
        st.write("No major issues flagged.")
    for issue in result["issues"]:
        with st.container(border=True):
            st.markdown(f"*\"{issue['quote']}\"*")
            st.write(f"**Dimension:** {issue['dimension']}")
            st.write(f"**Why it lost marks:** {issue['explanation']}")
            st.write(f"**Improved version:** {issue['improvedVersion']}")

    st.markdown("### What would move you up one CLB level")
    st.write(result["levelUpAdvice"])

    if st.button("Try another task"):
        st.session_state.selected_task = None
        st.session_state.result = None
        st.rerun()
