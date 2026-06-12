# admin.py
# Admin panel and administrative functions

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from keyboards import *
from utils import *
import config

# Conversation states
ADD_SUBJECT, ADD_QUESTION, ADD_IMAGE, ADD_OPTIONS = range(4)
DELETE_Q_ID = range(1)
EDIT_SELECT, EDIT_FIELD, EDIT_VALUE = range(3)
SETTINGS_TIMER = range(1)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ You don't have admin access.")
        return
    
    admin_text = f"""
👨‍💼 <b>Admin Panel</b>

Welcome, Admin!

<b>Available Actions:</b>
• ➕ Add Question - Add new questions with images
• 🗑️ Delete Question - Remove questions
• 📝 View All Questions - Browse all questions
• ✏️ Edit Question - Modify existing questions
• 📊 User Statistics - View user performance
• ⚙️ Settings - Configure bot settings

Use the buttons below to manage the bot.
"""
    
    await update.message.reply_text(
        admin_text,
        parse_mode='HTML',
        reply_markup=admin_menu
    )

# ===== ADD QUESTION =====
async def add_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add question conversation"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "➕ <b>Add New Question</b>\n\nSelect subject:",
        parse_mode='HTML',
        reply_markup=subject_menu
    )
    return ADD_SUBJECT

async def add_question_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subject selection"""
    query = update.callback_query
    await query.answer()
    
    subject = query.data.split(':')[1]
    context.user_data['add_subject'] = subject
    
    await query.message.edit_text(
        f"📐 <b>Adding {subject} Question</b>\n\n"
        f"Step 1️⃣: Send the question text\n"
        f"(or type 'skip' if you only want to use an image)",
        parse_mode='HTML'
    )
    return ADD_QUESTION

async def add_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive question text"""
    text = update.message.text
    
    if text.lower() == 'skip':
        context.user_data['add_question'] = ""
        await update.message.reply_text("⏭ Skipped text")
    else:
        context.user_data['add_question'] = text
        await update.message.reply_text("✅ Question text saved")
    
    await update.message.reply_text(
        "Step 2️⃣: Send the question image\n"
        "(or type 'skip' for text-only question)"
    )
    return ADD_IMAGE

async def add_question_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive question image"""
    if update.message.photo:
        photo = update.message.photo[-1]
        context.user_data['add_image'] = photo.file_id
        await update.message.reply_text("✅ Image saved!")
    else:
        context.user_data['add_image'] = None
        await update.message.reply_text("⏭ No image")
    
    subject = context.user_data.get('add_subject', 'Math')
    
    await update.message.reply_text(
        f"Step 3️⃣: Send all options and details\n\n"
        f"<b>Format:</b>\n"
        f"<code>OptionA | OptionB | OptionC | OptionD | Correct | Hint | Explanation | Topic</code>\n\n"
        f"<b>Example for {subject}:</b>\n" +
        (f"<code>12 | 15 | 18 | 20 | A | Add the numbers | 5+7=12 | Arithmetic</code>" 
         if subject == "Math" else
         f"<code>go | goes | going | gone | B | Check verb | Subject-verb agreement | Grammar</code>"),
        parse_mode='HTML'
    )
    return ADD_OPTIONS

async def save_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the complete question"""
    parts = [p.strip() for p in update.message.text.split('|')]
    
    if len(parts) != 8:
        await update.message.reply_text(
            f"❌ Wrong format! You provided {len(parts)} parts, need 8.\n\n"
            f"Format: OptionA | OptionB | OptionC | OptionD | Correct | Hint | Explanation | Topic"
        )
        return ADD_OPTIONS
    
    if parts[4].upper() not in ['A', 'B', 'C', 'D']:
        await update.message.reply_text("❌ Correct option must be A, B, C, or D!")
        return ADD_OPTIONS
    
    question_text = context.user_data.get('add_question', '')
    image_id = context.user_data.get('add_image')
    subject = context.user_data.get('add_subject', 'Math')
    
    question_id = db.add_question(
        question_text, image_id,
        parts[0], parts[1], parts[2], parts[3],
        parts[4].upper(), parts[5], parts[6],
        subject, parts[7]
    )
    
    await update.message.reply_text(
        f"✅ <b>Question #{question_id} Added Successfully!</b>\n\n"
        f"📚 Subject: {subject}\n"
        f"📖 Topic: {parts[7]}\n"
        f"{'📸 With image' if image_id else '📄 Text only'}\n"
        f"✅ Correct answer: {parts[4].upper()}",
        parse_mode='HTML',
        reply_markup=admin_menu
    )
    
    context.user_data.clear()
    return ConversationHandler.END

