import math
import json
import re


class State:
	project_index = 0
	services_page = 0
	wait_contact = False

	def __init__(self, TEXT, URLS, PROJECTS, SERVICES, lang, on_page):
		self.__TEXT = json.loads(TEXT)  #
		self.__URLS = json.loads(URLS)  #
		self.__PROJECTS = json.loads(PROJECTS)  #
		self.__SERVICES = json.loads(SERVICES)  #
		self.text_len = len(self.__TEXT)
		self.urls_len = len(self.__URLS)
		self.projects_len = len(self.__PROJECTS)
		self.services_len = len(self.__SERVICES)
		self.__lang = lang  #
		self.on_page = on_page  #
		self.max_pages = math.ceil(len(self.__SERVICES) / self.on_page)

	@staticmethod
	def get_new_index(val: str) -> int:
		index = re.findall(r"\d+", val)[0]
		if index.isdigit():
			return int(index)
		raise ValueError(f"No digits in '{val}'")

	# TEXT
	def set_lang(self, lang: str):
		self.__lang = lang

	def get_translate(self, string: str):
		return self.__TEXT[string][self.__lang]

	# PROJECT
	def next_proj(self):
		if self.project_index + 1 >= len(self.__PROJECTS):
			self.project_index = 0
		else:
			self.project_index += 1

	def prev_proj(self):
		if self.project_index - 1 < 0:
			self.project_index = len(self.__PROJECTS) - 1
		else:
			self.project_index -= 1

	def set_proj(self, val: str):
		new_index = self.get_new_index(val)
		if self.projects_len - 1 <= new_index or self.projects_len - 1 >= 0:
			self.project_index = new_index
		else:
			raise ValueError(f"Wrong index.Value:{new_index}, max value:{self.projects_len}")

	def get_projects(self):
		return self.__PROJECTS.copy()

	def get_project_val(self, val: str):
		return self.__PROJECTS[self.project_index][val]

	# SERVICES
	def next_order(self):
		if self.services_page + 1 >= self.max_pages:
			self.services_page = 0
		else:
			self.services_page += 1

	def prev_order(self):
		if self.services_page - 1 < 0:
			self.services_page = self.max_pages - 1
		else:
			self.services_page -= 1

	def get_url(self, key: str):
		return self.__URLS[key]

	def get_services(self):
		return self.__SERVICES.copy()

	def set_service_page(self, val):
		self.services_page = self.get_new_index(val)

	def toggle_service_selected(self, val):
		index = self.get_new_index(val)
		self.__SERVICES[index]["selected"] = not self.__SERVICES[index]["selected"]

	def get_stringify_selected(self):
		sel = []
		selected_string = self.get_translate("order_list") + "\n"
		for i in self.__SERVICES:
			if i["selected"]:
				sel.append(i)
		for i in sel:
			selected_string += self.get_translate(i["button_text"]) + "\n"
		selected_string += self.get_translate("order_confirm_button") + "\n"
		return selected_string
