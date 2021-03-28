import re


class State:
	project_index = 0
	services_page = 0
	user_lang = "en"
	lang_selected = False

	user_tg_id = None
	username = None
	user_db_id = None

	connect = None
	wait_contact = False

	def __init__(self, SERVICES, lang):
		self.__SERVICES = SERVICES
		self.__lang = lang

	def __str__(self):
		return str({"project_index": self.project_index,
		            "services_page": self.services_page,
		            "user_lang": self.user_lang,
		            "lang_selected": self.lang_selected,
		            "user_tg_id": self.user_tg_id,
		            "username": self.username,
		            "user_db_id": self.user_db_id,
		            "connect": self.connect,
		            "wait_contact": self.wait_contact}) + "\n" + str(self.__SERVICES)

	@staticmethod
	def get_new_index(val: str) -> int:
		index = re.findall(r"\d+", val)[0]
		if index.isdigit():
			return int(index)
		raise ValueError(f"No digits in '{val}'")

	# PROJECT
	def next_proj(self, projects_len: int):
		if self.project_index + 1 >= projects_len:
			self.project_index = 0
		else:
			self.project_index += 1

	def prev_proj(self, projects_len: int):
		if self.project_index - 1 < 0:
			self.project_index = projects_len - 1
		else:
			self.project_index -= 1

	def set_proj(self, val: str, projects_len: int):
		new_index = self.get_new_index(val)
		if projects_len - 1 <= new_index or projects_len - 1 >= 0:
			self.project_index = new_index
		else:
			raise ValueError(f"Wrong index.Value:{new_index}, max value:{projects_len}")

	# SERVICES
	def next_order(self, max_pages):
		if self.services_page + 1 >= max_pages:
			self.services_page = 0
		else:
			self.services_page += 1

	def prev_order(self, max_pages):
		if self.services_page - 1 < 0:
			self.services_page = max_pages - 1
		else:
			self.services_page -= 1

	def get_services(self):
		return self.__SERVICES.copy()

	def set_service_page(self, val):
		self.services_page = self.get_new_index(val)

	def toggle_service_selected(self, val: str):
		index = self.get_new_index(val)
		self.__SERVICES[index]["selected"] = not self.__SERVICES[index]["selected"]

	def get_selected(self) -> list:
		sel = []
		for i in self.__SERVICES:
			if i["selected"]:
				sel.append(i)
		return [i["button_text"] for i in sel]

	def unselect_all(self):
		for i in self.__SERVICES:
			i["selected"] = False
