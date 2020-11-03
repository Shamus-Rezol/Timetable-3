from menu.ui.label import Label
import menu.ui.color as color
import curses

class Header(Label):
	"""Заголовок меню."""
	def __init__(self, text):
		"""
		Параметры
		---------
		text : str
			Текст для отображения. Не может содержать символов перехода
			на новую линию.
		"""
		super().__init__(text)
		del self.service_space

	def refresh(self, is_on_cursor):
		"""Отрисовывает себя на родительском экране.

		Метод экранирует наследуемый.
		
		Параметры
		---------
		is_on_cursor : bool
			Если True, то в зарезервированное пространство перед текстом
			добавляет звездочку в первый символ.
		"""
		text=self.text.ljust(self.parent.screen.getmaxyx()[0]-1)
		self.parent.screen.addstr(text+'\n',
					curses.color_pair(color.header))
