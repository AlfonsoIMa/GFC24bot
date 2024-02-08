# -*- coding: UTF-8 -*-
""" Coded with <3 by @PonchoIMa

Copyright © 2024 Alfonso Izaguirre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

- Reference and credit to original authors of this software.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging, threading, time
from typing import Final
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, error, constants
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# DAY_OPORTUNITY_CHOSEN = 0
ADMINSTRATORS:  Final = # HIDDEN FOR SECURITY REASONS
TOKEN:          Final = # HIDDEN FOR SECURITY REASONS
BOT_USERNAME:   Final = '@gfc24_bot'
CLIENT = Application.chat_data
CHOOSING, CHOOSING_DATE, CHOOSING_SEMINARS, CHOOSING_OPORTUNITIES, CHOOSING_QUESTION, CHOOSING_TIME, ADMIN_MESSAGE = range(7)

# LOGGING
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# KEYBOARDS
OPER_KEYBOARD = [["📋РАСПИСАНИЕ", "👨‍🏫СЕМИНАРЫ"], ["🚀ВРЕМЯ ВОЗМОЖНОСТЕЙ", "🔴ТРАНСЛЯЦИЯ"], ["🤷‍♂️ЕСТЬ ВОПРОСЫ?", "🤔ЗАДАТЬ ВОПРОС"], ["🔴🔴НАПИСАТЬ СООБЩЕНИЕ🔴🔴"]]
MAIN_KEYBOARD = [["📋РАСПИСАНИЕ", "👨‍🏫СЕМИНАРЫ"], ["🚀ВРЕМЯ ВОЗМОЖНОСТЕЙ", "🔴ТРАНСЛЯЦИЯ"], ["🤷‍♂️ЕСТЬ ВОПРОСЫ?", "🤔ЗАДАТЬ ВОПРОС"]]
DATES_EVENT   = [["1 ФЕВРАЛЯ", "2 ФЕВРАЛЯ"], ["3 ФЕВРАЛЯ", "4 ФЕВРАЛЯ"], ["МЕНЮ"]]
SEMINARIES    = [["2 ФЕВРАЛЯ", "3 ФЕВРАЛЯ"], ["МЕНЮ"]]
OPPORTUNITIES = [["2 ФЕВРАЛЯ", "3 ФЕВРАЛЯ"], ["МЕНЮ"]]
OPORT_TIME    = [["☀️УТРО", "🌚ВЕЧЕР"], ["НАЗАД"]]
FAQS_EVENT    = [["⚠️ВАЖНО", "🏠РАССЕЛЕНИЕ"], ["☑️РЕГИСТРАЦИЯ", "🍏ПИТАНИЕ"], ["🚗ПАРКОВКА"], ["МЕНЮ"]]

def updateValues():
    global SCHEDULE_EVENT, SEMINARS_EVENT, OPORTUN_INFO, QUESTION_EVENT, SINGLEAN_EVENT
    SCHEDULE_EVENT = ['','','','']
    SEMINARS_EVENT = ['','']
    OPORTUN_INFO   = [["",""],["",""]]
    QUESTION_EVENT = ['','','','','']
    SINGLEAN_EVENT = ['','']
    while True:
        logging.info("Updating values…")
        try:
            BDD = open('textGFC.md').readlines()
            SCHEDULE_EVENT[0]  = '\n'.join(BDD[0].split('\n')[0].split('\\n'))
            SCHEDULE_EVENT[1]  = '\n'.join(BDD[1].split('\n')[0].split('\\n'))
            SCHEDULE_EVENT[2]  = '\n'.join(BDD[2].split('\n')[0].split('\\n'))
            SCHEDULE_EVENT[3]  = '\n'.join(BDD[3].split('\n')[0].split('\\n'))
            logging.info('SCHEDULE_EVENTS updated!')
            SEMINARS_EVENT[0]  = '\n'.join(BDD[4].split('\n')[0].split('\\n'))
            SEMINARS_EVENT[1]  = '\n'.join(BDD[5].split('\n')[0].split('\\n'))
            logging.info('SEMINARS_EVENTS updated!')
            OPORTUN_INFO[0][0] = '\n'.join(BDD[6].split('\n')[0].split('\\n'))
            OPORTUN_INFO[0][1] = '\n'.join(BDD[7].split('\n')[0].split('\\n'))
            OPORTUN_INFO[1][0] = '\n'.join(BDD[8].split('\n')[0].split('\\n'))
            OPORTUN_INFO[1][1] = '\n'.join(BDD[9].split('\n')[0].split('\\n'))
            logging.info('OPPORTUNITIES updated!')
            QUESTION_EVENT[0]  = '\n'.join(BDD[10].split('\n')[0].split('\\n'))
            QUESTION_EVENT[1]  = '\n'.join(BDD[11].split('\n')[0].split('\\n'))
            QUESTION_EVENT[2]  = '\n'.join(BDD[12].split('\n')[0].split('\\n'))
            QUESTION_EVENT[3]  = '\n'.join(BDD[13].split('\n')[0].split('\\n'))
            QUESTION_EVENT[4]  = '\n'.join(BDD[14].split('\n')[0].split('\\n'))
            logging.info('QUESTIONS updated!')
            SINGLEAN_EVENT[0]  = '\n'.join(BDD[15].split('\n')[0].split('\\n'))
            SINGLEAN_EVENT[1]  = '\n'.join(BDD[16].split('\n')[0].split('\\n'))
            logging.info("Updated…")
            time.sleep(300)
        except Exception as e:
            print(f'{e, e.with_traceback, e.__cause__}')
def isAdministrator(user_id: int, file_path: str = "user_ids.tbot") -> bool:
    return str(user_id) in ADMINSTRATORS
def check_for_duplicate_id(user_id: int, file_path: str = "user_ids.tbot") -> bool:
    try:
        with open(file_path, "r") as file:
            existing_ids = file.read().splitlines()
            logging.info(str(existing_ids))
        return str(user_id) in existing_ids
    except FileNotFoundError:
        return False  # No file yet, so no duplicates
    except TypeError as e:
        logging.error(f"Error loading user IDs from file: {e}")
        return False  # Assume no duplicates in case of file errors
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Привет! Я бот для помощи в ориентации на GFC24… ")
    user_id = update.effective_user.id
    if not check_for_duplicate_id(user_id):
        try:
            with open("user_ids.tbot", "a") as file:  # Open in binary append mode
                file.write(f'{user_id}\n')
        except OSError as e:
            logging.error(f"Error saving user ID to file: {e}")
        else:
            logging.info(f"User ID {user_id} collected and stored.")
    # await update.message.reply_text("Привет! Я бот для помощи в ориентации на GFC24 (TEST | Alpha 24m01a)")
    await update.message.reply_text("Пожалуйста, выберите один из вариантов в меню.",
                                    reply_markup = ReplyKeyboardMarkup(OPER_KEYBOARD if isAdministrator(update.effective_user.id) else MAIN_KEYBOARD,
                                                                       input_field_placeholder = "Выберите вариант…", resize_keyboard = True))
    return CHOOSING
async def shcedule_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, выберете день, программу которого вы хотите посмотреть",
                                    reply_markup = ReplyKeyboardMarkup(DATES_EVENT, input_field_placeholder = "Выберите вариант…", resize_keyboard = True),)
    return CHOOSING_DATE
async def date_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split()
    if(len(text) == 0):
        pass
    else:
        await update.message.reply_text(SCHEDULE_EVENT[int(text[0]) - 1],
                                        reply_markup = ReplyKeyboardMarkup(DATES_EVENT, input_field_placeholder = "Выберите вариант…", resize_keyboard = True),
                                        parse_mode = "MarkdownV2")
    return CHOOSING_DATE
async def seminaries_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, выберите один из вариантов в меню.",
                                    reply_markup = ReplyKeyboardMarkup(SEMINARIES, input_field_placeholder = "Выберите вариант…", resize_keyboard = True))
    return CHOOSING_SEMINARS
async def seminary_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if(len(text) == 0):
        pass
    else:
        await update.message.reply_text(SEMINARS_EVENT[int(text[0]) - 2],
                                        reply_markup = ReplyKeyboardMarkup(SEMINARIES, input_field_placeholder = "Выберите вариант…", resize_keyboard = True), disable_web_page_preview = True, parse_mode = "MarkdownV2")
    return CHOOSING_SEMINARS
async def ops_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, выберите один из вариантов в меню.",
                                    reply_markup = ReplyKeyboardMarkup(OPPORTUNITIES, input_field_placeholder = "Выберите вариант…", resize_keyboard = True))
    return CHOOSING_OPORTUNITIES
async def opportunity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["day_chosen"] = int(update.message.text[0])
    await update.message.reply_text("Пожалуйста, выберите один из вариантов в меню.",
                                        reply_markup = ReplyKeyboardMarkup(OPORT_TIME, input_field_placeholder = "Выберите вариант…", resize_keyboard = True))
    return CHOOSING_TIME
async def op_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = 0
    if("УТРО" not in update.message.text):
        n = 1
    await update.message.reply_text(OPORTUN_INFO[context.user_data["day_chosen"] - 2][n],
                                    reply_markup = ReplyKeyboardMarkup(OPORT_TIME, input_field_placeholder = "Выберите вариант…", resize_keyboard = True),
                                    parse_mode = 'MarkdownV2', disable_web_page_preview = True)
    return CHOOSING_TIME
async def faqs_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, выберите один из вариантов в меню.",
                                    reply_markup = ReplyKeyboardMarkup(FAQS_EVENT, input_field_placeholder = "Выберите вариант…", resize_keyboard = True),)
    return CHOOSING_QUESTION
async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    opt = 4
    if("НИЕ" in text):
        if("РАССЕЛЕНИЕ" in text):
            opt = 1
        else:
            opt = 3
    elif("ВАЖ" in text):
        opt = 0
    elif("РЕГИС" in text):
        opt = 2
    if(len(text) == 0):
        pass
    else:
        await update.message.reply_text(QUESTION_EVENT[opt],
                                        reply_markup = ReplyKeyboardMarkup(FAQS_EVENT, input_field_placeholder = "Выберите вариант…", resize_keyboard = True), 
                                        disable_web_page_preview = True, parse_mode = 'MarkdownV2')
    return CHOOSING_QUESTION
async def send_message_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) in ADMINSTRATORS:
        await update.message.reply_text("Пожалуйста, введите сообщение для отправки:",
                                        reply_markup = ReplyKeyboardMarkup([["🔴СТОП🔴"]], input_field_placeholder = "Выберите вариант…", resize_keyboard = True))
        return ADMIN_MESSAGE
    else:
        await update.message.reply_text("Извиняет. Вы не являетесь администратором. Пожалуйста, свяжитесь с одним из администраторов, чтобы выполнить это действие.",
                                        reply_markup = ReplyKeyboardMarkup(OPER_KEYBOARD if isAdministrator(update.effective_user.id) else MAIN_KEYBOARD,
                                                                       input_field_placeholder = "Выберите вариант…"))
        return CHOOSING
async def sending_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Trying to send message: {update.message.text}")
    message_to_send = update.message.text_html # update.message.text  # Wait for user response
    logging.info(f"Processing… {message_to_send}")
    if message_to_send:
        try:
            with open("user_ids.tbot", "r") as file:
                user_ids = file.read().splitlines()  # Load IDs from binary file
            for user_id in user_ids:
                logging.info(f"Attempting {user_id}")
                try:
                    await context.bot.send_message(chat_id = user_id, text = message_to_send, parse_mode = 'HTML')
                except Exception as e:
                    logging.error(f"Error sending message to user {user_id}: {e}")
                    # Handle errors gracefully, e.g., log them or retry
            await update.message.reply_text("Message sent to all users!",
                                            reply_markup = ReplyKeyboardMarkup(OPER_KEYBOARD if isAdministrator(update.effective_user.id) else MAIN_KEYBOARD,
                                                                       input_field_placeholder = "Выберите вариант…", resize_keyboard = True))
            return CHOOSING
        except FileNotFoundError:
            await update.message.reply_text("File 'user_ids.tbot' not found.")
    else:
        await update.message.reply_text("No message received. Timeout exceeded.", reply_markup = ReplyKeyboardMarkup(OPER_KEYBOARD if isAdministrator(update.effective_user.id) else MAIN_KEYBOARD,
                                                                       input_field_placeholder = "Выберите вариант…", resize_keyboard = True))
    return CHOOSING
async def handle_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    reply = ''
    if("ТРАНСЛЯЦИЯ" in text):
        reply = SINGLEAN_EVENT[0]
    else:
        reply = SINGLEAN_EVENT[1]
    await update.message.reply_text(reply,
                                    reply_markup = ReplyKeyboardMarkup(OPER_KEYBOARD if isAdministrator(update.effective_user.id) else MAIN_KEYBOARD,
                                                                       input_field_placeholder = "Выберите вариант…", resize_keyboard = True),
                                                                       parse_mode = "MarkdownV2")
    return CHOOSING
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s aborted the conversation.", user.first_name)
    await update.message.reply_text(
        "Пока!", reply_markup = ReplyKeyboardRemove()
    )
    return ConversationHandler.END
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error:\n\n{context.error}\n\n{context.error.with_traceback}')
    await context.bot.send_message(chat_id = '1523978922', text = f'Update {update} caused error:\n\n{context.error}\n\n{context.error.with_traceback}')
def main() -> None:
    # updater = Updater(TOKEN, connection_pool_size = 100)
    convStart = ConversationHandler(
        entry_points = [CommandHandler("start", start)],
        states = {
            CHOOSING: [
                MessageHandler(filters.Regex("РАСПИСАНИЕ"),     shcedule_chosen),
                MessageHandler(filters.Regex("ФЕВРАЛЯ"),        shcedule_chosen),
                MessageHandler(filters.Regex("СЕМИНАРЫ"),       seminaries_chosen),
                MessageHandler(filters.Regex("ВОЗМОЖНОСТЕЙ"),   ops_chosen),
                MessageHandler(filters.Regex("ЕСТЬ ВОПРОСЫ?"),  faqs_chosen),
                MessageHandler(filters.Regex("НАПИСАТЬ"),   send_message_to_all_users),
                MessageHandler(filters.TEXT,                    handle_options)
            ],
            CHOOSING_DATE: [
                MessageHandler(filters.Regex("ФЕВРАЛЯ") , date_chosen),
                MessageHandler(filters.Regex("МЕНЮ") , start),
            ],
            CHOOSING_SEMINARS: [
                MessageHandler(filters.Regex("ФЕВРАЛЯ") , seminary_chosen),
                MessageHandler(filters.Regex("МЕНЮ") , start),
            ],
            CHOOSING_OPORTUNITIES: [
                MessageHandler(filters.Regex("МЕНЮ") , start),
                MessageHandler(filters.TEXT, opportunity)
            ],
            CHOOSING_TIME: [
                MessageHandler(filters.Regex("НАЗАД") , ops_chosen),
                MessageHandler(filters.Regex("МЕНЮ") , start),
                MessageHandler(filters.TEXT, op_time)
            ],
            CHOOSING_QUESTION: [
                MessageHandler(filters.Regex("МЕНЮ") , start),
                MessageHandler(filters.TEXT, question)
            ],
            ADMIN_MESSAGE: [
                MessageHandler(filters.Regex("СТОП") , start),
                MessageHandler(filters.TEXT, sending_message),
            ]
        },
        fallbacks = [CommandHandler("stop", cancel)],
        allow_reentry = True
    )
    application = Application.builder().token(TOKEN).concurrent_updates(True).pool_timeout(350).connection_pool_size(700).build()
    application.add_handler(convStart)
    application.add_error_handler(error)
    application.run_polling(allowed_updates = Update.ALL_TYPES, poll_interval = 0.1, pool_timeout = 10)
    # updater.start_polling(poll_interval = 0.2)
if __name__ == "__main__":
    logging.info("Running bot…")
    x = threading.Thread(target = updateValues, daemon = True)
    x.start()
    logging.info("You should be good to modify values now?…")
    main()
