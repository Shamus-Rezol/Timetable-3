import os
import urllib

DOWNLOAD_DIRECTORY="./downloads"

class CloudFile(object):
	"""Класс CloudFile используется для облачного хранения файла.

	Аттрибуты
	---------
	name : str
		Название файла.

	url : str
		Ссылка для скачивания файла.

	Свойства
	--------
	path
		Возвращает (будующее) местоположения файла на компьютере.

	Методы
	------
	Метод ensure_root скрыт и должен игнорироваться.

	download()
		Скачивает файл на локальный компьютер.
	"""
	def __init__(self, name, url):
		"""
		Параметры
		---------
		name : str
			Имя файла.

		url : str
			Ссылка на его скачивание.
		"""
		self.name=name
		self.url=url

	@staticmethod
	def ensure_root():
		"""Обеспечивает наличие каталога скачивания."""
		if not os.path.isdir(DOWNLOAD_DIRECTORY):
			os.mkdir(DOWNLOAD_DIRECTORY)

	@property
	def path(self) -> str:
		"""Возвращает (будующее) местоположения файла на компьютере."""
		return DOWNLOAD_DIRECTORY+'/'+self.name

	def download(self):
		"""Скачивает файл на локальный компьютер."""
		CloudFile.ensure_root()
		urllib.request.urlretrieve(self.url, self.path)
