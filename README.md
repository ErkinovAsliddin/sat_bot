# 🎓 SAT Prep Bot

A Telegram bot for SAT preparation with practice questions, mock tests, and daily questions.

## Features

- 🧠 **Practice Questions** - Practice by subject (Math/English) with instant feedback
- 📘 **Full SAT Mock Tests** - Timed mock tests with scoring
- 🔥 **Daily Questions** - 3 questions daily to maintain your streak
- 💡 **SAT Tips & Tricks** - Expert strategies and techniques
- 📊 **Progress Tracking** - Track your performance and accuracy
- 👨‍💼 **Admin Panel** - Add/edit/delete questions and manage the bot

## Prerequisites

- Python 3.8+
- Telegram Bot Token (create at [@BotFather](https://t.me/botfather))

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd sat_bot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your bot token:
# BOT_API_TOKEN=your_token_here
# ADMIN_IDS=your_admin_id
```

## Running the Bot

### Local Development
```bash
python main.py
```

### Using Docker
```bash
docker build -t sat-bot .
docker run -e BOT_API_TOKEN=<your_token> sat-bot
```

## Project Structure

```
sat_bot/
├── main.py              # Entry point
├── config.py            # Configuration (uses .env)
├── handlers.py          # User command handlers
├── admin.py             # Admin panel functions
├── callbacks.py         # Inline button handlers
├── database.py          # SQLite database operations
├── keyboards.py         # Telegram keyboard layouts
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .gitignore           # Git ignore file
├── Dockerfile           # Docker configuration
└── README.md            # This file
```

## Usage

### For Users
1. Start the bot: `/start`
2. Choose from:
   - 🧠 Practice Questions
   - 📘 Full SAT Mock
   - 🔥 Daily Question
   - 💡 SAT Tricks
   - 📊 My Progress
   - ℹ️ Help

### For Admins
1. Start admin panel: `/admin`
2. Available actions:
   - ➕ Add Question
   - 🗑️ Delete Question
   - ✏️ Edit Question
   - 📝 View All Questions
   - 📊 User Statistics
   - ⚙️ Settings

## Adding Questions

Format: `Option A | Option B | Option C | Option D | Correct | Hint | Explanation | Topic`

Example:
```
12 | 15 | 18 | 20 | A | Add the numbers | 5+7=12 | Arithmetic
```

## Database

SQLite database (`sat_bot.db`) contains:
- Users - User profiles and statistics
- Questions - Question pool
- Attempts - User attempts and answers
- Mock Sessions - Mock test results
- Daily Questions - Daily question assignments

## Configuration

Edit `config.py` to modify:
- `MOCK_TOTAL_QUESTIONS` - Number of questions in mock test
- `MOCK_TIME_PER_QUESTION` - Seconds per question
- `DAILY_QUESTIONS_COUNT` - Daily questions per day

## Security

⚠️ **Important:**
- Never hardcode API tokens in code
- Use `.env` file for sensitive data
- Don't commit `.env` file to repository
- Rotate tokens if compromised

## Troubleshooting

### Bot not responding
- Check if token is correct
- Ensure internet connection
- Check logs for errors

### Questions not displaying
- Verify database has questions
- Check image file IDs are valid
- Review error logs

### Admin not working
- Verify admin ID in `ADMIN_IDS`
- Use `/admin` command
- Check admin permissions

## License

MIT License - feel free to use for personal/educational purposes

---

**Happy SAT Prep! 🚀📚**
