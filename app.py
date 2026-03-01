import random
import time
import streamlit as st

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
        text-transform: uppercase;
    }

    /* Divider */
    hr { border-color: #e8e6de; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Question bank ──────────────────────────────────────────────────────────────
QUESTIONS = {
    "Women Empowerment": [
        "If you could change one systemic barrier that holds women back, what would it be and why?",
        "How do you personally define women's empowerment, and how do you live that definition every day?",
        "What advice would you give to a young girl who has been told she is 'too much' or 'not enough'?",
        "In what ways can men be better allies in the fight for gender equality?",
        "How do you balance ambition with the societal expectations placed on women?",
        "Who is a woman — historical or living — who changed the world quietly, and what can we learn from her?",
        "What does it mean to lead with both strength and compassion, and why does that matter for women in power?",
        "How can communities better support mothers who are also pursuing careers and personal dreams?",
        "If you were president for a day, what single policy would you implement to uplift women?",
        "How do you respond when your competence is questioned simply because of your gender?",
        "What role does education play in closing the gender gap, and how do we make it accessible to all girls?",
        "How can social media be used as a tool for women's empowerment rather than a source of comparison?",
    ],
    "Environment": [
        "What is one small daily habit every person can adopt that would collectively make a massive difference for our planet?",
        "How do you personally reconcile the convenience of modern life with the responsibility to protect the environment?",
        "If you could speak to world leaders about climate change, what is the one truth you would make them face?",
        "How can local communities take environmental action without waiting for national or global policy changes?",
        "What role should young people play in shaping the environmental decisions that will define their future?",
        "How do we make sustainability accessible to people who are focused on day-to-day survival?",
        "What is the connection between protecting the environment and protecting human rights?",
        "How can technology be both a cause of and a solution to our environmental crisis?",
        "What does leaving a healthy planet for future generations mean to you personally?",
        "If you had one year and unlimited resources to address a single environmental issue, what would you choose and why?",
        "How do we inspire environmental responsibility in children before it becomes an emergency for them?",
        "What is the most underrated environmental issue that deserves more public attention?",
    ],
    "Culture & Identity": [
        "How has your cultural background shaped the values you carry into every room you enter?",
        "What is one tradition from your heritage that you believe the whole world could benefit from?",
        "How do you navigate spaces where your identity is underrepresented or misunderstood?",
        "What does it mean to be proud of where you come from while still being open to growth and change?",
        "How can societies celebrate diversity without reducing people to stereotypes?",
        "If you could preserve one aspect of your culture for future generations, what would it be and why?",
        "How do language and storytelling shape the way a culture sees itself and its place in the world?",
        "What is the most important lesson your family or community taught you that schools never could?",
        "How do you define home — is it a place, a people, or something else entirely?",
        "In a world that is increasingly globalized, how do we keep local cultures from disappearing?",
        "How has encountering a culture different from your own changed the way you see yourself?",
        "What responsibility do public figures have in representing their culture with accuracy and dignity?",
    ],
    "General Personality": [
        "What is a failure you once experienced that turned out to be one of the greatest gifts of your life?",
        "If you could have dinner with anyone — living or historical — who would it be and what would you ask them?",
        "What is the bravest thing you have ever done, and what did it teach you about yourself?",
        "How do you stay grounded and true to yourself when the world is constantly telling you who to be?",
        "What does success mean to you, and has that definition changed as you have grown?",
        "If you had to describe yourself using only three words, which words would you choose and why?",
        "What is a cause you would give up everything for, and what drew you to it?",
        "How do you handle self-doubt, and what do you tell yourself on your hardest days?",
        "What is one thing most people do not know about you that you wish they did?",
        "If your life had a theme song, what would it be and what chapter of your life does it represent?",
        "What does kindness look like in action, and how do you practice it when it is inconvenient?",
        "How do you want to be remembered, and are you living in a way that reflects that today?",
    ],
    "Mental Health & Wellness": [
        "How do you think we can dismantle the stigma around mental health, especially in communities where it is still taboo?",
        "What does self-care mean to you beyond the surface level, and how do you practice it authentically?",
        "How has prioritizing your mental health made you a better person for those around you?",
        "What would you say to a young person who is silently struggling and afraid to ask for help?",
        "How can schools better prepare students to handle stress, anxiety, and emotional challenges?",
        "What is the relationship between physical health and mental well-being, and how do you nurture both?",
        "How do we build communities where people feel safe enough to be honest about their struggles?",
        "What role does rest and stillness play in a high-achieving life, and why is it often undervalued?",
        "How do you personally recover from burnout, and what signs tell you that you need to slow down?",
        "If you could change one thing about how society talks about mental health, what would it be?",
        "How do you maintain hope and positivity during periods of genuine hardship?",
        "What does it mean to be emotionally strong, and how is that different from simply suppressing your feelings?",
    ],
    "Education": [
        "If you could redesign the education system from scratch, what would be the one thing you would never leave out?",
        "How do we make quality education accessible to children in communities that have historically been left behind?",
        "What is something you taught yourself outside of school that has shaped who you are more than any classroom lesson?",
        "How can teachers be better supported so that they can better support their students?",
        "What is the difference between being educated and being truly prepared for life?",
        "How do we keep curiosity alive in children when traditional schooling can sometimes feel like it extinguishes it?",
        "What role does reading play in building empathy, and how can we encourage more young people to read?",
        "How should schools address the rise of AI and prepare students for a future we cannot fully predict?",
        "What does equal access to education mean to you, and how far are we from achieving it?",
        "How has a teacher, mentor, or coach changed the direction of your life?",
        "Why is it important to learn history honestly, even when parts of it are uncomfortable?",
        "How can parents and communities fill the gaps that formal education leaves behind?",
    ],
    "Technology & Social Media": [
        "How do we teach the next generation to use social media as a tool for good rather than a source of harm?",
        "What responsibility do tech companies have in protecting the mental health of their users?",
        "How has technology changed the way we connect with each other — and what have we lost in that shift?",
        "What does digital literacy mean, and why is it just as important as reading and writing today?",
        "How do you personally set boundaries with technology so that it serves you rather than controls you?",
        "What is the most dangerous misconception people have about social media and its influence on society?",
        "How can online platforms be redesigned to amplify kindness instead of outrage?",
        "What is the impact of constantly comparing ourselves to curated versions of other people's lives?",
        "How do we protect children from the harms of the internet without taking away their freedom to explore it?",
        "What role can social media play in amplifying voices that traditional media has historically silenced?",
        "If you could give every teenager one piece of advice about their online presence, what would it be?",
        "How do we balance innovation and progress in technology with ethics and human dignity?",
    ],
    "Leadership & Service": [
        "What is the difference between holding a title and truly leading, and which do you aspire to?",
        "How do you lead people who do not share your vision, and what have you learned from that challenge?",
        "What does servant leadership mean to you, and can you share a moment when you practiced it?",
        "How can young people start making an impact in their communities right now, without waiting until they are older?",
        "What is the hardest decision a leader ever has to make, and how do you prepare yourself for those moments?",
        "How do you build trust with people who have every reason not to trust institutions or authority?",
        "What is the most underrated quality in a great leader that people rarely talk about?",
        "How do you stay humble when success and recognition start to define how others see you?",
        "What does it mean to use your platform for something greater than yourself?",
        "If you were mentoring a future leader today, what is the first lesson you would teach them?",
        "How do you respond to criticism — and how do you tell the difference between feedback worth keeping and noise worth ignoring?",
        "What does community look like when it is truly led by the people it serves?",
    ],
    "Peace & Global Issues": [
        "If you could sit down with two opposing world leaders, what is the first thing you would ask them to agree on?",
        "How do ordinary people contribute to peace in a world that seems increasingly divided?",
        "What is the connection between poverty and conflict, and how do we address both at the same time?",
        "How do we raise a generation that chooses dialogue over division?",
        "What does global citizenship mean to you, and how do you practice it in your daily life?",
        "How can the stories of refugees and displaced people change the way we talk about borders and belonging?",
        "What is one global issue that you believe is not getting enough attention, and what would you do about it?",
        "How do we honor the lessons of history while still allowing nations and people to move forward?",
        "What role does empathy play in resolving conflict — and can it really be taught?",
        "How do you stay informed about world events without losing hope or becoming overwhelmed?",
        "What does justice look like in a world where not everyone starts from the same place?",
        "If peace were a daily practice, what would that look like in your own home, school, or community?",
    ],
}


# ── Session state defaults ─────────────────────────────────────────────────────
if "question" not in st.session_state:
    st.session_state.question = None
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("<h1>Pageant Q&A Practice</h1>", unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Train your confidence. Master the moment.</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Controls ───────────────────────────────────────────────────────────────────
col_topics, col_timer = st.columns([3, 2])

with col_topics:
    st.markdown(
        '<p style="color:#6b6963; font-size:0.8rem; letter-spacing:0.06em; '
        'text-transform:uppercase; margin-bottom:0.4rem;">Topics</p>',
        unsafe_allow_html=True,
    )
    selected_topics = [
        topic for topic in QUESTIONS
        if st.checkbox(topic, value=(topic == "General Personality"))
    ]

with col_timer:
    timer_on = st.toggle("Timer", value=False)
    if timer_on:
        timer_seconds = st.slider("Seconds", min_value=15, max_value=120, value=60, step=5)
    else:
        timer_seconds = 0

st.markdown("---")

# ── Question picker ────────────────────────────────────────────────────────────
def generate_question(topics: list) -> str:
    pool = [q for t in topics for q in QUESTIONS[t]]
    last = st.session_state.get("last_question")
    choices = [q for q in pool if q != last] or pool
    return random.choice(choices)


# ── Generate button ────────────────────────────────────────────────────────────
if st.button("✨ Generate New Question", use_container_width=True):
    if not selected_topics:
        st.warning("Select at least one topic to get a question.")
    else:
        st.session_state.question = generate_question(selected_topics)
        st.session_state.last_question = st.session_state.question
        st.session_state.timer_running = True

# ── Question card ──────────────────────────────────────────────────────────────
if st.session_state.question:
    st.markdown(
        f'<div class="question-card"><p>{st.session_state.question}</p></div>',
        unsafe_allow_html=True,
    )

    # ── Timer ──────────────────────────────────────────────────────────────────
    if timer_seconds > 0 and st.session_state.timer_running:
        timer_placeholder = st.empty()

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
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#6b6963; font-size:0.78rem;">'
    "Practice makes perfect &nbsp;·&nbsp; You've got this"
    "</p>",
    unsafe_allow_html=True,
)
