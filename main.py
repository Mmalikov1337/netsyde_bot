import telebot
from telebot import types, apihelper
import config
from models.App import App
from models.Database import Database
import info.translations as info

db = Database(config.host, config.user, config.password, config.database)

apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(config.TOKEN)

app = App(
	info.text,
	info.urls,
	info.projects,
	info.services,
	5
)


# KEYBOARDS
# WELCOME
def welcome_kb(user_id: int):
	markup = types.ReplyKeyboardMarkup(row_width=1)
	markup.add(
		types.KeyboardButton(app.get_translate(user_id, "start_button_about")),
		types.KeyboardButton(app.get_translate(user_id, "start_button_projects")),
		types.KeyboardButton(app.get_translate(user_id, "start_button_order")),
		types.KeyboardButton(app.get_translate(user_id, "lang_change"))
	)
	return markup


# Projects
def project_kb(user_id: int):
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton("\U0001F878", callback_data="projects_prev"),
		types.InlineKeyboardButton(f"{app.get_project_index(user_id) + 1}/{app.projects_len}",
		                           callback_data="projects_pages"),
		types.InlineKeyboardButton("\U0001F87A", callback_data="projects_next"),
	)
	markup.row(
		types.InlineKeyboardButton(app.get_translate(user_id, "projects_button_info"), callback_data="projects_info"),
		types.InlineKeyboardButton(app.get_translate(user_id, "projects_button_site"), callback_data="projects_info",
		                           url=app.get_project_val(user_id, "site")),
	)
	return markup


def project_info_kb(user_id: int):
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton(app.get_translate(user_id, "projects_button_back"), callback_data="projects_back")
	)
	return markup


def pages_kb(_: int):
	markup = types.InlineKeyboardMarkup()
	for index, item in enumerate(app.get_projects()):
		markup.add(types.InlineKeyboardButton(f"{index + 1} - {item['name']}", callback_data=f"projects_set_{index}"))
	return markup


# Order
def order_kb(user_id: int):
	def get_slice(array, page, on_page):
		last_index = len(array) - 1
		start = page * on_page
		end = start + on_page
		if end > last_index:
			end = last_index
		return array[start:end]

	def get_emoji(val: bool):
		return "\U00002714" if val else "\U00002716"

	markup = types.InlineKeyboardMarkup()
	for index, item in enumerate(get_slice(app.get_services(user_id), app.get_service_page(user_id), app.on_page)):
		markup.add(
			types.InlineKeyboardButton(app.get_translate(user_id, item["button_text"]) + get_emoji(item["selected"]),
			                           callback_data=f"order_select_{app.get_service_page(user_id) * app.on_page + index}"))
	if app.on_page < app.services_len - 1:
		markup.row(
			types.InlineKeyboardButton("\U0001F878", callback_data="order_prev"),
			types.InlineKeyboardButton(f"{app.get_service_page(user_id) + 1}/{app.max_pages}",
			                           callback_data="order_pages"),
			types.InlineKeyboardButton("\U0001F87A", callback_data="order_next"),
		)
	markup.row(types.InlineKeyboardButton(app.get_translate(user_id, "order_make"), callback_data="order_make"))
	return markup


def order_pages_kb():
	markup = types.InlineKeyboardMarkup(row_width=3)
	buttons = []
	for item in range(0, app.max_pages):
		buttons.append(types.InlineKeyboardButton(f"{item + 1}", callback_data=f"order_set_page_{item}"))
	markup.add(*buttons)
	return markup


def order_back_kb(user_id: int):
	markup = types.InlineKeyboardMarkup(row_width=2)
	markup.row(
		types.InlineKeyboardButton(app.get_translate(user_id, "order_confirm_button"), callback_data=f"order_confirm"),
		types.InlineKeyboardButton(app.get_translate(user_id, "order_not_confirm_button"), callback_data=f"order_back"),
	)
	return markup


def order_get_contact_kb(user_id: int):
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton(app.get_translate(user_id, "order_get_contact_button"),
		                           callback_data=f"order_get_contact"),
	)
	return markup


#
def edit_project_media(user_id, chat_id, message_id, keyboard=project_kb, project_value="description"):
	with open(app.get_project_val(user_id, "image"), 'rb') as photo:
		bot.edit_message_media(
			media=types.InputMediaPhoto(media=photo, parse_mode="HTML",
			                            caption=app.get_translate(user_id,
			                                                      app.get_project_val(user_id, project_value))),
			chat_id=chat_id,
			message_id=message_id,
			reply_markup=keyboard(user_id)
		)


