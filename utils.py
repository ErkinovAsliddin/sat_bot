# utils.py
# Helper functions and utilities

from datetime import datetime
import config

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in config.ADMIN_IDS

def calculate_sat_score(correct, total):
    """Calculate SAT score based on correct answers"""
    if total == 0:
        return 200
    percentage = (correct / total) * 100
    score = int(200 + (percentage / 100) * 600)
    return score

def format_question_text(question_data):
    """Format question text for display"""
    q_id, question_text, image_file_id, opt_a, opt_b, opt_c, opt_d, correct, hint, explanation, subject, topic = question_data
    
    text = f"📚 Subject: {subject}\n"
    text += f"📖 Topic: {topic}\n\n"
    
    if question_text:
        text += f"{question_text}\n\n"
    
    text += f"A) {opt_a}\n"
    text += f"B) {opt_b}\n"
    text += f"C) {opt_c}\n"
    text += f"D) {opt_d}"
    
    return text

def get_current_date():
    """Get current date as string"""
    return datetime.now().strftime("%Y-%m-%d")

def format_stats(stats):
    """Format user statistics for display"""
    text = "📊 <b>Top Users Statistics</b>\n\n"
    
    for idx, (user_id, username, total, correct, streak) in enumerate(stats, 1):
        accuracy = (correct / total * 100) if total > 0 else 0
        text += f"{idx}. "
        if username:
            text += f"@{username}"
        else:
            text += f"User {user_id}"
        text += f"\n   📝 Attempts: {total} | ✅ Correct: {correct} ({accuracy:.1f}%)\n"
        text += f"   🔥 Streak: {streak}\n\n"
    
    return text

def format_progress(user_data):
    """Format individual user progress"""
    if not user_data:
        return "📊 No progress data yet. Start practicing to see your stats!"
    
    user_id, username, total, correct, streak, last_daily = user_data
    accuracy = (correct / total * 100) if total > 0 else 0
    
    text = f"📊 <b>Your Progress</b>\n\n"
    text += f"📝 Total Attempts: {total}\n"
    text += f"✅ Correct Answers: {correct}\n"
    text += f"📈 Accuracy: {accuracy:.1f}%\n"
    text += f"🔥 Current Streak: {streak}\n"
    
    if last_daily:
        text += f"📅 Last Daily: {last_daily}"
    
    return text

SAT_TRICKS = """
💡 <b>SAT Pro Tips & Tricks</b>

<b>📐 Math Section:</b>
1. <b>Plug In Numbers:</b> When solving algebraic problems, try plugging in simple numbers to test answer choices.

2. <b>Work Backwards:</b> Start with answer choices and work backwards - especially useful for word problems.

3. <b>Draw It Out:</b> Sketch diagrams for geometry problems, even if not provided.

4. <b>Look for Patterns:</b> SAT math often repeats question types - recognize patterns.

5. <b>Calculator Wisdom:</b> Use it strategically; some problems are faster without it.

6. <b>Check Units:</b> Always verify you're using the correct units in your answer.

<b>📚 English Section:</b>
1. <b>Read the Full Sentence:</b> Don't just focus on the underlined portion - context matters.

2. <b>Shorter is Better:</b> When in doubt, the most concise answer is often correct.

3. <b>Trust Your Ear:</b> Read it aloud in your head - if it sounds wrong, it probably is.

4. <b>Know Common Errors:</b>
   • Subject-verb agreement
   • Pronoun-antecedent agreement
   • Misplaced modifiers
   • Run-on sentences

5. <b>Punctuation Rules:</b>
   • Commas: Use for lists, after introductory phrases, with conjunctions
   • Semicolons: Join related independent clauses
   • Colons: Introduce lists or explanations

6. <b>Transition Words:</b> Pay attention to logic - "however," "moreover," "therefore" indicate specific relationships.

<b>⏱️ Time Management:</b>
• Spend ~1 minute per question
• Skip hard questions, come back later
• Don't spend >2 minutes on any single question
• Last 5 minutes: guess on remaining questions

<b>🎯 Test Day Strategy:</b>
• Read questions carefully - they often contain clues
• Eliminate obviously wrong answers first
• Never leave questions blank
• Trust your first instinct (unless you find an error)
• Stay calm - one hard question doesn't define your score

<b>📝 Practice Makes Perfect:</b>
• Review explanations for wrong answers
• Identify your weak topics and focus on them
• Take full-length practice tests regularly
• Analyze your mistakes to avoid repeating them

Good luck! 🍀
"""

def get_sat_tricks():
    """Return SAT tricks and tips"""
    return SAT_TRICKS

HELP_TEXT = """
ℹ️ <b>SAT Prep Bot - Help Guide</b>

<b>🎯 Main Features:</b>

<b>🧠 Practice Questions</b>
Practice unlimited questions by subject. Get instant feedback with hints and detailed explanations!

<b>📘 Full SAT Mock</b>
Take a timed 20-question mock test (10 Math + 10 English) to simulate real SAT conditions. Track your scores!

<b>🔥 Daily Question</b>
Get 3 fresh questions every day to maintain your practice streak.

<b>💡 SAT Tricks</b>
Access proven strategies and tips to boost your SAT score.

<b>📊 My Progress</b>
View your statistics, accuracy rate, and improvement over time.

<b>ℹ️ Help</b>
You're here! Get assistance anytime.

<b>👨‍💼 Admin Features:</b>
Admins can add/delete questions, view user stats, and manage bot settings.

<b>💬 Need More Help?</b>
Contact the admin: {admin_profiles}

Happy studying! 📚✨
"""

def get_help_text(admin_profiles=""):
    """Return help text with admin profiles"""
    return HELP_TEXT.format(admin_profiles=admin_profiles)

def get_admin_profiles():
    """Get formatted admin profiles"""
    profiles = []
    for admin_id in config.ADMIN_IDS:
        profiles.append(f"ID: {admin_id}")
    return "\n".join(profiles)
