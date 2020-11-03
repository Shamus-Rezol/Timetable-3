import menu.event as event
from menu.ui.label import Label
import menu.ui.color as color
import curses

class Button(Label):
	"""Объект кнопки, выполняющей какие-то действие по событию event.click.

	Объект наследуется от Label.
	"""

	def __init__(self, text, indent=0):
		super().__init__(text, indent, selectable=True)

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
		self.parent.screen.addstr(service, curses.color_pair(color.cursor))

		whats=(color.cursor if is_on_cursor else color.button)
		self.parent.screen.addstr(self.text+'\n', curses.color_pair(whats))
