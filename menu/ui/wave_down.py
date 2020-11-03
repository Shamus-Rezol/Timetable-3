import menu.event as event
from menu.ui.checkable import Checkable
import menu.ui.color as color
import curses

class WaveDown(Checkable):
	"""WaveDown запускает волну изменения состояний Checkable пунктов ниже нее.

	Объект наследуется от Checkable.

	При изменении состояния выбора этого пункта, меню посылается событие
	wave_down, которое изменяет статус всех следующих за ней Checkable
	пунктов на ее состояние.
	"""
	def __init__(self,  text, indent=0):
		"""
		Параметры
		---------
		Соответствуют инициализатору Checkable за исключением параметра
		default: отсутствует.
		"""
		super().__init__(text, indent, False)

		self.connect(event.change_value, self.on_value_changed)

	def on_value_changed(self):
		if self.parent != None:
			self.parent.handle_event(event.wave_down)
