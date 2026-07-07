#!/usr/bin/env python3
# main.py
# SAT Prep Bot - Main Entry Point

import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ConversationHandler, filters
)

# Import configuration
import config

# Import all handlers
from handlers import (
    start, practice_questions_handler, start_mock_test,
    daily_question, progress, sat_tricks, help_command, back_menu
)

from admin import (
    admin_panel, add_question_start, add_question_subject, 
    add_question_text, add_question_image, save_question,
    delete_question_start, delete_question_confirm,
    view_all_questions, edit_question_start, edit_question_select,
    edit_question_field, edit_question_save, user_statistics,
    settings_menu,
    ADD_SUBJECT, ADD_QUESTION, ADD_IMAGE, ADD_OPTIONS,
    DELETE_Q_ID, EDIT_SELECT, EDIT_FIELD, EDIT_VALUE
)

from callbacks import button_callback

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context):
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try /start or contact admin."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

def main():
    """Main function to start the bot"""
    print("=" * 60)
    print("🚀 SAT Prep Bot Starting...")
    print("=" * 60)
    
    # Create application
    app = ApplicationBuilder().token(config.API_TOKEN).build()
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # ===== BASIC COMMANDS =====
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    
    # ===== USER HANDLERS =====
    app.add_handler(MessageHandler(filters.Regex("🧠 Practice Questions"), practice_questions_handler))
    app.add_handler(MessageHandler(filters.Regex("📘 Full SAT Mock"), start_mock_test))
    app.add_handler(MessageHandler(filters.Regex("🔥 Daily Question"), daily_question))
    app.add_handler(MessageHandler(filters.Regex("📊 My Progress"), progress))
    app.add_handler(MessageHandler(filters.Regex("💡 SAT Tricks"), sat_tricks))
    app.add_handler(MessageHandler(filters.Regex("ℹ️ Help"), help_command))
    app.add_handler(MessageHandler(filters.Regex("⬅️ Back to Menu"), back_menu))
    
    # ===== ADMIN HANDLERS =====
    
    # Add Question Conversation
    add_question_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("➕ Add Question"), add_question_start)],
        states={
            ADD_SUBJECT: [CallbackQueryHandler(add_question_subject, pattern="^subject:")],
            ADD_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_question_text)],
            ADD_IMAGE: [MessageHandler((filters.PHOTO | filters.TEXT) & ~filters.COMMAND, add_question_image)],
            ADD_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_question)],
        },
        fallbacks=[MessageHandler(filters.Regex("⬅️ Back to Menu"), back_menu)],
        allow_reentry=True
    )
    app.add_handler(add_question_handler)
    
    # Delete Question Conversation
    delete_question_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("🗑️ Delete Question"), delete_question_start)],
        states={
            DELETE_Q_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_question_confirm)],
        },
        fallbacks=[MessageHandler(filters.Regex("⬅️ Back to Menu"), back_menu)],
        allow_reentry=True
    )
    app.add_handler(delete_question_handler)
    
    # Edit Question Conversation
    edit_question_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✏️ Edit Question"), edit_question_start)],
        states={
            EDIT_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_select)],
            EDIT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_field)],
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_save)],
        },
        fallbacks=[MessageHandler(filters.Regex("⬅️ Back to Menu"), back_menu)],
        allow_reentry=True
    )
    app.add_handler(edit_question_handler)
    
    # Other admin handlers
    app.add_handler(MessageHandler(filters.Regex("📝 View All Questions"), view_all_questions))
    app.add_handler(MessageHandler(filters.Regex("📊 User Statistics"), user_statistics))
    app.add_handler(MessageHandler(filters.Regex("⚙️ Settings"), settings_menu))
    
    # ===== CALLBACK HANDLERS =====
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # ===== START BOT =====
    print("✅ Bot is ready!")
    print(f"📊 Admin IDs: {config.ADMIN_IDS}")
    print(f"⏱️  Mock timer: {config.MOCK_TIME_PER_QUESTION}s per question")
    print(f"📅 Daily questions: {config.DAILY_QUESTIONS_COUNT} per day")
    print("=" * 60)
    
    # Run the bot
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
