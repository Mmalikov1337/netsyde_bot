import telebot
from telebot import types, apihelper
import config
import json

apihelper.ENABLE_MIDDLEWARE = True

bot = telebot.TeleBot(config.TOKEN)

TRANSLATIONS = {
	"start": {
		"en": "Hello",
		"ru": "привет"
	},
	"start_button_about": {
		'en': "About us",
		'ru': 'О нас'
	},
	'start_button_projects': {
		'en': 'Our projects',
		'ru': 'Наши проекты'
	},
	'start_button_order': {
		'en': 'Our services',
		'ru': 'Наши услуги'
	},
	'about': {
		'en': "<strong>About us</strong>\nWe help organizations unlock potential growth in the arena of digital "
		      "innovation and presence. We ideate and test concepts and turn them into business to fix their corporate "
		      "strategy.",
		'ru': "<strong>О нас</strong>\nМы помогаем организациям раскрыть потенциал роста в сфере цифровых инноваций и "
		      "присутствия. Мы придумываем и тестируем концепции и превращаем их в бизнес, чтобы закрепить их "
		      "корпоративную стратегию. "
	},
	"projects_button_info": {
		'en': 'More info',
		'ru': 'Детальная информация'
	},
	"projects_button_site": {
		'en': 'Project website',
		'ru': 'Сайт проекта'
	}, "projects_button_back": {
		'en': 'Back',
		'ru': 'Назад'
	},
	"projects_decrybe": {
		'en': 'projects_decrybe website',
		'ru': 'Сайт проекта'
	},
	"projects_cryptobot": {
		'en': 'projects_cryptobot website',
		'ru': 'Сайт проекта'
	}
}

URLS = {
	"github": "https://github.com/netsyde",
	"twitter": "https://twitter.com/netsydeplatform",
	"channel": "https://t.me/netsyde"
}
_lang = 'en'


def set_lang(lang: str):
	global _lang
	_lang = lang


def tr(string: str):
	return TRANSLATIONS[string][_lang]


_project_index = 0

PROJECTS = [
	{"name": "decrybe", "image": "media/images/cc.png", "description": tr("projects_decrybe"), "info": "netsy.de",
	 "site": "netsy.de"},
	{"name": "crypto", "image": "media/images/dec.png", "description": tr("projects_cryptobot"), "info": "netsy.de",
	 "site": "netsy.de"}
]


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


def get_project_val(val: str):
	return PROJECTS[_project_index][val]


def project_kb():
	markup = types.InlineKeyboardMarkup()
	markup.row(
		types.InlineKeyboardButton("\U0001F878", callback_data="projects_prev"),
		types.InlineKeyboardButton(f"{_project_index + 1}/{len(PROJECTS)}", callback_data="projects_pages"),
		types.InlineKeyboardButton("\U0001F87A", callback_data="projects_next"),
	)
	markup.row(
		types.InlineKeyboardButton(tr("projects_button_info"), callback_data="projects_info",
		                           url=get_project_val("info")),
		types.InlineKeyboardButton(tr("projects_button_site"), callback_data="projects_info",
		                           url=get_project_val("site")),
	)
	markup.row(
		types.InlineKeyboardButton(tr("projects_button_back"), callback_data="projects_info")
	)
	return markup


def edit_project_media(chat_id, message_id):
	with open(get_project_val("image"), 'rb') as photo:
		bot.edit_message_media(
			media=types.InputMediaPhoto(media=photo, parse_mode="HTML", caption=get_project_val("description")),
			chat_id=chat_id,
			message_id=message_id,
			reply_markup=project_kb()
		)


def get_str_checker(text: str):
	def str_checker(msg: types.Message):
		return msg.text == tr(text)

	return str_checker


@bot.middleware_handler(update_types=["message"])
def modify_message(_: telebot.TeleBot, message: types.Message):
	print("from:", message.from_user.to_dict()["username"], message.from_user.to_dict()["language_code"])
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


@bot.message_handler(func=get_str_checker("start_button_about"))
def about(msg: types.Message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	markup.add(
		types.InlineKeyboardButton("GitHub", callback_data="about_github", url=URLS["github"]),
		types.InlineKeyboardButton("Twitter", callback_data="about_github", url=URLS["twitter"]),
		types.InlineKeyboardButton("Telegram channel", callback_data="about_github", url=URLS["channel"]),
	)
	bot.send_message(msg.chat.id, tr("about"), parse_mode="HTML", reply_markup=markup)


@bot.message_handler(func=get_str_checker("start_button_projects"))
def projects(msg: types.Message):
	with open(get_project_val("image"), 'rb') as photo:
		bot.send_photo(
			msg.chat.id,
			photo,
			caption=get_project_val("description"),
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
	markup = types.InlineKeyboardMarkup()
	for index, item in enumerate(PROJECTS):
		markup.add(types.InlineKeyboardButton(f"{index + 1} - {item['name']}", callback_data="projects_info"))
	with open(get_project_val("image"), 'rb') as photo:
		bot.send_photo(
			call.message.chat.id,
			photo,
			caption=get_project_val("description"),
			disable_notification=True,
			reply_markup=markup
		)


bot.polling(none_stop=True)
