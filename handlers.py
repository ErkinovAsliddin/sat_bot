# handlers.py
# User-facing command and message handlers

from telegram import Update
from telegram.ext import ContextTypes
from database import db
from keyboards import *
from utils import *
import config

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - welcome message"""
    user = update.effective_user
    db.create_user(user.id, user.username)
    
    welcome_text = f"""
👋 <b>Welcome to SAT Prep Bot, {user.first_name}!</b>

I'm here to help you ace the SAT! 🎓

<b>What I offer:</b>
🧠 Practice questions with instant feedback
📘 Full-length mock tests with scoring
💡 Expert SAT tips and tricks
🔥 Daily questions to build your streak
📊 Progress tracking and analytics

Choose an option below to get started! 👇
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=main_menu
    )

async def practice_questions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle practice questions - show subject selection"""
    await update.message.reply_text(
        "🧠 <b>Practice Mode</b>\n\nSelect a subject to practice:",
        parse_mode='HTML',
        reply_markup=subject_menu
    )

async def start_practice_subject(update: Update, context: ContextTypes.DEFAULT_TYPE, subject: str):
    """Start practice for selected subject"""
    query = update.callback_query
    await query.answer()
    
    question = db.get_random_question(subject=subject)
    
    if not question:
        await query.message.reply_text(
            f"❌ No {subject} questions available yet. Please contact admin.",
            reply_markup=main_menu
        )
        return
    
    context.user_data['practice_mode'] = True
    context.user_data['current_subject'] = subject
    context.user_data['current_question'] = question[0]
    
    await send_question(context, query.message.chat.id, question, 
                       build_practice_keyboard(question[0]), query.message.message_id)

async def start_mock_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start full SAT mock test"""
    questions = db.get_mock_questions(config.MOCK_TOTAL_QUESTIONS)
    
    if len(questions) < config.MOCK_TOTAL_QUESTIONS:
        await update.message.reply_text(
            f"❌ Not enough questions for mock test. Need {config.MOCK_TOTAL_QUESTIONS}, found {len(questions)}.",
            reply_markup=main_menu
        )
        return
    
    context.user_data['mock_mode'] = True
    context.user_data['mock_questions'] = questions
    context.user_data['mock_current'] = 0
    context.user_data['mock_answers'] = {}
    context.user_data['mock_correct'] = 0
    
    await update.message.reply_text(
        f"📘 <b>SAT Mock Test Starting!</b>\n\n"
        f"• {config.MOCK_TOTAL_QUESTIONS} questions total\n"
        f"• {config.MOCK_TIME_PER_QUESTION} seconds per question\n"
        f"• No hints or explanations during test\n\n"
        f"Good luck! 🍀",
        parse_mode='HTML',
        reply_markup=remove_keyboard
    )
    
    await asyncio.sleep(2)
    await show_next_mock_question(update.message.chat.id, context)

async def show_next_mock_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Show next question in mock test"""
    current_idx = context.user_data.get('mock_current', 0)
    questions = context.user_data.get('mock_questions', [])
    
    if current_idx >= len(questions):
        await finish_mock_test(chat_id, context)
        return
    
    question = questions[current_idx]
    q_num = current_idx + 1
    total = len(questions)
    
    context.user_data['current_question'] = question[0]
    context.user_data['question_start_time'] = datetime.now()
    
    await send_question(context, chat_id, question, 
                       build_mock_keyboard(question[0], q_num, total), None)
    
    # Start timer
    context.job_queue.run_once(
        mock_timer_callback,
        config.MOCK_TIME_PER_QUESTION,
        chat_id=chat_id,
        name=f"mock_timer_{chat_id}",
        data={'question_id': question[0], 'q_num': q_num}
    )

async def mock_timer_callback(context: ContextTypes.DEFAULT_TYPE):
    """Handle mock test timer expiration"""
    chat_id = context.job.chat_id
    
    # Auto-advance to next question
    if context.user_data.get('mock_mode'):
        current_idx = context.user_data.get('mock_current', 0)
        context.user_data['mock_current'] = current_idx + 1
        
        await context.bot.send_message(
            chat_id,
            "⏱️ Time's up! Moving to next question..."
        )
        
        await asyncio.sleep(1)
        await show_next_mock_question(chat_id, context)

async def finish_mock_test(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Finish mock test and show results"""
    correct = context.user_data.get('mock_correct', 0)
    total = config.MOCK_TOTAL_QUESTIONS
    sat_score = calculate_sat_score(correct, total)
    
    user_id = context.user_data.get('user_id')
    if user_id:
        db.save_mock_session(user_id, total, correct, sat_score)
    
    accuracy = (correct / total) * 100
    
    result_text = f"""
🎯 <b>Mock Test Complete!</b>

📊 <b>Your Results:</b>
• Score: <b>{sat_score}/800</b>
• Correct: {correct}/{total} ({accuracy:.1f}%)
• Wrong: {total - correct}

{'🎉 Excellent work!' if accuracy >= 80 else '💪 Keep practicing!' if accuracy >= 60 else '📚 Review and try again!'}
"""
    
    context.user_data.clear()
    
    await context.bot.send_message(
        chat_id,
        result_text,
        parse_mode='HTML',
        reply_markup=main_menu
    )

