import asyncio
import io
import json
import os
import queue
import random
import threading

import edge_tts
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

# ── TTS streaming ──────────────────────────────────────────────────────────────

def stream_tts(text: str):
    """Yield MP3 audio chunks as they arrive from edge-tts."""
    chunk_queue = queue.Queue()

    def run():
        async def _run():
            communicate = edge_tts.Communicate(text, voice="en-US-EmmaNeural", rate="-8%")
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunk_queue.put(chunk["data"])
            chunk_queue.put(None)
        asyncio.run(_run())

    t = threading.Thread(target=run, daemon=True)
    t.start()

    while True:
        chunk = chunk_queue.get()
        if chunk is None:
            break
        yield chunk


# ── Question bank (fallback) ───────────────────────────────────────────────────
QUESTIONS = {
    "Women": {
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
    "Mental Health": {
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
    "Leadership": {
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
    "LGBTQIA+": {
        "Easy": [
            "How do you define love, and why do you believe every person deserves to experience it freely?",
            "What does inclusion mean to you in your everyday life?",
        ],
        "Medium": [
            "What is the difference between tolerance and genuine acceptance, and why does that distinction matter?",
            "How can allies move beyond passive support to active, meaningful advocacy?",
        ],
        "Hard": [
            "What systemic changes would you prioritize to reduce the disproportionately high rates of homelessness among LGBTQIA+ youth?",
            "What is the long-term cost to society when any group of people is systematically excluded from full participation in civic life?",
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
    "Women":        "questions_women_empowerment.json",
    "Environment":              "questions_environment.json",
    "Culture & Identity":       "questions_culture_identity.json",
    "General Personality":      "questions_general_personality.json",
    "Mental Health": "questions_mental_health.json",
    "Education":                "questions_education.json",
    "Technology & Social Media":"questions_technology.json",
    "Leadership":     "questions_leadership.json",
    "Pageantry":                "questions_pageantry.json",
    "Peace & Global Issues":    "questions_peace.json",
    "Youth":                    "questions_youth.json",
    "LGBTQIA+":                 "questions_lgbtq.json",
}
_BASE = os.path.dirname(__file__)
for _topic, _fname in _TOPIC_FILES.items():
    _path = os.path.join(_BASE, _fname)
    if os.path.exists(_path):
        with open(_path) as _f:
            QUESTIONS[_topic] = json.load(_f)

QUESTIONS = dict(sorted(QUESTIONS.items()))
TOPICS = list(QUESTIONS.keys())


# ── Routes ─────────────────────────────────────────────────────────────────────

def get_version():
    # Use Render's built-in commit SHA env var, fallback to local git
    sha = os.environ.get("RENDER_GIT_COMMIT", "")
    if sha:
        return sha[:7]
    try:
        import subprocess
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "dev"

VERSION = get_version()

@app.route("/")
def index():
    return render_template("index.html", topics=TOPICS, version=VERSION)


@app.route("/question", methods=["POST"])
def question():
    data = request.get_json()
    topics = data.get("topics", [])
    difficulties = data.get("difficulties", [])
    last = data.get("last", "")

    if not topics or not difficulties:
        return jsonify({"error": "Select at least one topic and difficulty."}), 400

    pool = [
        q
        for t in topics if t in QUESTIONS
        for lvl in difficulties if lvl in QUESTIONS[t]
        for q in QUESTIONS[t][lvl]
    ]
    if not pool:
        return jsonify({"error": "No questions found for the selected options."}), 400

    choices = [q for q in pool if q != last] or pool
    return jsonify({"question": random.choice(choices)})


@app.route("/speak")
def speak():
    text = request.args.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400

    return Response(stream_tts(text), mimetype="audio/mpeg")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
