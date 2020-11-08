import os.path, json

DEFAULT=dict(groups=["11исип202"], departaments=["информ"])

class Preferences(object):
	"""Объект конфигурации предпочтений.

	Методы
	------
	Метод load_defaults скрыт и должен игнорироваться.

	Аттрибуты
	---------
	groups : list
		Предпочитаемые группы.

	departaments : list
		Предпочитаемые отделения.
	"""
	def __init__(self, file):
		"""
		Параметры
		---------
		file : str
			Полный путь к файлу предпочтений.
		"""
		if os.path.isfile(file):
			try:
				with open(file, 'r', encoding="utf-8") as fp:
					data=json.load(fp)

					if "groups" in data.keys():
						self.groups=data["groups"]
					else:
						self.groups=DEFAULT["groups"]

					if "departaments" in data.keys():
						self.departaments=data["departaments"]
					else:
						self.departaments=DEFAULT["departaments"]
			except:
				import panic, traceback
				whats="[ preferences.json ] Ошибка чтения файла предпочтений:"
				message="Файл предпочтений был сброшен к настройкам по "
				message+="умолчанию из-за следующей ошибки:\n\n"
				message+=traceback.format_exc()
				panic.info(whats, message, (232, 199), (51, 232))
				self.load_defaults(file)
		else:
			self.load_defaults(file)

	def load_defaults(self, file):
		"""Загружает настройки по умолчанию."""
		with open(file, 'w', encoding="utf-8") as fp:
			json.dump(DEFAULT, fp, ensure_ascii=False, indent=4)
			self.groups=DEFAULT["groups"]
			self.departaments=DEFAULT["departaments"]
