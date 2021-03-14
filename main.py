import telebot
from telebot import types, apihelper
import config
from models.State import State
import info.translations as info

apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(config.TOKEN)
state = State(
	info.text,
	info.urls,
	info.projects,
	info.services,
	"en",
	5
)


# KEYBOARDS
# WELCOME
def welcome_kb():
	markup = types.ReplyKeyboardMarkup(row_width=1)
	markup.add(
		types.KeyboardButton(state.get_translate("start_button_about")),
		types.KeyboardButton(state.get_translate("start_button_projects")),
		types.KeyboardButton(state.get_translate("start_button_order")),
		types.KeyboardButton(state.get_translate("lang_change"))
	)
	return markup


# Projects
def project_kb():
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton("\U0001F878", callback_data="projects_prev"),
		types.InlineKeyboardButton(f"{state.project_index + 1}/{state.projects_len}", callback_data="projects_pages"),
		types.InlineKeyboardButton("\U0001F87A", callback_data="projects_next"),
	)
	markup.row(
		types.InlineKeyboardButton(state.get_translate("projects_button_info"), callback_data="projects_info"),
		types.InlineKeyboardButton(state.get_translate("projects_button_site"), callback_data="projects_info",
		                           url=state.get_project_val("site")),
	)
	return markup


def project_info_kb():
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton(state.get_translate("projects_button_back"), callback_data="projects_back")
	)
	return markup


def pages_kb():
	markup = types.InlineKeyboardMarkup()
	for index, item in enumerate(state.get_projects()):
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
	for index, item in enumerate(get_slice(state.get_services(), state.services_page, state.on_page)):
		markup.add(
			types.InlineKeyboardButton(state.get_translate(item["button_text"]) + get_emoji(item["selected"]),
			                           callback_data=f"order_select_{state.services_page * state.on_page + index}"))
	if state.on_page < state.services_len - 1:
		markup.row(
			types.InlineKeyboardButton("\U0001F878", callback_data="order_prev"),
			types.InlineKeyboardButton(f"{state.services_page + 1}/{state.max_pages}", callback_data="order_pages"),
			types.InlineKeyboardButton("\U0001F87A", callback_data="order_next"),
		)
	markup.row(types.InlineKeyboardButton(state.get_translate("order_make"), callback_data="order_make"))
	return markup


def order_pages_kb():
	markup = types.InlineKeyboardMarkup(row_width=3)
	buttons = []
	for item in range(0, state.max_pages):
		buttons.append(types.InlineKeyboardButton(f"{item + 1}", callback_data=f"order_set_page_{item}"))
	markup.add(*buttons)
	return markup


def order_back_kb():
	markup = types.InlineKeyboardMarkup(row_width=2)
	markup.row(
		types.InlineKeyboardButton(state.get_translate("order_confirm_button"), callback_data=f"order_confirm"),
		types.InlineKeyboardButton(state.get_translate("order_not_confirm_button"), callback_data=f"order_back"),
	)
	return markup


def order_get_contact_kb():
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton(state.get_translate("order_get_contact_button"), callback_data=f"order_get_contact"),
	)
	return markup


#
def edit_project_media(chat_id, message_id, keyboard=project_kb, project_value="description"):
	with open(state.get_project_val("image"), 'rb') as photo:
		bot.edit_message_media(
			media=types.InputMediaPhoto(media=photo, parse_mode="HTML",
			                            caption=state.get_translate(state.get_project_val(project_value))),
			chat_id=chat_id,
			message_id=message_id,
			reply_markup=keyboard()
		)


def get_str_checker(text: str):
	def str_checker(msg: types.Message):
		return msg.text == state.get_translate(text)

	return str_checker


@bot.middleware_handler(update_types=["message"])
def modify_message(_: telebot.TeleBot, message: types.Message):
	state.user_lang = str(message.from_user.to_dict()["language_code"])
	print("from:", message.from_user.to_dict()["username"], state.user_lang, message)
	if message.sticker:
		print("file_id:", message.sticker.file_id)
	else:
		print("message:", message.text)


@bot.message_handler(commands=["start"])
def welcome(msg: types.Message):
	bot.send_message(msg.chat.id, state.get_translate('start'), parse_mode="HTML", reply_markup=welcome_kb())


@bot.message_handler(func=lambda call: state.wait_contact)
def get_contact(msg: types.Message):
	state.wait_contact = False
	bot.edit_message_text(state.get_translate("order_get_contact_final"), msg.chat.id, msg.id - 1, parse_mode="HTML")


# LANG
@bot.message_handler(func=get_str_checker("lang_change"))
def language(msg: types.Message):
	print(state.get_translate("lang_change"))
	markup = types.InlineKeyboardMarkup(row_width=1)
	markup.add(
		types.InlineKeyboardButton(state.get_translate("lang_set_ru"), callback_data="lang_set_ru"),
		types.InlineKeyboardButton(state.get_translate("lang_set_en"), callback_data="lang_set_en")
	)
	bot.send_message(msg.chat.id, state.get_translate("lang"), parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "lang_set_ru")
