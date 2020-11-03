import menu.event as event
from menu.ui.label import Label
import menu.ui.color as color
import curses

class Checkable(Label):
	"""Выбираемый и исполняемый пункт (как одиночно, так и пакетно).

	Базовое меню поддерживает нажатие клавиши 'E' (англ.), которая
	рассылает всем пунктам данного класса событие event.click, если
	аттрибут value == True.

	Объект наследуется от Label.

	Аттрибуты
	---------
	value : bool
		Выбран ли этот элемент для пакетного исполнения.
	"""

	def __init__(self, text, indent=0, default=False):
		"""
		Параметры
		---------
		text : str
			Текст для отображения. Не может содержать символов перехода
			на новую линию.

		default : bool
			Значение выделения по умолчанию. По умолчанию False.

		indent : int
			Отступ от служебного пространства перед text.

			Фактически резервируется ничем неиспользуемое служебное
			пространство.
		"""
		super().__init__(text, indent, selectable=True)

		self.value=default

		self.connect(event.invert_all, self.change_value)
		self.connect(event.change_value, self.change_value)
		self.connect(event.reset, setattr, self, "value", default)

	def change_value(self):
		self.value=not self.value

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
		if self.value:
			service=service[:1]+'+'+service[2:]
		self.parent.screen.addstr(service, curses.color_pair(color.cursor2))

		whats=None
		if is_on_cursor:
			if self.value:
				whats=color.cursor2
			else:
				whats=color.cursor
		elif self.value:
			whats=color.hightlighted2
		else:
			whats=color.checkable
		self.parent.screen.addstr(self.text+'\n', curses.color_pair(whats))
