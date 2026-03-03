import asyncio
import base64
import io
import json
import os
import random
import time
import edge_tts
from mutagen.mp3 import MP3
import streamlit as st
import streamlit.components.v1 as components


async def _synthesize(text: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice="en-US-EmmaNeural", rate="-8%")
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()


def speak(text: str) -> tuple[bytes, float]:
    audio = asyncio.run(_synthesize(text))
    duration = MP3(io.BytesIO(audio)).info.length
    return audio, duration

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pageant Q&A Practice",
    page_icon="👑",
    layout="centered",
)

# ── Styles ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    html, body, [data-testid="stApp"] {
        background-color: #faf9f0;
        color: #131314;
        font-family: 'Inter', sans-serif;
    }

    /* hide the default Streamlit header/footer */
    #MainMenu, footer, header { visibility: hidden; }

    h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2.4rem;
        font-weight: 600;
        text-align: center;
        color: #131314;
        letter-spacing: -0.02em;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        text-align: center;
        color: #6b6963;
        font-size: 1rem;
        font-weight: 300;
        margin-bottom: 2rem;
    }

    /* Question card */
    .question-card {
        background: #ffffff;
        border: 1px solid #e8e6de;
        border-radius: 12px;
        padding: 2rem 2.4rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    .question-card p {
        font-size: 1.25rem;
        font-weight: 400;
        line-height: 1.75;
        color: #131314;
        margin: 0;
    }

    /* Timer display */
    .timer-display {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.02em;
        padding: 0.5rem 0;
    }

    .timer-label {
        text-align: center;
        font-size: 0.8rem;
        color: #6b6963;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: -0.5rem;
    }

    /* Streamlit button overrides */
    .stButton > button {
        background: #d97757;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 2rem;
        font-size: 0.95rem;
        font-weight: 600;
        width: 100%;
        letter-spacing: 0.01em;
        transition: opacity 0.2s;
    }
    .stButton > button:hover {
        opacity: 0.88;
        color: #ffffff;
        border: none;
    }

    /* Selectbox / radio labels */
    label, .stRadio label, .stSelectbox label {
        color: #6b6963 !important;
        font-size: 0.8rem;
        letter-spacing: 0.06em;
    }

    /* Divider */
    hr { border-color: #e8e6de; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Question bank (nested by difficulty) ───────────────────────────────────────
QUESTIONS = {
    "Women Empowerment": {
        "Easy": [
            "How do you personally define women's empowerment, and how do you live that definition every day?",
            "What advice would you give to a young girl who has been told she is 'too much' or 'not enough'?",
            "How do you respond when your competence is questioned simply because of your gender?",
            "How do you balance ambition with the societal expectations placed on women?",
        ],
        "Medium": [
            "Who is a woman — historical or living — who changed the world quietly, and what can we learn from her?",
            "What does it mean to lead with both strength and compassion, and why does that matter for women in power?",
            "How can communities better support mothers who are also pursuing careers and personal dreams?",
            "How can social media be used as a tool for women's empowerment rather than a source of comparison?",
        ],
        "Hard": [
            "If you could change one systemic barrier that holds women back, what would it be and why?",
            "In what ways can men be better allies in the fight for gender equality?",
            "If you were president for a day, what single policy would you implement to uplift women?",
            "What role does education play in closing the gender gap, and how do we make it accessible to all girls?",
        ],
    },
    "Environment": {
        "Easy": [
            "What is one small daily habit every person can adopt that would collectively make a massive difference for our planet?",
            "How do you personally reconcile the convenience of modern life with the responsibility to protect the environment?",
            "What does leaving a healthy planet for future generations mean to you personally?",
            "How do we inspire environmental responsibility in children before it becomes an emergency for them?",
        ],
        "Medium": [
            "How can local communities take environmental action without waiting for national or global policy changes?",
            "What role should young people play in shaping the environmental decisions that will define their future?",
            "How do we make sustainability accessible to people who are focused on day-to-day survival?",
            "What is the most underrated environmental issue that deserves more public attention?",
        ],
        "Hard": [
            "If you could speak to world leaders about climate change, what is the one truth you would make them face?",
            "What is the connection between protecting the environment and protecting human rights?",
            "How can technology be both a cause of and a solution to our environmental crisis?",
            "If you had one year and unlimited resources to address a single environmental issue, what would you choose and why?",
        ],
    },
    "Culture & Identity": {
        "Easy": [
            "How has your cultural background shaped the values you carry into every room you enter?",
            "What is one tradition from your heritage that you believe the whole world could benefit from?",
            "What is the most important lesson your family or community taught you that schools never could?",
            "How do you define home — is it a place, a people, or something else entirely?",
        ],
        "Medium": [
            "How do you navigate spaces where your identity is underrepresented or misunderstood?",
            "What does it mean to be proud of where you come from while still being open to growth and change?",
            "If you could preserve one aspect of your culture for future generations, what would it be and why?",
            "How has encountering a culture different from your own changed the way you see yourself?",
        ],
        "Hard": [
            "How can societies celebrate diversity without reducing people to stereotypes?",
            "How do language and storytelling shape the way a culture sees itself and its place in the world?",
            "In a world that is increasingly globalized, how do we keep local cultures from disappearing?",
            "What responsibility do public figures have in representing their culture with accuracy and dignity?",
        ],
    },
    "General Personality": {
        "Easy": [
            "If you could have dinner with anyone — living or historical — who would it be and what would you ask them?",
            "If you had to describe yourself using only three words, which words would you choose and why?",
            "What is one thing most people do not know about you that you wish they did?",
            "If your life had a theme song, what would it be and what chapter of your life does it represent?",
        ],
        "Medium": [
            "What is a failure you once experienced that turned out to be one of the greatest gifts of your life?",
            "What is the bravest thing you have ever done, and what did it teach you about yourself?",
            "How do you stay grounded and true to yourself when the world is constantly telling you who to be?",
            "How do you handle self-doubt, and what do you tell yourself on your hardest days?",
        ],
        "Hard": [
            "What does success mean to you, and has that definition changed as you have grown?",
            "What is a cause you would give up everything for, and what drew you to it?",
            "What does kindness look like in action, and how do you practice it when it is inconvenient?",
            "How do you want to be remembered, and are you living in a way that reflects that today?",
        ],
    },
    "Mental Health & Wellness": {
        "Easy": [
            "What does self-care mean to you beyond the surface level, and how do you practice it authentically?",
            "How has prioritizing your mental health made you a better person for those around you?",
            "How do you personally recover from burnout, and what signs tell you that you need to slow down?",
            "How do you maintain hope and positivity during periods of genuine hardship?",
        ],
        "Medium": [
            "What would you say to a young person who is silently struggling and afraid to ask for help?",
            "What is the relationship between physical health and mental well-being, and how do you nurture both?",
            "What role does rest and stillness play in a high-achieving life, and why is it often undervalued?",
            "What does it mean to be emotionally strong, and how is that different from simply suppressing your feelings?",
        ],
        "Hard": [
            "How do you think we can dismantle the stigma around mental health, especially in communities where it is still taboo?",
            "How can schools better prepare students to handle stress, anxiety, and emotional challenges?",
            "How do we build communities where people feel safe enough to be honest about their struggles?",
            "If you could change one thing about how society talks about mental health, what would it be?",
        ],
    },
    "Education": {
        "Easy": [
            "What is something you taught yourself outside of school that has shaped who you are more than any classroom lesson?",
            "What is the difference between being educated and being truly prepared for life?",
            "What role does reading play in building empathy, and how can we encourage more young people to read?",
            "How has a teacher, mentor, or coach changed the direction of your life?",
        ],
        "Medium": [
            "How can teachers be better supported so that they can better support their students?",
            "How do we keep curiosity alive in children when traditional schooling can sometimes feel like it extinguishes it?",
            "Why is it important to learn history honestly, even when parts of it are uncomfortable?",
            "How can parents and communities fill the gaps that formal education leaves behind?",
        ],
        "Hard": [
            "If you could redesign the education system from scratch, what would be the one thing you would never leave out?",
            "How do we make quality education accessible to children in communities that have historically been left behind?",
            "How should schools address the rise of AI and prepare students for a future we cannot fully predict?",
            "What does equal access to education mean to you, and how far are we from achieving it?",
        ],
    },
    "Technology & Social Media": {
        "Easy": [
            "How do you personally set boundaries with technology so that it serves you rather than controls you?",
            "What is the impact of constantly comparing ourselves to curated versions of other people's lives?",
            "If you could give every teenager one piece of advice about their online presence, what would it be?",
            "How has technology changed the way we connect with each other — and what have we lost in that shift?",
        ],
        "Medium": [
            "How do we teach the next generation to use social media as a tool for good rather than a source of harm?",
            "What does digital literacy mean, and why is it just as important as reading and writing today?",
            "What is the most dangerous misconception people have about social media and its influence on society?",
            "What role can social media play in amplifying voices that traditional media has historically silenced?",
        ],
        "Hard": [
            "What responsibility do tech companies have in protecting the mental health of their users?",
            "How can online platforms be redesigned to amplify kindness instead of outrage?",
            "How do we protect children from the harms of the internet without taking away their freedom to explore it?",
            "How do we balance innovation and progress in technology with ethics and human dignity?",
        ],
    },
    "Leadership & Service": {
        "Easy": [
            "What does servant leadership mean to you, and can you share a moment when you practiced it?",
            "How can young people start making an impact in their communities right now, without waiting until they are older?",
            "What is the most underrated quality in a great leader that people rarely talk about?",
            "What does it mean to use your platform for something greater than yourself?",
        ],
        "Medium": [
            "What is the difference between holding a title and truly leading, and which do you aspire to?",
            "How do you stay humble when success and recognition start to define how others see you?",
            "If you were mentoring a future leader today, what is the first lesson you would teach them?",
            "How do you respond to criticism — and how do you tell the difference between feedback worth keeping and noise worth ignoring?",
        ],
        "Hard": [
            "How do you lead people who do not share your vision, and what have you learned from that challenge?",
            "What is the hardest decision a leader ever has to make, and how do you prepare yourself for those moments?",
            "How do you build trust with people who have every reason not to trust institutions or authority?",
            "What does community look like when it is truly led by the people it serves?",
        ],
    },
    "Pageantry": {
        "Easy": [
            "Why do you want to compete in this pageant, and what does this moment mean to you personally?",
            "What does wearing a crown represent to you beyond the title itself?",
            "How have pageants shaped who you are and what you stand for today?",
            "What is one thing you would do on your very first day as a titleholder?",
        ],
        "Medium": [
            "What would your platform be during your reign, and why is that cause close to your heart?",
            "How would you use your title to create a lasting impact that outlives your reign?",
            "What qualities do you believe make a truly great titleholder beyond beauty and talent?",
            "How do you plan to show up for your community every single day that you wear the crown?",
        ],
        "Hard": [
            "How are pageants still relevant in today's world, and how would you defend their value to someone who disagrees?",
            "Why should you be the next winner, and what is it about you that this title cannot afford to miss?",
            "How can pageants evolve to become more inclusive, diverse, and representative of the world we actually live in?",
            "If you could redefine what it means to win a pageant for the next generation of contestants, what would that look like?",
        ],
    },
    "Peace & Global Issues": {
        "Easy": [
            "How do ordinary people contribute to peace in a world that seems increasingly divided?",
            "What does global citizenship mean to you, and how do you practice it in your daily life?",
            "How do you stay informed about world events without losing hope or becoming overwhelmed?",
            "If peace were a daily practice, what would that look like in your own home, school, or community?",
        ],
        "Medium": [
            "How do we raise a generation that chooses dialogue over division?",
            "How can the stories of refugees and displaced people change the way we talk about borders and belonging?",
            "What is one global issue that you believe is not getting enough attention, and what would you do about it?",
            "What role does empathy play in resolving conflict — and can it really be taught?",
        ],
        "Hard": [
            "If you could sit down with two opposing world leaders, what is the first thing you would ask them to agree on?",
            "What is the connection between poverty and conflict, and how do we address both at the same time?",
            "How do we honor the lessons of history while still allowing nations and people to move forward?",
            "What does justice look like in a world where not everyone starts from the same place?",
        ],
    },
    "Youth": {
        "Easy": [
            "What does it mean to be young in today's world, and how do you make the most of this chapter of your life?",
            "Who is a young person — past or present — who inspires you, and what can we learn from their story?",
            "What is one piece of advice you would give to a younger version of yourself?",
            "How do you balance the pressures of growing up with staying true to who you are?",
        ],
        "Medium": [
            "How can young people turn their passion into purpose before they even graduate?",
            "What does it mean to lead as a young person in a world that often underestimates your voice?",
            "How do we create spaces where young people feel safe to fail, learn, and try again?",
            "What is the most important issue facing young people today that adults are not taking seriously enough?",
        ],
        "Hard": [
            "How do we bridge the gap between generations so that young people's ideas are not just heard but actually implemented?",
            "What systemic changes would you make to give every young person — regardless of background — a fair start?",
            "How do we prepare the next generation to lead in a world that is changing faster than our institutions can keep up?",
            "What does it mean to be a young advocate for change without losing your joy, your rest, or yourself in the process?",
        ],
    },
}

# ── Load expanded question banks from JSON files ───────────────────────────────
_TOPIC_FILES = {
    "Women Empowerment":    "questions_women_empowerment.json",
    "Environment":          "questions_environment.json",
    "Culture & Identity":   "questions_culture_identity.json",
    "General Personality":  "questions_general_personality.json",
    "Mental Health & Wellness": "questions_mental_health.json",
    "Education":            "questions_education.json",
    "Technology & Social Media": "questions_technology.json",
    "Leadership & Service": "questions_leadership.json",
    "Pageantry":            "questions_pageantry.json",
    "Peace & Global Issues":"questions_peace.json",
    "Youth":                "questions_youth.json",
}
_BASE = os.path.dirname(__file__)
for _topic, _fname in _TOPIC_FILES.items():
    _path = os.path.join(_BASE, _fname)
    if os.path.exists(_path):
        with open(_path) as _f:
            QUESTIONS[_topic] = json.load(_f)

QUESTIONS = dict(sorted(QUESTIONS.items()))

# ── Session state defaults ─────────────────────────────────────────────────────
if "question" not in st.session_state:
    st.session_state.question = None
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None
if "tts_question" not in st.session_state:
    st.session_state.tts_question = None
if "tts_duration" not in st.session_state:
    st.session_state.tts_duration = 0.0

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("<h1>Pageant Q&A Practice</h1>", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
col_topics, col_right = st.columns([3, 2])

with col_topics:
    st.markdown(
        '<p style="color:#6b6963; font-size:0.8rem; letter-spacing:0.06em; '
        'margin-bottom:0.4rem;">Topics</p>',
        unsafe_allow_html=True,
    )
    selected_topics = [
        topic for topic in QUESTIONS
        if st.checkbox(topic, value=(topic == "General Personality"))
    ]

with col_right:
    st.markdown(
        '<p style="color:#6b6963; font-size:0.8rem; letter-spacing:0.06em; '
        'margin-bottom:0.4rem;">Difficulty</p>',
        unsafe_allow_html=True,
    )
    selected_difficulties = [
        lvl for lvl in ["Easy", "Medium", "Hard"]
        if st.checkbox(lvl, value=True)
    ]

    st.markdown("<br>", unsafe_allow_html=True)

    timer_on = st.toggle("Timer", value=False)
    if timer_on:
        timer_seconds = st.slider("Seconds", min_value=15, max_value=120, value=60, step=5)
    else:
        timer_seconds = 0

    read_aloud = st.toggle("Read aloud", value=False)

# ── Question picker ────────────────────────────────────────────────────────────
def generate_question(topics: list, difficulties: list) -> str:
    pool = [q for t in topics for lvl in difficulties for q in QUESTIONS[t][lvl]]
    last = st.session_state.get("last_question")
    choices = [q for q in pool if q != last] or pool
    return random.choice(choices)


# ── Generate button ────────────────────────────────────────────────────────────
if st.button("Generate New Question", use_container_width=True):
    if not selected_topics or not selected_difficulties:
        st.warning("Select at least one topic and one difficulty level.")
    else:
        st.session_state.question = generate_question(selected_topics, selected_difficulties)
        st.session_state.last_question = st.session_state.question
        st.session_state.timer_running = True

# ── Question card ──────────────────────────────────────────────────────────────
if st.session_state.question:
    st.markdown(
        f'<div class="question-card"><p>{st.session_state.question}</p></div>',
        unsafe_allow_html=True,
    )

    if read_aloud:
        if st.session_state.tts_question != st.session_state.question:
            audio, duration = speak(st.session_state.question)
            st.session_state.tts_audio = audio
            st.session_state.tts_duration = duration
            st.session_state.tts_question = st.session_state.question
        audio_b64 = base64.b64encode(st.session_state.tts_audio).decode()
        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <style>
          body {{ margin: 0; padding: 0; background: transparent; }}
          .player {{
            display: flex; align-items: center; gap: 12px;
            padding: 0.6rem 0;
          }}
          #btn {{
            width: 36px; height: 36px; border-radius: 50%;
            border: 1.5px solid #d97757; background: transparent;
            color: #d97757; font-size: 13px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
          }}
          #btn:hover {{ background: #d97757; color: #fff; }}
          #bar {{
            flex: 1; height: 3px; background: #e8e6de;
            border-radius: 999px; cursor: pointer; position: relative;
          }}
          #progress {{
            height: 100%; background: #d97757;
            border-radius: 999px; width: 0%;
          }}
          #time {{ font-size: 0.75rem; color: #6b6963; white-space: nowrap; font-family: 'Inter', sans-serif; letter-spacing: 0.02em; }}
        </style>
        <div class="player">
          <button id="btn">▶</button>
          <div id="bar"><div id="progress"></div></div>
          <span id="time">0:00</span>
        </div>
        <audio id="audio" autoplay>
          <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <script>
          var a = document.getElementById('audio');
          var btn = document.getElementById('btn');
          var prog = document.getElementById('progress');
          var timeEl = document.getElementById('time');
          var bar = document.getElementById('bar');
          a.onplay = function() {{ btn.textContent = '⏸'; }};
          a.onpause = function() {{ btn.textContent = '▶'; }};
          a.ontimeupdate = function() {{
            var pct = (a.currentTime / a.duration) * 100 || 0;
            prog.style.width = pct + '%';
            var s = Math.floor(a.currentTime);
            timeEl.textContent = Math.floor(s/60) + ':' + ('0'+(s%60)).slice(-2);
          }};
          a.onended = function() {{ btn.textContent = '▶'; }};
          btn.onclick = function() {{ a.paused ? a.play() : a.pause(); }};
          bar.onclick = function(e) {{
            var rect = bar.getBoundingClientRect();
            a.currentTime = ((e.clientX - rect.left) / rect.width) * a.duration;
          }};
        </script>
        """, height=60)

    # ── Timer ──────────────────────────────────────────────────────────────────
    if timer_seconds > 0 and st.session_state.timer_running:
        timer_placeholder = st.empty()

        if read_aloud and st.session_state.tts_duration > 0:
            time.sleep(st.session_state.tts_duration)

        for remaining in range(timer_seconds, -1, -1):
            if remaining > 10:
                color = "#d97757"   # terracotta
            elif remaining > 5:
                color = "#f97316"   # orange
            else:
                color = "#ef4444"   # red

            if remaining == 0:
                timer_placeholder.markdown(
                    '<div class="timer-display" style="color:#ef4444;">TIME\'S UP!</div>'
                    '<p class="timer-label">Great job — reset and go again</p>',
                    unsafe_allow_html=True,
                )
                components.html(
                    """<script>
                    (function() {
                        var ctx = new (window.AudioContext || window.webkitAudioContext)();
                        var now = ctx.currentTime;
                        [[1318.51, 0.5, 4.0], [1318.51 * 2.756, 0.14, 1.8], [659.25, 0.18, 3.0]].forEach(function(p) {
                            var osc = ctx.createOscillator();
                            var g = ctx.createGain();
                            osc.connect(g); g.connect(ctx.destination);
                            osc.type = 'sine'; osc.frequency.value = p[0];
                            g.gain.setValueAtTime(p[1], now);
                            g.gain.exponentialRampToValueAtTime(0.001, now + p[2]);
                            osc.start(now); osc.stop(now + p[2]);
                        });
                    })();
                    </script>""",
                    height=0,
                )
            else:
                mins = remaining // 60
                secs = remaining % 60
                display = f"{mins}:{secs:02d}" if mins else f"0:{secs:02d}"
                timer_placeholder.markdown(
                    f'<div class="timer-display" style="color:{color};">{display}</div>'
                    '<p class="timer-label">Time remaining</p>',
                    unsafe_allow_html=True,
                )
                time.sleep(1)

        st.session_state.timer_running = False

# ── Footer ─────────────────────────────────────────────────────────────────────
