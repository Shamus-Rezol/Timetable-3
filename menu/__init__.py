"""Модуль предоставляет конструируемые меню.

Модуль base содержит базовые объекты меню.
Модуль ui содержит продвинутые пункты меню.
Модуль event содержит идентификаторы событий.



Взаимодействуя с меню, пользователь генерирует некоторые события.
Эти события рассылаются в нужные пункты меню. Обрабатывая их, они так
же могут послать в меню какое-то событие, так как связаны с ним с момента
их добавления.

menu=Menu()

init()
# append(instance, *args)
# label принимает текст, который будет отображать.
menu.append(label, "Простой пункт меню с текстом.")

# checkable - расширяет возможности label.
_=menu.append(checkable, "Более функциональный пункт.")
_.connect(event.click, setattr, _, "... был нажат!")
"""
import menu.event as event
from menu.ui.color import init as init_color

from menu.base.menu import Menu

from menu.ui.label import Label
from menu.ui.empty import Empty
from menu.ui.header import Header
from menu.ui.button import Button
from menu.ui.checkable import Checkable
from menu.ui.wave_down import WaveDown

import curses

def init():
	"""Инициализирует главное окно curses и модуль menu.ui.color.

	Так как некоторые объекты меню из ui нуждаются в инициализации color,
	необходимо вызвать эту функцию перед добавлением в меню каких
	любо пунктов из ui.

	Возвращает инициализированное окно."""

	stdscr=curses.initscr()

	curses.cbreak()
	curses.noecho()
	curses.curs_set(False)

	init_color()

	return stdscr
