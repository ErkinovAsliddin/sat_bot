# callbacks.py
# Callback query handlers for inline buttons

from telegram import Update
from telegram.ext import ContextTypes
from database import db
from keyboards import *
from utils import *
from handlers import send_question, show_next_mock_question, show_next_daily_question
import config

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback handler for all inline buttons"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    context.user_data['user_id'] = user_id
    
    # Subject selection
    if data.startswith("subject:"):
        subject = data.split(':')[1]
        
        # Check if in add question mode
        if context.user_data.get('adding_question'):
            from admin import add_question_subject
            return await add_question_subject(update, context)
        else:
            # Practice mode
            from handlers import start_practice_subject
            return await start_practice_subject(update, context, subject)
    
    # Practice mode answers
    elif data.startswith("practice:"):
        await handle_practice_answer(update, context)
    
    # Mock test answers
    elif data.startswith("mock:"):
        await handle_mock_answer(update, context)
    
    # Daily question answers
    elif data.startswith("daily:"):
        await handle_daily_answer(update, context)
    
    # Hint request
    elif data.startswith("hint:"):
        await show_hint(update, context)
    
    # Explanation request
    elif data.startswith("explain:"):
        await show_explanation(update, context)
    
    # Next practice question
    elif data == "next_practice":
        await next_practice_question(update, context)
    
    # Next mock question
    elif data == "mock_next":
        await advance_mock_test(update, context)
    
    # Next daily question
    elif data == "daily_next":
        await advance_daily_questions(update, context)
    
    # Admin callbacks
    elif data.startswith("filter:"):
        await handle_filter_questions(update, context)
    
    elif data.startswith("qpage:"):
        await handle_question_page(update, context)
    
    elif data.startswith("confirm_del:"):
        await confirm_delete_question(update, context)
    
    elif data == "cancel_del":
        await query.message.edit_text(
            "❌ Deletion cancelled",
            reply_markup=None
        )
        await query.message.reply_text("Back to admin panel", reply_markup=admin_menu)
    
    elif data == "back_admin":
        await query.message.delete()
        await query.message.reply_text(
            "👨‍💼 Admin Panel",
            reply_markup=admin_menu
        )
    
    elif data.startswith("settings:"):
        await handle_settings_callback(update, context)
    
    elif data.startswith("timer:"):
        await update_timer_setting(update, context)

async def handle_practice_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answer in practice mode"""
    query = update.callback_query
    data = query.data
    
    _, question_id, user_answer = data.split(':')
    question_id = int(question_id)
    
    question = db.get_question_by_id(question_id)
    if not question:
        await query.message.reply_text("❌ Question not found")
        return
    
    correct_answer = question[7]
    is_correct = user_answer == correct_answer
    
    # Record attempt
    user_id = update.effective_user.id
    db.record_attempt(user_id, question_id, user_answer, is_correct)
    db.update_user_stats(user_id, is_correct)
    
    # Show result
    result_emoji = "✅" if is_correct else "❌"
    result_text = f"\n\n{result_emoji} <b>{'Correct!' if is_correct else 'Incorrect!'}</b>\n"
    result_text += f"Your answer: {user_answer}\n"
    result_text += f"Correct answer: {correct_answer}\n"
    
    try:
        await query.message.edit_caption(
            caption=query.message.caption + result_text,
            reply_markup=build_practice_keyboard(question_id),
            parse_mode='HTML'
        )
    except:
        await query.message.edit_text(
            text=query.message.text + result_text,
            reply_markup=build_practice_keyboard(question_id),
            parse_mode='HTML'
        )

async def handle_mock_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answer in mock test mode"""
    query = update.callback_query
    data = query.data
    
    _, question_id, user_answer = data.split(':')
    question_id = int(question_id)
    
    # Cancel timer
    current_jobs = context.job_queue.get_jobs_by_name(f"mock_timer_{query.message.chat.id}")
    for job in current_jobs:
        job.schedule_removal()
    
    question = db.get_question_by_id(question_id)
    correct_answer = question[7]
    is_correct = user_answer == correct_answer
    
    # Store answer
    answers = context.user_data.get('mock_answers', {})
    answers[question_id] = user_answer
    context.user_data['mock_answers'] = answers
    
    if is_correct:
        context.user_data['mock_correct'] = context.user_data.get('mock_correct', 0) + 1
    
    # Record attempt
    user_id = update.effective_user.id
    db.record_attempt(user_id, question_id, user_answer, is_correct)
    
    await query.message.reply_text(
        f"{'✅' if is_correct else '❌'} Answer recorded!"
    )
    
    # Move to next question
    context.user_data['mock_current'] = context.user_data.get('mock_current', 0) + 1
    
    import asyncio
    await asyncio.sleep(1)
    await show_next_mock_question(query.message.chat.id, context)

