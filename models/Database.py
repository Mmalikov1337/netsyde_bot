import pymysql


class Database:
	def __init__(self, host, user, password, db):
		self.host = host
		self.user = user
		self.password = password
		self.db = db
		self.connection = pymysql.connect(host=self.host, user=self.user,
		                                  password=self.password, database=self.db)
		self.cursor = self.connection.cursor()

	def add_user(self, nickname, tg_id):
		""":return id of user in table"""
		in_table = self.cursor.execute("SELECT * FROM users WHERE nickname=%s", nickname) > 0
		if not in_table:
			self.cursor.execute("INSERT INTO users (nickname,tg_id) VALUES ( %s, %s)",
			                    (nickname, tg_id))
			self.connection.commit()
			user_id = self.cursor.lastrowid
			return user_id

		self.cursor.execute("SELECT * FROM users WHERE tg_id=%s", tg_id)
		user_id = list(*self.cursor.fetchall())[0]
		return user_id

	def make_order(self, user_id, connect, selected):
		self.cursor.execute("SELECT * FROM services")
		a = self.cursor.fetchall()
		all_services = dict((y, x) for x, y in a)
		selected_indexes = [all_services[i] for i in selected]
		# print(all_services, selected_indexes)
		self.cursor.execute("INSERT INTO orders (user_id, contact) VALUES(%s, %s)", (user_id, connect))
		order_id = self.cursor.lastrowid
		self.cursor.executemany("INSERT INTO order_compositions (order_id, service_id) VALUES(%s, %s)",
		                        [(order_id, i) for i in selected_indexes])
		self.connection.commit()
