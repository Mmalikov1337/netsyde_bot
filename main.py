import telebot
from telebot import types, apihelper
import config
from math import ceil
import re
import info
import json

apihelper.ENABLE_MIDDLEWARE = True

bot = telebot.TeleBot(config.TOKEN)

TRANSLATIONS = json.loads(info.translations.text)
URLS = json.loads(info.translations.urls)

_lang = 'en'


def set_lang(lang: str):
	global _lang
	_lang = lang


def tr(string: str):
	return TRANSLATIONS[string][_lang]


PROJECTS = json.loads(info.translations.projects)
SERVICES = json.loads(info.translations.services)

_project_index = 0

_order_page = 0
_on_page = 5
_max_pages = ceil(len(SERVICES) / _on_page)
_wait_contact = False


# PROJECT FUNCTIONS
def next_proj():
	global _project_index
	if _project_index + 1 >= len(PROJECTS):
		_project_index = 0
	else:
		_project_index += 1


def prev_proj():
	global _project_index
	if _project_index - 1 < 0:
		_project_index = len(PROJECTS) - 1
	else:
		_project_index -= 1


def set_proj(index: int):
	global _project_index
	_project_index = index


def get_project_val(val: str):
	return PROJECTS[_project_index][val]


# Order functions
def next_order():
	global _order_page
	if _order_page + 1 >= _max_pages:
		_order_page = 0
	else:
		_order_page += 1


def prev_order():
	global _order_page
	if _order_page - 1 < 0:
		_order_page = _max_pages - 1
	else:
		_order_page -= 1


# KEYBOARDS
# Projects
def project_kb():
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton("\U0001F878", callback_data="projects_prev"),
		types.InlineKeyboardButton(f"{_project_index + 1}/{len(PROJECTS)}", callback_data="projects_pages"),
		types.InlineKeyboardButton("\U0001F87A", callback_data="projects_next"),
	)
	markup.row(
		types.InlineKeyboardButton(tr("projects_button_info"), callback_data="projects_info"),
		types.InlineKeyboardButton(tr("projects_button_site"), callback_data="projects_info",
		                           url=get_project_val("site")),
	)
	return markup


def project_info_kb():
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton(tr("projects_button_back"), callback_data="projects_back")
	)
	return markup


def pages_kb():
	markup = types.InlineKeyboardMarkup()
	for index, item in enumerate(PROJECTS):
		markup.add(types.InlineKeyboardButton(f"{index + 1} - {item['name']}", callback_data=f"projects_set_{index}"))
	return markup


# Order
def order_kb():
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
	for index, item in enumerate(get_slice(SERVICES, _order_page, _on_page)):
		markup.add(
			types.InlineKeyboardButton(tr(item["button_text"]) + get_emoji(item["selected"]),
			                           callback_data=f"order_select_{_order_page * _on_page + index}"))
	if _on_page < len(SERVICES) - 1:
		markup.row(
			types.InlineKeyboardButton("\U0001F878", callback_data="order_prev"),
			types.InlineKeyboardButton(f"{_order_page + 1}/{_max_pages}", callback_data="order_pages"),
			types.InlineKeyboardButton("\U0001F87A", callback_data="order_next"),
		)
	markup.row(types.InlineKeyboardButton(tr("order_make"), callback_data="order_make"))
	return markup


def order_pages_kb():
	markup = types.InlineKeyboardMarkup(row_width=3)
	buttons = []
	for item in range(0, _max_pages):
		buttons.append(types.InlineKeyboardButton(f"{item + 1}", callback_data=f"order_set_page_{item}"))
	markup.add(*buttons)
	return markup


def order_back_kb():
	markup = types.InlineKeyboardMarkup(row_width=2)
	markup.row(
		types.InlineKeyboardButton(tr("order_confirm_button"), callback_data=f"order_confirm"),
		types.InlineKeyboardButton(tr("order_not_confirm_button"), callback_data=f"order_back"),
	)
	return markup


def order_get_contact_kb():
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton(tr("order_get_contact_button"), callback_data=f"order_get_contact"),
	)
	return markup


#
def edit_project_media(chat_id, message_id, keyboard=project_kb, project_value="description"):
	with open(get_project_val("image"), 'rb') as photo:
		bot.edit_message_media(
			media=types.InputMediaPhoto(media=photo, parse_mode="HTML", caption=tr(get_project_val(project_value))),
			chat_id=chat_id,
			message_id=message_id,
			reply_markup=keyboard()
		)


def get_str_checker(text: str):
	def str_checker(msg: types.Message):
		return msg.text == tr(text)

	return str_checker


def get_new_index(val: str) -> int:
	index = re.findall(r"\d+", val)[0]
	if index.isdigit():
		return int(index)
	return 0


@bot.middleware_handler(update_types=["message"])
def modify_message(_: telebot.TeleBot, message: types.Message):
	print("from:", message.from_user.to_dict()["username"], message.from_user.to_dict()["language_code"], message)
	if message.sticker:
		print("file_id:", message.sticker.file_id)
	else:
		print("message:", message.text)