async def handle_daily_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answer in daily question mode"""
    query = update.callback_query
    data = query.data
    
    _, question_id, user_answer = data.split(':')
    question_id = int(question_id)
    
    question = db.get_question_by_id(question_id)
    correct_answer = question[7]
    is_correct = user_answer == correct_answer
    
    # Record attempt
    user_id = update.effective_user.id
    db.record_attempt(user_id, question_id, user_answer, is_correct)
    db.update_user_stats(user_id, is_correct)
    
    if is_correct:
        context.user_data['daily_correct'] = context.user_data.get('daily_correct', 0) + 1
    
    # Show result
    result_text = f"\n\n{'✅ Correct!' if is_correct else '❌ Incorrect!'}\n"
    result_text += f"Answer: {correct_answer}"
    
    try:
        await query.message.edit_caption(
            caption=query.message.caption + result_text,
            reply_markup=None,
            parse_mode='HTML'
        )
    except:
        await query.message.edit_text(
            text=query.message.text + result_text,
            reply_markup=None,
            parse_mode='HTML'
        )
    
    # Auto-advance after 2 seconds
    import asyncio
    await asyncio.sleep(2)
    
    context.user_data['daily_current'] = context.user_data.get('daily_current', 0) + 1
    await show_next_daily_question(query.message.chat.id, context)

async def show_hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hint for current question"""
    query = update.callback_query
    question_id = int(query.data.split(':')[1])
    
    question = db.get_question_by_id(question_id)
    if question and question[8]:
        await query.answer(f"💡 Hint: {question[8]}", show_alert=True)
    else:
        await query.answer("No hint available", show_alert=True)

async def show_explanation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show explanation for current question"""
    query = update.callback_query
    question_id = int(query.data.split(':')[1])
    
    question = db.get_question_by_id(question_id)
    if question and question[9]:
        await query.answer(f"📖 Explanation: {question[9]}", show_alert=True)
    else:
        await query.answer("No explanation available", show_alert=True)

async def next_practice_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Load next practice question"""
    query = update.callback_query
    
    subject = context.user_data.get('current_subject')
    current_q_id = context.user_data.get('current_question')
    
    question = db.get_random_question(subject=subject, exclude_id=current_q_id)
    
    if not question:
        await query.message.reply_text(
            "No more questions available!",
            reply_markup=main_menu
        )
        context.user_data.clear()
        return
    
    context.user_data['current_question'] = question[0]
    
    await send_question(context, query.message.chat.id, question,
                       build_practice_keyboard(question[0]), query.message.message_id)

async def advance_mock_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Advance to next mock test question"""
    query = update.callback_query
    
    # Cancel timer
    current_jobs = context.job_queue.get_jobs_by_name(f"mock_timer_{query.message.chat.id}")
    for job in current_jobs:
        job.schedule_removal()
    
    current_idx = context.user_data.get('mock_current', 0)
    context.user_data['mock_current'] = current_idx + 1
    
    await query.message.delete()
    await show_next_mock_question(query.message.chat.id, context)

async def advance_daily_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Advance to next daily question"""
    query = update.callback_query
    
    current_idx = context.user_data.get('daily_current', 0)
    context.user_data['daily_current'] = current_idx + 1
    
    await query.message.delete()
    await show_next_daily_question(query.message.chat.id, context)

# ===== ADMIN CALLBACKS =====

async def handle_filter_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle question filtering"""
    query = update.callback_query
    subject = query.data.split(':')[1]
    
    from admin import show_questions_page
    await show_questions_page(update, context, subject, 0)

async def handle_question_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle question pagination"""
    query = update.callback_query
    _, page, subject = query.data.split(':')
    page = int(page)
    
    from admin import show_questions_page
    await show_questions_page(update, context, subject if subject != 'All' else None, page)

async def confirm_delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and delete question"""
    query = update.callback_query
    qid = int(query.data.split(':')[1])
    
    if db.delete_question(qid):
        await query.message.edit_text(
            f"✅ Question #{qid} deleted successfully!",
            reply_markup=None
        )
    else:
        await query.message.edit_text(
            f"❌ Failed to delete question #{qid}",
            reply_markup=None
        )
    
    import asyncio
    await asyncio.sleep(2)
    await query.message.reply_text("Back to admin panel", reply_markup=admin_menu)

async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings callbacks"""
    query = update.callback_query
    action = query.data.split(':')[1]
    
    if action == "timer":
        from admin import change_timer_setting
        await change_timer_setting(update, context)
    elif action == "back":
        from admin import settings_menu
        await query.message.delete()
        # Create a fake update for settings_menu
        fake_update = Update(update.update_id, message=query.message)
        await settings_menu(fake_update, context)

async def update_timer_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Update timer setting"""
    query = update.callback_query
    seconds = int(query.data.split(':')[1])
    
    # Update config (in production, save to file)
    config.MOCK_TIME_PER_QUESTION = seconds
    
    await query.message.edit_text(
        f"✅ Timer updated to {seconds} seconds per question!",
        reply_markup=None
    )
    
    import asyncio
    await asyncio.sleep(2)
    
    from admin import settings_menu
    fake_update = Update(update.update_id, message=query.message)
    await settings_menu(fake_update, context)
