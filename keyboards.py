# keyboards.py
# All keyboard layouts for the bot

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

# Main menu for regular users
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🧠 Practice Questions"), KeyboardButton("📘 Full SAT Mock")],
        [KeyboardButton("💡 SAT Tricks"), KeyboardButton("📊 My Progress")],
        [KeyboardButton("🔥 Daily Question"), KeyboardButton("ℹ️ Help")],
    ],
    resize_keyboard=True
)

# Admin menu
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("➕ Add Question"), KeyboardButton("🗑️ Delete Question")],
        [KeyboardButton("📝 View All Questions"), KeyboardButton("✏️ Edit Question")],
        [KeyboardButton("📊 User Statistics"), KeyboardButton("⚙️ Settings")],
        [KeyboardButton("⬅️ Back to Menu")]
    ],
    resize_keyboard=True
)

# Subject selection keyboard
subject_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("📐 Math", callback_data="subject:Math")],
    [InlineKeyboardButton("📚 English", callback_data="subject:English")]
])

# Remove keyboard (for tests)
remove_keyboard = ReplyKeyboardRemove()

def build_practice_keyboard(question_id):
    """Build keyboard for practice mode with hint and explanation"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("A", callback_data=f"practice:{question_id}:A"),
         InlineKeyboardButton("B", callback_data=f"practice:{question_id}:B")],
        [InlineKeyboardButton("C", callback_data=f"practice:{question_id}:C"),
         InlineKeyboardButton("D", callback_data=f"practice:{question_id}:D")],
        [InlineKeyboardButton("💡 Hint", callback_data=f"hint:{question_id}"),
         InlineKeyboardButton("📖 Explanation", callback_data=f"explain:{question_id}")],
        [InlineKeyboardButton("⏭ Next Question", callback_data="next_practice")]
    ])

def build_mock_keyboard(question_id, q_num, total):
    """Build keyboard for mock test (no hints)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("A", callback_data=f"mock:{question_id}:A"),
         InlineKeyboardButton("B", callback_data=f"mock:{question_id}:B")],
        [InlineKeyboardButton("C", callback_data=f"mock:{question_id}:C"),
         InlineKeyboardButton("D", callback_data=f"mock:{question_id}:D")],
        [InlineKeyboardButton(f"⏭ Next ({q_num}/{total})", callback_data="mock_next")]
    ])

def build_daily_keyboard(question_id, q_num, total):
    """Build keyboard for daily questions"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("A", callback_data=f"daily:{question_id}:A"),
         InlineKeyboardButton("B", callback_data=f"daily:{question_id}:B")],
        [InlineKeyboardButton("C", callback_data=f"daily:{question_id}:C"),
         InlineKeyboardButton("D", callback_data=f"daily:{question_id}:D")],
        [InlineKeyboardButton("💡 Hint", callback_data=f"hint:{question_id}"),
         InlineKeyboardButton("📖 Explanation", callback_data=f"explain:{question_id}")],
        [InlineKeyboardButton(f"⏭ Next ({q_num}/{total})", callback_data="daily_next")]
    ])

def build_admin_view_keyboard(questions, page=0, subject=None):
    """Build keyboard for viewing questions in admin panel"""
    buttons = []
    items_per_page = 10
    start = page * items_per_page
    end = start + items_per_page
    
    for q in questions[start:end]:
        q_id = q[0]
        q_text = q[1] if q[1] else "📸 Image Question"
        q_subject = q[10]
        buttons.append([InlineKeyboardButton(
            f"#{q_id} | {q_subject} | {q_text[:30]}...",
            callback_data=f"view_q:{q_id}"
        )])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page:{page-1}:{subject or 'all'}"))
    if end < len(questions):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page:{page+1}:{subject or 'all'}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_admin")])
    
    return InlineKeyboardMarkup(buttons)

def build_question_detail_keyboard(question_id):
    """Build keyboard for individual question view"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Edit", callback_data=f"edit_q:{question_id}"),
         InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_q:{question_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_list")]
    ])

def build_settings_keyboard():
    """Build keyboard for bot settings"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱️ Mock Timer Settings", callback_data="settings:timer")],
        [InlineKeyboardButton("📅 Daily Questions Count", callback_data="settings:daily")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_admin")]
    ])

def build_timer_keyboard():
    """Build keyboard for timer settings"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("30 sec", callback_data="timer:30"),
         InlineKeyboardButton("60 sec", callback_data="timer:60")],
        [InlineKeyboardButton("90 sec", callback_data="timer:90"),
         InlineKeyboardButton("120 sec", callback_data="timer:120")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings:back")]
    ])

def build_confirm_keyboard(action, item_id):
    """Build confirmation keyboard for deletions"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm:{action}:{item_id}"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")]
    ])