async def daily_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show daily questions"""
    today = get_current_date()
    user_id = update.effective_user.id
    
    # Check if user already did today's questions
    user_data = db.get_user(user_id)
    if user_data and user_data[5] == today:
        await update.message.reply_text(
            "✅ You've already completed today's questions!\n"
            "Come back tomorrow for new ones. 🔥",
            reply_markup=main_menu
        )
        return
    
    # Get or create daily questions
    daily_questions = db.get_daily_questions(today)
    
    if not daily_questions:
        # Create new daily questions
        all_questions = db.get_all_questions()
        if len(all_questions) < config.DAILY_QUESTIONS_COUNT:
            await update.message.reply_text(
                "❌ Not enough questions available. Contact admin.",
                reply_markup=main_menu
            )
            return
        
        import random
        selected = random.sample(all_questions, config.DAILY_QUESTIONS_COUNT)
        question_ids = [q[0] for q in selected]
        db.set_daily_questions(today, question_ids)
        daily_questions = selected
    
    context.user_data['daily_mode'] = True
    context.user_data['daily_questions'] = daily_questions
    context.user_data['daily_current'] = 0
    context.user_data['daily_correct'] = 0
    
    await update.message.reply_text(
        f"🔥 <b>Daily Questions - {today}</b>\n\n"
        f"Answer {config.DAILY_QUESTIONS_COUNT} questions to maintain your streak!",
        parse_mode='HTML',
        reply_markup=remove_keyboard
    )
    
    await asyncio.sleep(1)
    await show_next_daily_question(update.message.chat.id, context)

async def show_next_daily_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Show next daily question"""
    current_idx = context.user_data.get('daily_current', 0)
    questions = context.user_data.get('daily_questions', [])
    
    if current_idx >= len(questions):
        await finish_daily_questions(chat_id, context)
        return
    
    question = questions[current_idx]
    q_num = current_idx + 1
    total = len(questions)
    
    context.user_data['current_question'] = question[0]
    
    await send_question(context, chat_id, question,
                       build_daily_keyboard(question[0], q_num, total), None)

async def finish_daily_questions(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Finish daily questions"""
    correct = context.user_data.get('daily_correct', 0)
    total = config.DAILY_QUESTIONS_COUNT
    accuracy = (correct / total) * 100
    
    # Update user's last daily date
    user_id = context.user_data.get('user_id')
    if user_id:
        db.cursor.execute(
            "UPDATE users SET last_daily=?, streak=streak+1 WHERE user_id=?",
            (get_current_date(), user_id)
        )
        db.conn.commit()
    
    result_text = f"""
✅ <b>Daily Questions Complete!</b>

📊 Today's Score: {correct}/{total} ({accuracy:.1f}%)
🔥 Streak maintained!

Come back tomorrow for new questions!
"""
    
    context.user_data.clear()
    
    await context.bot.send_message(
        chat_id,
        result_text,
        parse_mode='HTML',
        reply_markup=main_menu
    )

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user progress"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    progress_text = format_progress(user_data)
    
    await update.message.reply_text(
        progress_text,
        parse_mode='HTML',
        reply_markup=main_menu
    )

async def sat_tricks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show SAT tricks and tips"""
    await update.message.reply_text(
        get_sat_tricks(),
        parse_mode='HTML',
        reply_markup=main_menu
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    admin_profiles = get_admin_profiles()
    help_text = get_help_text(admin_profiles)
    
    await update.message.reply_text(
        help_text,
        parse_mode='HTML',
        reply_markup=main_menu
    )

async def back_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to main menu"""
    context.user_data.clear()
    
    await update.message.reply_text(
        "🏠 Back to main menu",
        reply_markup=main_menu
    )

async def send_question(context: ContextTypes.DEFAULT_TYPE, chat_id: int, 
                       question_data: tuple, keyboard, message_id=None):
    """Send question to user (text and/or image)"""
    q_id, question_text, image_file_id = question_data[0], question_data[1], question_data[2]
    question_formatted = format_question_text(question_data)
    
    try:
        if image_file_id and image_file_id.strip():
            # Send image with caption
            if message_id:
                await context.bot.delete_message(chat_id, message_id)
            
            await context.bot.send_photo(
                chat_id,
                photo=image_file_id,
                caption=question_formatted,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            # Send text only
            if message_id:
                await context.bot.edit_message_text(
                    question_formatted,
                    chat_id,
                    message_id,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await context.bot.send_message(
                    chat_id,
                    question_formatted,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
    except Exception as e:
        print(f"Error sending question: {e}")
        # Fallback to text only
        if message_id:
            await context.bot.edit_message_text(
                question_formatted,
                chat_id,
                message_id,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id,
                question_formatted,
                reply_markup=keyboard,
                parse_mode='HTML'
            )

import asyncio
