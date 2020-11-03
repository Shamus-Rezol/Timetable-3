import curses

from menu.base.item import Item
import menu.ui.color as color

class Empty(Item):
	"""Объект пустой строки в меню.

	Объект наследуется от Item.
	"""
	def __init__(self):
		super().__init__(selectable=False)

	def refresh(self, *args):
		"""Отрисовывает себя на родительском экране.

		Метод экранирует наследуемый.
		"""
		if self.parent == None:
			return

		self.parent.screen.addstr('\n')
