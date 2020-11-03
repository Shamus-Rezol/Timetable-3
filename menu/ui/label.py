import curses

from menu.base.item import Item
import menu.ui.color as color

class Label(Item):
	"""Простой цветной текстовый пункт меню.

	Объект наследуется от Item.

	Для инициализации экземпляра Label, необходимо инициализировать
	модуль color.

	Аттрибуты
	---------
	Аттрибуты text и service_space смотрите в параметрах инициализатора.

	Методы
	------
	refresh(is_on_cursor)
		Отрисовывает себя на родительском экране.
	"""
	def __init__(self,
				text,
				service_space=0,
				selectable=False):
		"""
		Параметры
		---------
		text : str
			Текст для отображения. Не может содержать символов перехода
			на новую линию.

		service_space : int
			Зарезервированное пространство перед text. Различные меню и
			дочерние классы могут использовать его на свое усмотрение.

		selectable : bool
			Могут ли меню с навигацией по пунктам выбирать этот пункт. По
			умолчанию False.
		"""
		super().__init__(selectable)

		self.text=str(text).replace('\n', ' ')
		self.service_space=service_space

	def refresh(self, is_on_cursor):
		"""Отрисовывает себя на родительском экране.

		Метод экранирует наследуемый.
		
		Параметры
		---------
		is_on_cursor : bool
			Если True, то в зарезервированное пространство перед текстом
			добавляет звездочку в первый символ.
		"""
		if self.parent == None:
			return

		service=' '*self.service_space
		if is_on_cursor:
			service='*'+service[1:]
			self.parent.screen.addstr(service,
					curses.color_pair(color.cursor))
		else:
			self.parent.screen.addstr(service)
		self.parent.screen.addstr(self.text+'\n',
					curses.color_pair(color.label))
