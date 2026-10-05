# 📚 TNPSC தயாரிப்பு மையம் – Tamil Learning App

Sarvam AI (sarvam-105b) மாதிரியால் இயங்கும் தமிழ் போட்டித் தேர்வுக்கான கற்றல் இணையதளம் —
**இரு தேர்வுகள்**: TNPSC குரூப் 2 & 2A (முதல்நிலை) மற்றும் TNPSC உதவி பொறியாளர் (AE – EEE).

## மூன்று பிரிவுகள் (இரு தேர்வுகளுக்கும்)

| பிரிவு | இணைப்பு | விவரம் |
|---|---|---|
| 📖 கற்றல் | `/learn` | தேர்வு தேர்வாக → `/learn/tnpsc`, `/learn/ae`: பாடத்திட்ட அலகுகள் + AI தமிழ் குறிப்புகள் |
| 🗂️ வினாத்தாள்கள் | `/papers` | இரு பிரிவுகள்: குரூப் 2 வினாத்தாள்கள் + AE-EEE (2018–2025) வினாத்தாள்கள் – பார்க்க மட்டும் |
| 🤖 AI சந்தேகம் | `/chat` | இரு தேர்வுகளின் பாடத்திட்டமும் அறிந்த தமிழ் சாட்போட் + சரிபார்க்கப்பட்ட திருக்குறள் |

## இயக்கும் முறை

```
cd C:\Users\ADMIN\Desktop\Tamil
pip install -r requirements.txt
python app.py
```

Browser: http://127.0.0.1:5000

## குறிப்புகள் மீண்டும் உருவாக்க (இரு பாடத்திட்டங்களும்)

```
python scripts/generate_notes.py
```

## Routes

- `/`, `/learn`, `/learn/<track>`, `/learn/<track>/<part>/<unit>` (track: `tnpsc` | `ae`)
- `/papers`, `/papers/view/<filename>` (பார்க்க மட்டும் — பதிவேற்றம்/நீக்கம் இல்லை)
- `/chat`, `POST /api/chat`, `GET /api/kural/random`

## Files

- `app.py` — Flask routes, dual-track setup, chat API, Tirukkural verification
- `data/syllabus.json` — குரூப் 2/2A பாடத்திட்டம் (குறியீடு 495, 12.12.2024)
- `data/syllabus_ae.json` — AE-EEE பாடத்திட்டம் (10 அலகுகள், பட்டப்படிப்புத்தரம்)
- `data/notes/*.json` — AI தமிழ் குறிப்புகள் (ஒவ்வொரு அலகிற்கும்)
- `data/papers.json` — வினாத்தாள் பட்டியல் (track: `tnpsc` | `ae`)
- `data/tirukkural.json`, `tirukkural_detail.json` — 1330 குறள் + 133 அதிகாரம் (சரிபார்க்கப்பட்ட தரவு)
- `static/papers/` — PDF கோப்புகள் (குரூப் 2 × 2, AE-EEE × 7)
- `templates/` — base, home, learn, track, unit, papers, view_paper, chat
- `.env` — SARVAM_API_KEY (பகிர வேண்டாம்!)

## API

- `POST /api/chat` — {message, history} → {reply} (தமிழ் மட்டும்)
- `GET /api/kural/random` — சரிபார்க்கப்பட்ட திருக்குறள் (AI இல்லை)
