from collection.cloud_file import CloudFile
from timetable.departament import Departament
from collection.parse import ParseDate, ParseDepartamentName, ParseTable

import datetime
import json
import os

class Document(object):
	"""Класс Document предназначен для работы с документом рассписания.

	Аттрибуты
	---------
	Аттрибуты cloud_file, _path, _dname, _date, _departament, _warnings
	и _with_changes скрыты и должны игнорироваться.

	Свойства
	--------
	path : str
		Местоположение файла на локальном компьютере. Вызывает неявную
		загрузку документа через ensure_exist().

	name : str
		Имя документа.

	departament_name : str
		Имя рассписания вида «Рассписание таких-то отделений».

	date : datetime.date
		Метка даты в имени документа.

	with_changes : bool
		Метка наличия изменений. Сигнатура: «измен» в названии файла.

	Методы
	------
	ensure_exist()
		Обеспечивает наличие файла на локальном компьютере.

	GetDepartament()
		Возвращает объект Departament и кортеж предупреждений.
	"""
	def __init__(self, name, url):
		"""
		Параметры
		---------
		name : str
			Название документа рассписания.

		url : str
			Ссылка для его скачивания.
		"""
		self.cloud_file=CloudFile(name, url)

		self._path=str()
		self._date=None
		self._dname=None
		self._with_changes=None
		self._departament=None
		self._warnings=tuple()

	def ensure_exist(self):
		"""Обеспечивает наличие файла на локальном компьютере."""
		if not os.path.isfile(self._path):
			if not os.path.isfile(self.cloud_file.path):
				self.cloud_file.download()
			self._path=self.cloud_file.path

	@property
	def path(self) -> str:
		self.ensure_exist()
		return self._path

	@property
	def name(self) -> str:
		return self.cloud_file.name

	@property
	def departament_name(self) -> str:
		if self._dname == None:
			self._dname=ParseDepartamentName(self.name)
		return self._dname

	@property
	def date(self) -> datetime.date:
		if self._date == None:
			self._date=ParseDate(self.name)
		return self._date

	@property
	def with_changes(self) -> bool:
		if self._with_changes == None:
			if self.name.lower().find("измен") != -1:
				self._with_changes=True
			else:
				self._with_changes=False
		return self._with_changes

	def GetDepartament(self):
		"""Возвращает объект Departament и кортеж предупреждений.

		Возврат
		-------
		GetDepartament возвращает кортеж вида (Departament, warnings),
		где Departament - соответствующий рассписанию этого документа
		объект, а warnings - возникшие проблемы при лексировании таблицы
		из документа и ее разбора на аттрибуты Departament (вида кортежа
		из строк).
		"""
		if self._departament == None:
			self.ensure_exist()
			(table, shape, warnings)=ParseTable(self, True)
			self._departament=Departament(str(self.date)+' '+self.departament_name)
			self._warnings=list(warnings)
			self._warnings+=list(self._departament.parse(table, shape))
			self._warnings=tuple(self._warnings)
		return (self._departament, self._warnings)

	@staticmethod
	def load(data):
		"""Возвращает новый экземпляр Document из JSON сериализации.

		Параметры
		---------
		data : str или bytes
			JSON сериализация объекта Document
		"""
		(name, url, path)=json.loads(data)
		obj=Document(name, url)
		obj._path=path
		return obj

	def to_json(self):
		"""Возвращает себя в формате строки JSON."""
		data=(self.cloud_file.name, self.cloud_file.url, self._path)
		return json.dumps(data, ensure_ascii=False)
