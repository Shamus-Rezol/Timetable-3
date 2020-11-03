"""Модуль информирования пользователя об возникших ошибках.
"""
import os
import uuid
import subprocess

import traceback
import curses

TEMP="./~tmp"
NOTEPAD="notepad.exe"

def view(string):
	"""Создает временный файл с string и открывает его в NOTEPAD."""
	file=uuid.uuid4().hex+".tb"
	path=TEMP+'/'+file

	if not os.path.isdir(TEMP):
		os.mkdir(TEMP)

	with open(path, 'w') as fp:
		fp.write(str(string))

	subprocess.Popen((NOTEPAD, path))

# TODO ограничить длинну линий и организовать видимый перенос.
def info(whats, message, c1, c2, refresh=None):
	"""Выводит на экран сообщение message с заголовком whats.

	По нажатию на ВВОД будет вызван view с соответствующими параметрами.

	Изменяет настройки стандартного экрана и резервирует цвета под
	номерами 254 и 255.

	Параметры
	---------
	whats : str
		Заголовок; о чем говорит сообщение ниже.

	message : str
		Текст любой длинны.

	c1 : tuple
		Цвет заголовка вида кортежа (fore, back). Аргументы передаются
		в curses.init_pair(_, fore, back).

	c2 : tuple
		Подобен c1, но цвет для сообщения.

	Опционально
	-----------
	refresh
		Пользовательская функция обновления экрана. По завершению, будет
		вызвана без каких-либо параметров.
	"""
	whats=whats.replace('\n', '')

	COLOR_WHATS=255
	COLOR_MESSAGE=254

	stdscr=curses.initscr()

	curses.noecho()
	curses.curs_set(False)
	try:
		curses.use_default_colors()
	except:
		curses.start_color()
		curses.use_default_colors()
	curses.init_pair(COLOR_WHATS, *c1)
	curses.init_pair(COLOR_MESSAGE, *c2)

	COLOR_WHATS=curses.color_pair(COLOR_WHATS)
	COLOR_MESSAGE=curses.color_pair(COLOR_MESSAGE)

	label_2="Нажмите ВВОД для сохранения в файл"
	label_3="Нажмите любую клавишу для продолжения"

	lines=message.split('\n')
	cols=max((len(l) for l in lines))
	cols=max(cols, len(whats), len(label_2), len(label_3))+1
	rows=len(lines)+1
	del lines

	screen=curses.newpad(rows, cols)
	screen.addstr(message, COLOR_MESSAGE)
	screen.keypad(True)

	dy=0
	dx=0

	dp0=(1, 0)
	dp1=(curses.LINES-1-2, curses.COLS-1)

	# Гарантирует, что строка поместится на экран и сохранит цвет даже
	# в неиспользуемых символах справа.
	label=lambda s: s.ljust(curses.COLS-1, ' ')[:curses.COLS-1]

	label_1=label(whats)
	label_2=label(label_2)
	label_3=label(label_3)

	while True:
		stdscr.clear()
		stdscr.addstr(label_1, COLOR_WHATS)
		stdscr.addstr(curses.LINES-2, 0, label_2, COLOR_WHATS)
		stdscr.addstr(curses.LINES-1, 0, label_3, COLOR_WHATS)
		stdscr.refresh()
		screen.refresh(dy, dx, *dp0, *dp1)

		key=screen.getch()
		if key in (3, 27): # ^C | ESC
			break

		elif key == curses.KEY_UP:
			dy=max(dy-2, 0)
		elif key == curses.KEY_DOWN:
			dy=min(dy+2, rows-3)
		elif key == curses.KEY_LEFT:
			dx=max(dx-4, 0)
		elif key == curses.KEY_RIGHT:
			dx=min(dx+4, cols-2)

		elif key == curses.KEY_MOUSE:
			state=curses.getmouse()[4]
			print(state)

		elif key in (ord('\r'), ord('\n')):
			view(whats+'\n'+message)
			break
		else:
			break

	if refresh != None:
		refresh()

def panic():
	"""Выводит на экран сообщение о возникшей критической ошибке."""
	whats="[PANIC SCREEN] В программе возникла критическая ошибка"
	message=traceback.format_exc()
	info(whats, message, (231, 4), (51, 232))
	raise