def get_str_checker(user_id: int, text: str):
	def str_checker(msg: types.Message):
		return msg.text == app.get_translate(user_id, text)

	return str_checker


@bot.middleware_handler(update_types=["message"])
def modify_message(_: telebot.TeleBot, message: types.Message):
	user_lang = str(message.from_user.to_dict()["language_code"])
	username = message.from_user.to_dict()["username"]
	user_tg_id = message.from_user.to_dict()["id"]
	text = message.text
	app.add_user(user_tg_id)
	user_db_id = db.add_user(username, user_tg_id)
	app.set_user_info(user_tg_id, username, user_db_id)
	print(f"username: {username}", f"lang: {user_lang}", f"user_tg_id: {user_tg_id}", f"user_db_id: {user_db_id}",
	      sep="\n")
	if message.sticker:
		print("file_id:", message.sticker.file_id)
	else:
		print("message:", text)
	print(f"full: {message}\n")


@bot.message_handler(commands=["start"])
def welcome(msg: types.Message):
	user_id = msg.from_user.to_dict()["id"]
	bot.send_message(msg.chat.id, app.get_translate(user_id, 'start'), parse_mode="HTML",
	                 reply_markup=welcome_kb(user_id))


@bot.message_handler(func=lambda msg: app.get_wait_contact(msg.from_user.to_dict()["id"]))
def get_contact(msg: types.Message):
	user_id = msg.from_user.to_dict()["id"]
	app.set_connect(user_id, msg.text)
	app.set_wait_contact(user_id, False)
	bot.edit_message_text(app.get_translate(user_id, "order_get_contact_final"), msg.chat.id, msg.id - 1,
	                      parse_mode="HTML")
	db.make_order(app.get_db_id(user_id), app.get_connect(user_id), app.get_selected(user_id))
	app.unselect_all(user_id)


@bot.message_handler(func=lambda msg: get_str_checker(msg.from_user.to_dict()["id"], "lang_change")(msg))
def language(msg: types.Message):
	user_id = msg.from_user.to_dict()["id"]
	markup = types.InlineKeyboardMarkup(row_width=1)
	markup.add(
		types.InlineKeyboardButton(app.get_translate(user_id, "lang_set_ru"), callback_data="lang_set_ru"),
		types.InlineKeyboardButton(app.get_translate(user_id, "lang_set_en"), callback_data="lang_set_en")
	)
	bot.send_message(msg.chat.id, app.get_translate(user_id, "lang"), parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "lang_set_ru")