@bot.message_handler(commands=["start"])
def welcome(msg: types.Message):
	markup = types.ReplyKeyboardMarkup(row_width=1)
	markup.add(
		types.KeyboardButton(tr("start_button_about")),
		types.KeyboardButton(tr("start_button_projects")),
		types.KeyboardButton(tr("start_button_order")),
		types.KeyboardButton("Change language \U0001F202")
	)
	bot.send_message(msg.chat.id, tr('start'), parse_mode="HTML", reply_markup=markup)


@bot.message_handler(func=lambda call: _wait_contact)
def get_contact(msg: types.Message):
	global _wait_contact
	_wait_contact = False
	print(msg.text, _wait_contact)
	bot.edit_message_text(tr("order_get_contact_final"), msg.chat.id, msg.id - 1, parse_mode="HTML")


# ABOUT
@bot.message_handler(func=get_str_checker("start_button_about"))
def about(msg: types.Message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	markup.add(
		types.InlineKeyboardButton("GitHub", callback_data="about_github", url=URLS["github"]),
		types.InlineKeyboardButton("Twitter", callback_data="about_github", url=URLS["twitter"]),
		types.InlineKeyboardButton("Telegram channel", callback_data="about_github", url=URLS["channel"]),
	)
	bot.send_message(msg.chat.id, tr("about"), parse_mode="HTML", reply_markup=markup)


# PROJECTS
@bot.message_handler(func=get_str_checker("start_button_projects"))
def projects(msg: types.Message):
	with open(get_project_val("image"), 'rb') as photo:
		bot.send_photo(
			msg.chat.id,
			photo,
			caption=tr(get_project_val("description")),
			disable_notification=True,
			reply_markup=project_kb()
		)


@bot.callback_query_handler(func=lambda call: call.data == "projects_prev")
def projects_prev(call: types.CallbackQuery):
	prev_proj()
	edit_project_media(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "projects_next")
def projects_next(call: types.CallbackQuery):
	next_proj()
	edit_project_media(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "projects_pages")
def project_pages(call: types.CallbackQuery):
	edit_project_media(call.message.chat.id, call.message.id, pages_kb)


@bot.callback_query_handler(func=lambda call: "projects_set_" in call.data)
def project_set_page(call: types.CallbackQuery):
	global _project_index
	_project_index = get_new_index(call.data)
	edit_project_media(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "projects_info")
def project_pages_info(call: types.CallbackQuery):
	edit_project_media(call.message.chat.id, call.message.id, project_info_kb, "info")


@bot.callback_query_handler(func=lambda call: call.data == "projects_back")
def project_pages_info(call: types.CallbackQuery):
	edit_project_media(call.message.chat.id, call.message.id)


# ORDER
@bot.message_handler(func=get_str_checker("start_button_order"))
def order(msg: types.Message):
	bot.send_message(msg.chat.id, tr("order"), parse_mode="HTML", reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_prev")
def projects_prev(call: types.CallbackQuery):
	prev_order()
	bot.edit_message_text(tr("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_next")
def projects_next(call: types.CallbackQuery):
	next_order()
	bot.edit_message_text(tr("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_pages")
def project_pages(call: types.CallbackQuery):
	bot.edit_message_text(tr("order_pages"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_pages_kb())


@bot.callback_query_handler(func=lambda call: "order_set_page_" in call.data)
def project_set_page(call: types.CallbackQuery):
	global _order_page
	_order_page = get_new_index(call.data)
	bot.edit_message_text(tr("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_dont_know" or call.data == "order_info")
def project_set_page(call: types.CallbackQuery):
	# toggle_order_mode()
	bot.edit_message_text(tr(call.data), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: "order_select_" in call.data)
def project_set_page(call: types.CallbackQuery):
	order_index = get_new_index(call.data)
	global SERVICES
	SERVICES[order_index]["selected"] = not SERVICES[order_index]["selected"]

	bot.edit_message_text(tr("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_make")
def project_set_page(call: types.CallbackQuery):
	sel = []
	selected_string = tr("order_list") + "\n"
	for i in SERVICES:
		if i["selected"]:
			sel.append(i)
	for i in sel:
		selected_string += tr(i["button_text"]) + "\n"
	selected_string += tr("order_confirm_button") + "\n"
	bot.edit_message_text(selected_string, call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_back_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_back")
def project_set_page(call: types.CallbackQuery):
	bot.edit_message_text(tr("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_confirm")
def project_set_page(call: types.CallbackQuery):
	global _wait_contact
	_wait_contact = True
	bot.edit_message_text(tr("order_get_contact"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_get_contact_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_get_contact")
def project_set_page(call: types.CallbackQuery):
	global _wait_contact
	_wait_contact = False
	bot.edit_message_text(tr("order_get_contact_final"), call.message.chat.id, call.message.id, parse_mode="HTML")


bot.polling(none_stop=True)
