# ✦ Katacy

A pageant Q&A practice app built for competitors who want to train like it's the real thing.

Live at [katacy.com](https://katacy.com)

## Features

- **12 topics** — Women, Environment, Culture & Identity, Mental Health, Education, Technology & Social Media, Leadership, Pageantry, Peace & Global Issues, Youth, LGBTQIA+, General Personality
- **3 difficulty levels** — Easy, Medium, Hard
- **Read aloud** — questions spoken via text-to-speech
- **Countdown timer** — with color changes as time runs low and a bell at the end
- **Overtime counter** — counts up after time's up so you know how long you went over
- **Mobile-friendly** — responsive design with slide-in sidebar

## Running locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python katacy.py
```

Open `http://localhost:8080` in your browser.

## Tech stack

- **Flask** — backend and routing
- **edge-tts** — text-to-speech audio streaming
- **Vanilla HTML/CSS/JS** — no frontend framework
- **Render** — hosting
