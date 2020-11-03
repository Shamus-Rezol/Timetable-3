from collection.document import Document

import time
import json
import datetime
import traceback

import urllib.request
import lxml.etree
import os.path

# Корневой путь сайта.
WEBSITE="http://portal.asiec.ru/"
# Страница WEBSITE с таблицей документов рассписаний.
PAGE="timetable/"
# Кодировка страниц сайта.
ENCODING="utf-8"

# Максимальное колличество попыток получить ответ от WEBSITE+PAGE и
# задержка перед повторной попыткой в секундах.
MAX_ATTEMPTS=3
DELAY=6

# xPath элемента строки таблицы на сайте WEBSITE+PAGE.
XPATH=".//a[@class=\"element-title  \"]"

class Documents(object):
	"""Класс Documents получает и хранит актуальные документы рассписаний.

	Аттрибуты
	---------
	timestamp : str
		Метка времени обновления этого списка.

	documents : list
		Список документов.

	warnings : tuple
		Кортеж предупреждений, возникших в ходе получения списка
		документов.

	Методы
	------
	refresh()
		Обновляет список документов.

	load(file)
		Загружает себя из файла.

	dump(file)
		Сериализует себя в файл.
	"""
	def __init__(self):
		self.timestamp="1970-01-01 00:00:00"
		self.documents=list()
		self.warnings=tuple()

	def __iter__(self):
		return iter(self.documents)

	def refresh(self):
		"""Обновляет список документов.

		В процессе работы обновляются аттрибуты timestamp, warnings и
		documents.

		С сайта WEBSITE+PAGE получается html разметка страницы в
		кодировке ENCODING. В ней ищутся строки таблицы по XPATH.

		Строки таблицы
		--------------
		Текст элемента
			название документа рассписания.

		data-bx-download
			Ссылка перехода на страницу скачивания этого документа (без
			WEBSITE).

		Исключения
		----------
		urllib.error.*
			При превышении максимального числа попыток (MAX_ATTEMPTS)
			получить ответ от WEBSITE+PAGE.

		UnicodeError или его наследник
			Не удалось декодировать страницу.
		"""
		self.documents.clear()
		self.warnings=list()
		
		for attempt in range(1, MAX_ATTEMPTS+1):
			try:
				responce=urllib.request.urlopen(WEBSITE+PAGE)
				break
			except:
				self.warnings.append(
					  "Не удалось получить ответ (попытка "+str(attempt)
					+ ") от сайта из-за следующего исключения:\n"
					+ traceback.format_exc())
				if attempt == MAX_ATTEMPTS:
					raise
				time.sleep(DELAY)

		html=responce.read().decode(ENCODING)
		del responce

		for tag in lxml.etree.HTML(html).xpath(XPATH):
			try:
				name=tag.text
				page=tag.get("data-bx-download")
				url=WEBSITE+page
				self.documents.append(Document(name, url))
			except:
				self.warnings.append(
					  "Какой-то документ не может быть получен с сайта "
				    + "из-за следующего исключения:\n"
				    + traceback.format_exc())

		fmt="%Y-%m-%d %H:%M:%S"
		self.timestamp=datetime.datetime.now().strftime(fmt)
		self.warnings=tuple(self.warnings)

	def load(self, file):
		"""Загружает себя из файла.

		Параметры
		---------
		file : str
			Полный путь к файлу.
		"""
		if os.path.isfile(file):
			try:
				with open(file, 'r', encoding="utf-8") as fp:
					data=json.load(fp)
				self.timestamp=data["timestamp"]
				self.warnings=tuple(data["warnings"])
				self.documents=list()
				for obj_dat in data["documents"]:
					self.documents.append(Document.load(obj_dat))
			except:
				self.refresh()
				cat=("Было вызвано следующее исключение при попытке "
					+"десериализации файла '{}':\n{}\nДокументы были "
					+"обновлены из интернета."
				).format(file, traceback.format_exc())
				self.warnings=(cat, )+self.warnings
				self.dump(file)
		else:
			self.refresh()
			self.dump(file)

	def dump(self, file):
		"""Сериализует себя в файл.

		Файл будет перезаписан без каких-либо проверок!

		Параметры
		---------
		file : str
			Полный путь к файлу.
		"""
		with open(file, 'w', encoding="utf-8") as fp:
			data=dict(
				timestamp=self.timestamp,
				warnings=self.warnings,
				documents=list())

			for document in self.documents:
				data["documents"].append(document.to_json())

			json.dump(data, fp, ensure_ascii=False, indent=4)