def lang_set_ru(call: types.CallbackQuery):
	state.set_lang("ru")
	bot.send_message(call.message.chat.id, state.get_translate('start'), parse_mode="HTML", reply_markup=welcome_kb())


@bot.callback_query_handler(func=lambda call: call.data == "lang_set_en")
def lang_set_en(call: types.CallbackQuery):
	state.set_lang("en")
	bot.send_message(call.message.chat.id, state.get_translate('start'), parse_mode="HTML", reply_markup=welcome_kb())


# ABOUT
@bot.message_handler(func=get_str_checker("start_button_about"))
def about(msg: types.Message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	markup.add(
		types.InlineKeyboardButton("GitHub", callback_data="about_github", url=state.get_url("github")),
		types.InlineKeyboardButton("Twitter", callback_data="about_github", url=state.get_url("twitter")),
		types.InlineKeyboardButton("Telegram channel", callback_data="about_github", url=state.get_url("channel")),
	)
	bot.send_message(msg.chat.id, state.get_translate("about"), parse_mode="HTML", reply_markup=markup)


# PROJECTS
@bot.message_handler(func=get_str_checker("start_button_projects"))
def projects(msg: types.Message):
	with open(state.get_project_val("image"), 'rb') as photo:
		bot.send_photo(
			msg.chat.id,
			photo,
			caption=state.get_translate(state.get_project_val("description")),
			disable_notification=True,
			reply_markup=project_kb()
		)


@bot.callback_query_handler(func=lambda call: call.data == "projects_prev")
def projects_prev(call: types.CallbackQuery):
	state.prev_proj()
	edit_project_media(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "projects_next")
def projects_next(call: types.CallbackQuery):
	state.next_proj()
	edit_project_media(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: call.data == "projects_pages")
def project_pages(call: types.CallbackQuery):
	edit_project_media(call.message.chat.id, call.message.id, pages_kb)


@bot.callback_query_handler(func=lambda call: "projects_set_" in call.data)
def project_set_page(call: types.CallbackQuery):
	state.set_proj(call.data)
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
	bot.send_message(msg.chat.id, state.get_translate("order"), parse_mode="HTML", reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_prev")
def projects_prev(call: types.CallbackQuery):
	state.prev_order()
	bot.edit_message_text(state.get_translate("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_next")
def projects_next(call: types.CallbackQuery):
	state.next_order()
	bot.edit_message_text(state.get_translate("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_pages")
def project_pages(call: types.CallbackQuery):
	bot.edit_message_text(state.get_translate("order_pages"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_pages_kb())


@bot.callback_query_handler(func=lambda call: "order_set_page_" in call.data)
def project_set_page(call: types.CallbackQuery):
	state.services_page(call.data)
	bot.edit_message_text(state.get_translate("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_dont_know" or call.data == "order_info")
def project_set_page(call: types.CallbackQuery):
	bot.edit_message_text(state.get_translate(call.data), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: "order_select_" in call.data)
def project_set_page(call: types.CallbackQuery):
	state.toggle_service_selected(call.data)
	bot.edit_message_text(state.get_translate("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_make")
def project_set_page(call: types.CallbackQuery):
	selected_string = state.get_stringify_selected()
	bot.edit_message_text(selected_string, call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_back_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_back")
def project_set_page(call: types.CallbackQuery):
	bot.edit_message_text(state.get_translate("order"), call.message.chat.id, call.message.id, parse_mode="HTML",
	                      reply_markup=order_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_confirm")
def project_set_page(call: types.CallbackQuery):
	state.wait_contact = True
	bot.edit_message_text(state.get_translate("order_get_contact"), call.message.chat.id, call.message.id,
	                      parse_mode="HTML",
	                      reply_markup=order_get_contact_kb())


@bot.callback_query_handler(func=lambda call: call.data == "order_get_contact")
def project_set_page(call: types.CallbackQuery):
	state.wait_contact = False
	bot.edit_message_text(state.get_translate("order_get_contact_final"), call.message.chat.id, call.message.id,
	                      parse_mode="HTML")


@bot.message_handler(func=lambda x: not state.lang_selected and not state.is_lang_native())
def any(msg: types.Message):
	markup = types.InlineKeyboardMarkup(row_width=2)
	markup.row(
		types.InlineKeyboardButton("yes", callback_data=f"lang_set_native"),
		types.InlineKeyboardButton("no", callback_data=f"lang_not_set_native"),
	)
	print("\nasd\n")

	m = "do you want to change lang?"
	bot.send_message(msg.chat.id, m, parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "lang_set_native")
def lang_set_native(call: types.CallbackQuery):
	state.set_lang(state.user_lang)


@bot.callback_query_handler(func=lambda call: call.data == "lang_not_set_native")
def lang_not_set_native(call: types.CallbackQuery):
	state.lang_selected = True
	bot.send_message(call.message.chat.id, state.get_translate('start'), parse_mode="HTML", reply_markup=welcome_kb())


bot.polling(none_stop=True)