# ===== DELETE QUESTION =====
async def delete_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start delete question"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🗑️ <b>Delete Question</b>\n\n"
        "Send the question ID to delete.\n"
        "Use 'View All Questions' to see IDs.\n\n"
        "Type 'cancel' to abort.",
        parse_mode='HTML'
    )
    return DELETE_Q_ID

async def delete_question_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and delete question"""
    text = update.message.text
    
    if text.lower() == 'cancel':
        await update.message.reply_text("❌ Cancelled", reply_markup=admin_menu)
        return ConversationHandler.END
    
    try:
        qid = int(text)
        question = db.get_question_by_id(qid)
        
        if not question:
            await update.message.reply_text(
                "❌ Question not found!",
                reply_markup=admin_menu
            )
            return ConversationHandler.END
        
        # Show question details and confirm
        q_text = question[1] if question[1] else "📸 Image Question"
        
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_del:{qid}"),
             InlineKeyboardButton("❌ Cancel", callback_data="cancel_del")]
        ])
        
        await update.message.reply_text(
            f"⚠️ <b>Confirm Deletion</b>\n\n"
            f"ID: #{qid}\n"
            f"Subject: {question[10]}\n"
            f"Question: {q_text[:100]}...\n\n"
            f"Are you sure you want to delete this question?",
            parse_mode='HTML',
            reply_markup=keyboard
        )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid ID. Please send a number.",
            reply_markup=admin_menu
        )
        return DELETE_Q_ID

# ===== VIEW QUESTIONS =====
async def view_all_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all questions with pagination"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    
    questions = db.get_all_questions()
    
    if not questions:
        await update.message.reply_text(
            "📝 No questions in database yet.",
            reply_markup=admin_menu
        )
        return
    
    # Show filter options
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📐 Math Only", callback_data="filter:Math"),
         InlineKeyboardButton("📚 English Only", callback_data="filter:English")],
        [InlineKeyboardButton("📋 All Questions", callback_data="filter:All")]
    ])
    
    await update.message.reply_text(
        f"📝 <b>Total Questions: {len(questions)}</b>\n\n"
        f"Select filter:",
        parse_mode='HTML',
        reply_markup=keyboard
    )

async def show_questions_page(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                             subject=None, page=0):
    """Show paginated questions"""
    query = update.callback_query
    
    if subject and subject != 'All':
        questions = db.get_all_questions(subject)
    else:
        questions = db.get_all_questions()
    
    if not questions:
        await query.answer("No questions found!")
        return
    
    items_per_page = 10
    start = page * items_per_page
    end = start + items_per_page
    page_questions = questions[start:end]
    
    text = f"📝 <b>Questions ({start+1}-{min(end, len(questions))} of {len(questions)})</b>\n\n"
    
    for q in page_questions:
        q_id = q[0]
        q_text = q[1] if q[1] else "📸 Image"
        q_subject = q[10]
        q_topic = q[11]
        text += f"#{q_id} | {q_subject} | {q_topic}\n{q_text[:50]}...\n\n"
    
    # Build navigation keyboard
    buttons = []
    nav_row = []
    
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"qpage:{page-1}:{subject or 'All'}"))
    if end < len(questions):
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"qpage:{page+1}:{subject or 'All'}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_admin")])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await query.message.edit_text(
        text,
        parse_mode='HTML',
        reply_markup=keyboard
    )

# ===== EDIT QUESTION =====
async def edit_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start edit question"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "✏️ <b>Edit Question</b>\n\n"
        "Send the question ID to edit.\n"
        "Type 'cancel' to abort.",
        parse_mode='HTML'
    )
    return EDIT_SELECT

async def edit_question_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select question to edit"""
    text = update.message.text
    
    if text.lower() == 'cancel':
        await update.message.reply_text("❌ Cancelled", reply_markup=admin_menu)
        return ConversationHandler.END
    
    try:
        qid = int(text)
        question = db.get_question_by_id(qid)
        
        if not question:
            await update.message.reply_text("❌ Question not found!")
            return EDIT_SELECT
        
        context.user_data['edit_qid'] = qid
        context.user_data['edit_question'] = question
        
        q_text = question[1] if question[1] else "📸 Image only"
        
        await update.message.reply_text(
            f"📝 <b>Question #{qid}</b>\n\n"
            f"Subject: {question[10]}\n"
            f"Topic: {question[11]}\n"
            f"Question: {q_text}\n\n"
            f"A) {question[3]}\n"
            f"B) {question[4]}\n"
            f"C) {question[5]}\n"
            f"D) {question[6]}\n\n"
            f"Correct: {question[7]}\n"
            f"Hint: {question[8]}\n"
            f"Explanation: {question[9]}\n\n"
            f"What would you like to edit?\n"
            f"Reply with: <code>hint</code>, <code>explanation</code>, or <code>cancel</code>",
            parse_mode='HTML'
        )
        return EDIT_FIELD
        
    except ValueError:
        await update.message.reply_text("❌ Invalid ID")
        return EDIT_SELECT

