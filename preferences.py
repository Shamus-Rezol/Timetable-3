import os.path, json

DEFAULT=dict(groups=list(), departaments=list())

class Preferences(object):
	"""Объект конфигурации предпочтений.

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
		else:
			with open(file, 'w', encoding="utf-8") as fp:
				json.dump(DEFAULT, fp, ensure_ascii=False, indent=4)
				self.groups=DEFAULT["groups"]
				self.departaments=DEFAULT["departaments"]
