import json
import math
from .State import State
from typing import Dict
import copy


class App:
	users_data: Dict[int, State] = dict()
	default_lang = "en"

	def __init__(self, TEXT, URLS, PROJECTS, SERVICES, on_page):
		self.__TEXT = json.loads(TEXT)
		self.__URLS = json.loads(URLS)
		self.__PROJECTS = json.loads(PROJECTS)
		self.__SERVICES = json.loads(SERVICES)
		self.text_len = len(self.__TEXT)
		self.urls_len = len(self.__URLS)
		self.projects_len = len(self.__PROJECTS)
		self.services_len = len(self.__SERVICES)
		self.on_page = on_page
		self.max_pages = math.ceil(len(self.__SERVICES) / self.on_page)

	def check_user(self, user_id: int) -> bool:
		return user_id in self.users_data

	def add_user(self, user_id: int) -> True:
		""":return True if user added, and False if user already in"""
		if self.check_user(user_id):
			return False
		self.users_data[user_id] = State(copy.deepcopy(self.__SERVICES), self.default_lang)
		return True

	def set_user_info(self, user_tg_id, username, user_db_id):
		self.users_data[user_tg_id].user_tg_id = user_tg_id
		self.users_data[user_tg_id].username = username
		self.users_data[user_tg_id].user_db_id = user_db_id

	def get_db_id(self, user_id: int):
		self.add_user(user_id)
		return self.users_data[user_id].user_db_id

	def get_translate(self, user_id: int, string: str) -> str:
		self.add_user(user_id)
		return self.__TEXT[string][self.users_data[user_id].user_lang]

	def get_wait_contact(self, user_id: int) -> bool:
		self.add_user(user_id)
		return self.users_data[user_id].wait_contact

	def set_wait_contact(self, user_id: int, val: bool):
		self.add_user(user_id)
		self.users_data[user_id].wait_contact = val

	def set_connect(self, user_id: int, connect: str):
		self.users_data[user_id].connect = connect

	def get_connect(self, user_id: int) -> str:
		return self.users_data[user_id].connect

	def get_url(self, key: str):
		return self.__URLS[key]

	def set_lang(self, user_id: int, lang: str):
		self.add_user(user_id)
		self.users_data[user_id].user_lang = lang

	def get_project_val(self, user_id: int, val: str) -> str:
		self.add_user(user_id)
		return self.__PROJECTS[self.users_data[user_id].project_index][val]

	def get_projects(self):
		return self.__PROJECTS.copy()

	def next_proj(self, user_id: int):
		self.add_user(user_id)
		self.users_data[user_id].next_proj(self.projects_len)

	def prev_proj(self, user_id: int):
		self.add_user(user_id)
		self.users_data[user_id].prev_proj(self.projects_len)

	def set_proj(self, user_id: int, val: str):
		self.add_user(user_id)
		self.users_data[user_id].set_proj(val, self.projects_len)

	def get_project_index(self, user_id: int) -> int:
		self.add_user(user_id)
		return self.users_data[user_id].project_index

	# services
	def set_service_page(self, user_id: int, val: str):
		self.add_user(user_id)
		self.users_data[user_id].set_service_page(val)

	def get_services(self, user_id: int):
		self.add_user(user_id)
		return self.users_data[user_id].get_services()

	def get_stringify_selected(self, user_id: int):
		self.add_user(user_id)
		sel = self.get_selected(user_id)
		selected_string = self.get_translate(user_id, "order_list") + "\n"
		for i in sel:
			selected_string += self.get_translate(user_id, i) + "\n"
		selected_string += self.get_translate(user_id, "order_confirm_button") + "\n"
		return selected_string

	def get_selected(self, user_id: int) -> list:
		self.add_user(user_id)
		return self.users_data[user_id].get_selected()

	def unselect_all(self, user_id: int):
		self.users_data[user_id].unselect_all()

	def next_order(self, user_id: int):
		self.add_user(user_id)
		self.users_data[user_id].next_order(self.max_pages)

	def prev_order(self, user_id: int):
		self.add_user(user_id)
		self.users_data[user_id].prev_order(self.max_pages)

	def toggle_service_selected(self, user_id: int, val: str):
		self.add_user(user_id)
		self.users_data[user_id].toggle_service_selected(val)

	def get_service_page(self, user_id: int) -> int:
		self.add_user(user_id)
		return self.users_data[user_id].services_page
# def is_lang_native(self, user_id: int):  # dynamic
# 	return self.users_data[user_id]. == self.__lang