def lang_set_ru(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.set_lang(user_id, "ru")
	bot.send_message(call.message.chat.id, app.get_translate(user_id, 'start'), parse_mode="HTML",
	                 reply_markup=welcome_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "lang_set_en")
def lang_set_en(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.set_lang(user_id, "en")
	bot.send_message(call.message.chat.id, app.get_translate(user_id, 'start'), parse_mode="HTML",
	                 reply_markup=welcome_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


# ABOUT
@bot.message_handler(func=lambda msg: get_str_checker(msg.from_user.to_dict()["id"], "start_button_about")(msg))
def about(msg: types.Message):
	user_id = msg.from_user.to_dict()["id"]
	markup = types.InlineKeyboardMarkup(row_width=1)
	markup.add(
		types.InlineKeyboardButton("GitHub", callback_data="about_github", url=app.get_url("github")),
		types.InlineKeyboardButton("Twitter", callback_data="about_github", url=app.get_url("twitter")),
		types.InlineKeyboardButton("Telegram channel", callback_data="about_github", url=app.get_url("channel")),
	)
	bot.send_message(msg.chat.id, app.get_translate(user_id, "about"), parse_mode="HTML", reply_markup=markup)


# PROJECTS
@bot.message_handler(func=lambda msg: get_str_checker(msg.from_user.to_dict()["id"], "start_button_projects")(msg))
def projects(msg: types.Message):
	user_id = msg.from_user.to_dict()["id"]
	with open(app.get_project_val(user_id, "image"), 'rb') as photo:
		bot.send_photo(
			msg.chat.id,
			photo,
			caption=app.get_translate(user_id, app.get_project_val(user_id, "description")),
			disable_notification=True,
			reply_markup=project_kb(user_id)
		)


@bot.callback_query_handler(func=lambda call: call.data == "projects_prev")
def projects_prev(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.prev_proj(user_id)
	edit_project_media(user_id, call.message.chat.id, call.message.id)
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "projects_next")
def projects_next(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.next_proj(user_id)
	edit_project_media(user_id, call.message.chat.id, call.message.id)
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "projects_pages")
def project_pages(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	edit_project_media(user_id, call.message.chat.id, call.message.id, pages_kb)
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: "projects_set_" in call.data)
def project_set_page(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.set_proj(user_id, call.data)
	edit_project_media(user_id, call.message.chat.id, call.message.id)
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "projects_info")
def project_pages_info(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	edit_project_media(user_id, call.message.chat.id, call.message.id, project_info_kb, "info")
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "projects_back")
def project_pages_info(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	edit_project_media(user_id, call.message.chat.id, call.message.id)
	bot.answer_callback_query(call.id, "", show_alert=False)


# ORDER
@bot.message_handler(func=lambda msg: get_str_checker(msg.from_user.to_dict()["id"], "start_button_order")(msg))
def order(msg: types.Message):
	user_id = msg.from_user.to_dict()["id"]
	bot.send_message(msg.chat.id, app.get_translate(user_id, "order"), parse_mode="HTML",
	                 reply_markup=order_kb(user_id))


@bot.callback_query_handler(func=lambda call: call.data == "order_prev")
def projects_prev(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.prev_order(user_id)
	bot.edit_message_text(app.get_translate(user_id, "order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "order_next")
def projects_next(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.next_order(user_id)
	bot.edit_message_text(app.get_translate(user_id, "order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "order_pages")
def project_pages(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	bot.edit_message_text(app.get_translate(user_id, "order_pages"), call.message.chat.id, call.message.id,
	                      parse_mode="HTML",
	                      reply_markup=order_pages_kb())
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: "order_set_page_" in call.data)
def service_set_page(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.set_service_page(user_id, call.data)
	bot.edit_message_text(app.get_translate(user_id, "order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: "order_select_" in call.data)
def project_set_page(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.toggle_service_selected(user_id, call.data)
	bot.edit_message_text(app.get_translate(user_id, "order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "order_make")
def make_order(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	if len(app.get_selected(user_id)) <= 0:
		bot.answer_callback_query(call.id, app.get_translate(user_id, "order_make_not_selected"), show_alert=True)
		return
	selected_string = app.get_stringify_selected(user_id)
	bot.edit_message_text(selected_string, call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_back_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "order_back")
def project_set_page(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	bot.edit_message_text(app.get_translate(user_id, "order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "order_confirm")
def project_set_page(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.set_wait_contact(user_id, True)
	bot.edit_message_text(app.get_translate(user_id, "order_get_contact"), call.message.chat.id, call.message.id,
	                      parse_mode="HTML",
	                      reply_markup=order_get_contact_kb(user_id))
	bot.answer_callback_query(call.id, "", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "order_get_contact")
def project_set_page(call: types.CallbackQuery):
	user_id = call.from_user.to_dict()["id"]
	app.set_connect(user_id, ">>Connect with telegram<<")
	app.set_wait_contact(user_id, False)
	bot.edit_message_text(app.get_translate(user_id, "order_get_contact_final"), call.message.chat.id, call.message.id,
	                      parse_mode="HTML")
	db.make_order(app.get_db_id(user_id), app.get_connect(user_id), app.get_selected(user_id))
	app.unselect_all(user_id)
	bot.answer_callback_query(call.id, "", show_alert=False)


#
# @bot.message_handler(func=lambda x: not app.lang_selected and not app.is_lang_native())
# def any(msg: types.Message):
# 	markup = types.InlineKeyboardMarkup(row_width=2)
# 	markup.row(
# 		types.InlineKeyboardButton("yes", callback_data=f"lang_set_native"),
# 		types.InlineKeyboardButton("no", callback_data=f"lang_not_set_native"),
# 	)
# 	print("\nasd\n")
#
# 	m = "do you want to change lang?"
# 	bot.send_message(msg.chat.id, m, parse_mode="HTML", reply_markup=markup)
#
#
# @bot.callback_query_handler(func=lambda call: call.data == "lang_set_native")
# def lang_set_native(call: types.CallbackQuery):
# 	app.set_lang(app.user_lang)
#
#
# @bot.callback_query_handler(func=lambda call: call.data == "lang_not_set_native")
# def lang_not_set_native(call: types.CallbackQuery):
# 	app.lang_selected = True
# 	bot.send_message(call.message.chat.id, app.get_translate('start'), parse_mode="HTML", reply_markup=welcome_kb())
#

bot.polling(none_stop=True)
