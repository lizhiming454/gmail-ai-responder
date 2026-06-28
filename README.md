# 📧 Gmail AI Auto-Responder

> Automatically monitors your Gmail inbox and replies to emails using **OpenAI GPT-4o** — with a flexible rules engine to control which emails get replied to and how.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![Gmail API](https://img.shields.io/badge/Gmail-API-red)](https://developers.google.com/gmail/api)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- **Real-time inbox monitoring** — polls Gmail for new unread messages
- **AI-powered replies** — generates context-aware responses using OpenAI GPT
- **Flexible rule engine** — match by sender, subject keywords, or catch-all
- **Blacklist support** — skip no-reply, mailing lists, and spam automatically
- **Auto-labeling** — marks processed emails with a custom Gmail label
- **Daemon mode** — runs continuously on a configurable schedule
- **Fully configurable** — rules, prompts, model, and intervals via JSON + `.env`

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/lizhiming454/gmail-ai-responder.git
cd gmail-ai-responder
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Gmail API credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → Enable **Gmail API**
3. Go to **Credentials** → Create **OAuth 2.0 Client ID** (Desktop App)
4. Download `credentials.json` and place it in `config/`

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 5. Run it
```bash
# Run once
python main.py

# Run as a daemon (checks every 60 seconds)
python main.py --daemon
```

On first run, a browser window will open for Gmail OAuth2 authorization. After that, the token is cached in `config/token.json`.

---

## ⚙️ Configuration

### Rules engine (`config/rules.json`)

```json
{
  "rules": [
    {
      "name": "VIP clients",
      "match": { "from_contains": ["boss@bigcorp.com"], "subject_contains": [] },
      "system_prompt": "Reply warmly and helpfully. Keep replies under 150 words.",
      "priority": 1
    },
    {
      "name": "Default fallback",
      "match": { "from_contains": [], "subject_contains": [] },
      "system_prompt": "Write a polite, concise reply.",
      "priority": 99
    }
  ],
  "blacklist": {
    "from_contains": ["noreply@", "no-reply@"],
    "subject_contains": ["unsubscribe", "out of office"]
  }
}
```

### Environment variables (`.env`)

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_CREDENTIALS_FILE` | `config/credentials.json` | Path to OAuth2 credentials |
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Model to use for replies |
| `POLL_INTERVAL` | `60` | Seconds between inbox checks (daemon mode) |
| `PROCESSED_LABEL` | `AUTO_REPLIED` | Gmail label applied after reply |
| `MAX_PER_RUN` | `10` | Max emails processed per run |

---

## 📁 Project Structure

```
gmail-ai-responder/
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── config/
│   ├── credentials.json   # Gmail OAuth2 credentials (not in repo)
│   └── rules.json         # Reply rules configuration
├── core/
│   ├── gmail_client.py    # Gmail API wrapper
│   ├── ai_responder.py    # OpenAI integration
│   └── rule_engine.py     # Rules matching engine
└── logs/
    └── responder.log      # Application logs
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.
