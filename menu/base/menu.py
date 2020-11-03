import menu.event as event
from menu.ui.checkable import Checkable
from menu.ui.wave_down import WaveDown
import curses

def clamp(minimum, value, maximum):
	return min(max(value, minimum), maximum)

# ISSUE: Что будет с прокруткой oY, если каждый пункт занимает не одну
# строчку? Вероятно, она будет неправильной, и существует некоторый набор
# пунктов, курсор при прокрутке которых будет уходить за рамки
# отображаемой области. Синоним к названию этого меню - простота...
# Временно решил это запретив символ перехода на новую строку в классе
# label, на котором базируются все используемые в моей программе меню с
# текстом. В любом случая, я и не думал так использовать это. Так что,
# дорогие вы мои, это ваша головная боль.
class Menu(object):
	"""Базовый класс меню, который уже может использоваться как меню.

	Меню базируется на прокручиваемом окне curses, и оно не усложнено
	системой его расширения. То есть пункты при их отрисовке на экране
	вполне могут выйдти за пределы его буфера, что вызовет критическую
	ошибку в программе. Для избежания этого следует задавать достаточный
	размер окну. См параметр инициализации size.

	ISSUE. Возможны ошибки при нулевом колличестве элементов так как
	считается, что курсор всегда указывает на индекс какого-то элемента
	в списке.

	Аттрибуты
	---------
	Аттрибуты lines, cursor, _batch_handler, _ace и dy скрыты и должны
	игнорироваться.

	dp0, dp1
		Смотрите в параметрах инициализатора.

	items : list
		Список различных экземпляров пунктов меню.

	screen
		Прокручиваемое окно curses, на котором отображается меню.

		Переинициализация (не рекоменюуется):
			_=Menu()
			size=(lines, columns)
			_.screen=curses.newpad(size)
			_.screen.keypad(True)
			_.dy=0
			_.cursor=0

	is_alive : bool
		True, если работает основной цикл меню. Изменив на False, можно
		остановить его, но только после нажатия пользователе клавиши,
		которое обработается.

	Свойства
	--------
	current_item
		Возвращает текущий пункт (на курсоре).

	Методы
	------
	append(instance, *arguments)
		Создает, инициализирует и добавляет новый пункт меню

	insert(x, instance, *arguemtns)
		Подобен append, но добавляет на определенный индекс x.

	send2all(event_id)
		Отправляет событие event_id всем пунктам.

	clear
		Удаляет все пункты.

	refresh
		Обновляет отображаемое меню на экране.

	skip_non_selectable(side)
		Пропускает все невыделяемые пункты меню.

	advance(n):
		Продвигает курсор меню на n пунктов и изменяет прокрутку по оси oY.

	handle_event(event_id)
		Обрабатывает событие.

	setup_batch_handler(handler)
		Устанавливает пакетный обработчик нажатия клавиши 'E' (en).

	handle_key(key):
		Обрабатывает нажатие клавиши.

	run()
		Выполнить основной цикл жизни меню.
	"""

	'''Заметки для разработчиков.

	Скрытые аттрибуты
	-----------------
	lines : int
		Колличество линий в отображаемой части экрана. Необходимо для
		правильного обновления прокрутки в advance.

	cursor : int
		Индекс пункта items, на котором находится курсор.

	dy : int
		Начальная oY координата прокручиваемого экрана для отображения.

	_batch_handler
		Пользовательский пакетный обработчик.
	'''
	def __init__(self, dp0=(0, 0), dp1=None, size=(512, 1024)):
		"""
		Примечание
		----------
			Основное окно curses должно быть инициализировано до
			инициализации этого объекта так как при ней создается
			прокручиваемое окно curses.

		Параметры
		---------
		dp0 : tuple
			Точка верхрего левого угла главного окна для отрисовки части
			окна меню. Имеет вид кортежа координат (y, x). По умолчанию
			в началах координат (0, 0).

		dp1 : tuple
			Точка нижнего правого угла главного окна для отрисовки части
			окна меню. Имеет вид кортежа координат (y, x). По умолчанию
			None, то есть определится автоматически на самый дальний
			возможный угол.

		size : tuple
			Размер буфера прокручиваемого окна. Является кортежем вида
			(lines, columns). Переданный размер нельзя будет изменить,
			не переинициализировав окно screen самостоятельно.
		"""
		self._batch_handler=None
		self.screen=curses.newpad(*size)
		self.screen.keypad(True)
		self.is_alive=False
		self.items=list()
		self._ace=False
		self.cursor=0
		self.dp0=dp0
		self.dy=0

		if dp1 == None:
			self.dp1=(curses.LINES-1, curses.COLS-1)

		else:
			self.dp1=dp1

		# +1 так как обе линии включаются.
		self.lines=self.dp1[0]-self.dp0[0]+1

	def append(self, instance, *arguments, **kw):
		"""Создает, инициализирует и добавляет новый пункт меню.

		Если у данного instance имеется аттрибут service_space, то к нему
		добавляется 2. Первый символ используется для отображения курсора.

		Параметры
		---------
		instance
			Класс создаваемого пункта меню.

		*arguments и **kw
			Параметры инициализации instance.

		Возвращает ссылку на созданный экземпляр меню для действий над ним.
		"""
		item=instance(*arguments, **kw)
		item.setup(self)

		if "service_space" in dir(item):
			item.service_space+=2

		if len(self.items) == 0:
			self.cursor=0
			self.dy=0

		self.items.append(item)
		return self.items[-1]

	def insert(self, x, instance, *arguments, **kw):
		"""Подобен append, но добавляет на определенный индекс x."""
		item=instance(*arguments, **kw)
		item.setup(self)

		if "service_space" in dir(item):
			item.service_space+=2

		if len(self.items) == 0:
			self.cursor=0
			self.dy=0

		self.items.insert(x, item)
		return self.items[x]

	def send2all(self, event_id):
		"""Отправляет событие event_id всем пунктам."""
		for item in self.items:
			item.handle(event_id)

	def clear(self):
		"""Удаляет все пункты."""
		self.send2all(event.clear)
		self.items.clear()

	def refresh(self):
		"""Обновляет отображаемое меню на экране."""
		self.screen.clear()
		for index, item in enumerate(self.items):
			is_on_cursor=(self.cursor == index)
			item.refresh(is_on_cursor)# TODO: изменил передаваемые аргументы.
		self.screen.refresh(self.dy, 0, *self.dp0, *self.dp1)

	def advance(self, n: int, skip_non_selectable=True):
		"""Продвигает курсор меню на n пунктов и изменяет прокрутку по оси oY.

		Параметры
		---------
		n : int
			На сколько пунктов необходимо продвинуть. Положительное - 
			вниз, отрицательное - вверх.

		skip_non_selectable : bool
			Служебный параметр. Используется для запрета рекурсии.
		"""
		if n == 0:
			return
		self.cursor=clamp(0, self.cursor+n, len(self.items)-1)
		# Изменение прокрутки будет происходить только если курсор вышел
		# за видимую область:
		if n > 0 and self.cursor >= self.dy+self.lines:
			self.dy+=1

		elif n < 0 and self.cursor <= self.dy:
			self.dy-=1

		self.dy=clamp(0, self.dy, max(len(self.items)-self.lines, 0))

		if skip_non_selectable:
			self.skip_non_selectable(n)

	@property
	def current_item(self):
		return self.items[self.cursor]

	def skip_non_selectable(self, side):
		"""Пропускает все невыделяемые пункты меню.

		Если текущий элемент является крайним и он non selectable, то
		запускает рекурсию функции с противоположной стороной, но только
		если колличество пунктов превышает три.

		Параметры
		---------
		side : int
			Направление пропуска. Положительное - вниз. Отрицательное -
			вверх.

		recurse : int
			Должен игнорироваться. Служебный параметр ограничения
			рекурсии вызова. Прибавляется на 1 при каждом запуске
			рекурсии, имеющей место быть в крайних пунктах меню.
			Ограничение: 1 проход от начала до конца. Если не найден non
			selectable пункт, то останавливает рекурсию.
		"""
		recurses=0
		side=clamp(-1, side, 1)
		while not self.current_item.selectable:
			if ((self.cursor == len(self.items)-1 and side > 0)
							or (self.cursor == 0 and side < 0)):
				side=side*(-1)
				recurses+=1
			if recurses == 2:
				break
			self.advance(side, False)

	def handle_event(self, event_id):
		"""Обрабатывает событие."""
		if event_id == event.wave_down:
			if isinstance(self.current_item, WaveDown):
				value=self.current_item.value
				stay=self.cursor
				self.advance(1)
				while (isinstance(self.current_item, Checkable)
						and not isinstance(self.current_item, WaveDown)):
					if self.cursor == len(self.items)-1:
						break
					elif self.current_item.value != value:
						self.current_item.handle(event.change_value)
					self.advance(1, False)
				self.advance(-(self.cursor-stay))

	def setup_batch_handler(self, handler, abort_click_event=False):
		"""Устанавливает пакетный обработчик нажатия клавиши 'E' (en).

		Все выбранные Checkable элементы будут передаты в обработчик как
		параметры.

		Параметры
		---------
		handler
			Функция, принимающая в качестве параметров список выбранных
			пунктов.

			Если None, то уже существующий обработчик просто удаляется.

		abort_click_event : bool
			В случае True, выбранным пунктам не будет передаваться
			event.click ни до, ни после. Иначе он передается до вызова
			обработчика. Игнорируется, если handler == None.
		"""
		self._batch_handler=handler

		if handler == None:
			self._ace=False
		else:
			self._ace=abort_click_event

	def handle_key(self, key):
		"""Обрабатывает нажатие клавиши.

		Параметры
		---------
		key : bytes
			Байт, обозначающий нажатую кнопку.
		"""
		keys=lambda x: (ord(c) for c in x)

		if key == 27:# ESCAPE
			self.is_alive=False

		elif key == curses.KEY_UP:
			self.advance(-1)

		elif key == curses.KEY_DOWN:
			self.advance(1)

		elif key in (ord(' '), curses.KEY_RIGHT, curses.KEY_LEFT):
			self.current_item.handle(event.change_value)

		elif key in keys("iш"):
			self.send2all(event.invert_all)

		elif key in keys("sы"):
			self.send2all(event.reset)

		elif key in keys("\n\r"):
			_=self.items[self.cursor]
			_.handle(event.click)

		elif key in keys("eу"):
			to_exec=list()
			for item in self.items:
				if isinstance(item, Checkable):
					if item.value:
						to_exec.append(item)

			if not self._ace:
				for item in to_exec:
					item.handle(event.click)

			if self._batch_handler != None:
				self._batch_handler(*to_exec)

	def run(self):
		"""Выполнить основной цикл жизни меню."""
		self.is_alive=True
		while self.is_alive:
			self.refresh()
			self.handle_key(self.screen.getch())