async def edit_question_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select field to edit"""
    field = update.message.text.lower()
    
    if field == 'cancel':
        await update.message.reply_text("❌ Cancelled", reply_markup=admin_menu)
        context.user_data.clear()
        return ConversationHandler.END
    
    if field not in ['hint', 'explanation']:
        await update.message.reply_text(
            "❌ Invalid field. Choose: <code>hint</code> or <code>explanation</code>",
            parse_mode='HTML'
        )
        return EDIT_FIELD
    
    context.user_data['edit_field'] = field
    
    await update.message.reply_text(
        f"✏️ Enter new <b>{field}</b>:",
        parse_mode='HTML'
    )
    return EDIT_VALUE

async def edit_question_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save edited question"""
    new_value = update.message.text
    qid = context.user_data.get('edit_qid')
    field = context.user_data.get('edit_field')
    question = context.user_data.get('edit_question')
    
    if field == 'hint':
        db.update_hint_explanation(qid, new_value, question[9])
    else:  # explanation
        db.update_hint_explanation(qid, question[8], new_value)
    
    await update.message.reply_text(
        f"✅ Question #{qid} updated successfully!\n"
        f"Updated {field}: {new_value}",
        reply_markup=admin_menu
    )
    
    context.user_data.clear()
    return ConversationHandler.END

# ===== USER STATISTICS =====
async def user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    
    stats = db.get_user_stats()
    
    if not stats:
        await update.message.reply_text(
            "📊 No user activity yet.",
            reply_markup=admin_menu
        )
        return
    
    stats_text = format_stats(stats)
    
    await update.message.reply_text(
        stats_text,
        parse_mode='HTML',
        reply_markup=admin_menu
    )

# ===== SETTINGS =====
async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    
    await update.message.reply_text(
        f"⚙️ <b>Bot Settings</b>\n\n"
        f"Current Settings:\n"
        f"• Mock Timer: {config.MOCK_TIME_PER_QUESTION}s per question\n"
        f"• Daily Questions: {config.DAILY_QUESTIONS_COUNT} per day\n\n"
        f"Select setting to change:",
        parse_mode='HTML',
        reply_markup=build_settings_keyboard()
    )

async def change_timer_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change timer settings"""
    query = update.callback_query
    await query.answer()
    
    await query.message.edit_text(
        "⏱️ <b>Mock Test Timer</b>\n\n"
        "Select time per question:",
        parse_mode='HTML',
        reply_markup=build_timer_keyboard()
    )
