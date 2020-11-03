import menu.event as event

class Item(object):
	"""Базовый класс для различных пунктов меню.

	Взаимодействие объекта реализовано событиями. К примеру, при
	некотором состоянии меню Y отправляет пункту Z событие W, обрабатывая
	которое вызывается функция F с параметрами A.

	События
	-------
	event.clear
		Аттрибут parent становится None.

	Аттрибуты
	---------
	Аттрибут handlers скрыт и должен игнорироваться.

	parent
		Ссылка на экземпляр меню, к которому принадлежит объект. Доступна
		после вызова метода setup.

	selectable : bool
		Могут ли меню с навигацией по пунктам выбирать этот пункт. По
		умолчанию False.

	Методы
	------
	connect(event_id, handler, *args)
		Присоединяет обработчик handler с параметрами *args к событию event_id.

	disconnect(event_id)
		Отсоединяет все обработчики события event_id.

	handle(event_id)
		Вызывает все обработчики события event_id.

	setup(menu)
		Выполняет привязку к меню.

	refresh(is_on_cursor)
		Обновляет себя на родительском меню.
	"""

	'''Заметки для разработчиков.

	Скрытые аттрибуты
	-----------------
	handlers : dict
		Хранилище обработчиков. Ключи - идентификаторы событий. Значения -
		список списков, где последние имеют вид (handler, *arguments).
	'''
	def __init__(self, selectable=False):
		"""
		Параметры
		---------
		selectable : bool
			Могут ли меню с навигацией по пунктам выбирать этот пункт.
			По умолчанию False.
		"""
		self.handlers=dict()
		self.parent=None
		self.selectable=selectable

		self.connect(event.clear, setattr, self, "parent", None)

	def connect(self, event_id, handler, *args):
		"""Присоединяет обработчик handler с параметрами *args к событию event_id.

		Параметры
		---------
		event_id
			Идентификатор события.

		handler
			Обработчик события. К примеру, какая-то функция.

		*args
			Аргументы, которые будут переданы обработчику при вызове как
			параметры.
		"""
		if not event_id in self.handlers.keys():
			self.handlers[event_id]=list()
		self.handlers[event_id].append((handler, *args))

	def disconnect(self, event_id):
		"""Отсоединяет все обработчики события event_id."""
		if event_id in self.handlers.keys():
			del self.handlers[event_id]

	def handle(self, event_id):
		"""Вызывает все обработчики события event_id."""
		if event_id in self.handlers.keys():
			for item in self.handlers[event_id]:
				handler, *args = item
				handler(*args)

	def setup(self, menu):
		"""Выполняет привязку к меню."""
		self.parent=menu

	def refresh(self, is_on_cursor):
		"""Обновляет себя на родительском меню.

		Метод может и должен быть перезаписан дочерними объектами.
		"""
		pass
