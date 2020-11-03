import datetime
import zipfile
import bs4
import re

MONTHS_ABBRS=\
(('jan', 'янв', 1),
 ('feb', 'фев', 2),
 ('mar', 'мар', 3),
 ('apr', 'апр', 4),
 ('may', 'май', 5),
 ('jun', 'июн', 6),
 ('jul', 'июл', 7),
 ('aug', 'авг', 8),
 ('sep', 'сен', 9),
 ('oct', 'окт', 10),
 ('nov', 'ноя', 11),
 ('dec', 'дек', 12))

DATE_REGEX=r"([0-9]+)[ ,.-]{1,2}([а-яА-Яa-zA-Z0-9]+)[ ,.-]{1,2}([0-9]+)"
def ParseDate(string) -> datetime.date:
	"""Возвращает метку даты из строки или «нулевую» дату.

	Метка
	-----
	Состоит из трех частей, разделенных пробелом, запятой, тире или
	точкой. Центральная часть,- месяц, может быть определена по первым
	трем буквам названия на русском или на английском. Первая и
	последняя - день и год соответственно.

	Параметры
	---------
	string : str
		Анализируемая строка.

	Возврат
	-------
	Метку даты из строки или, если ее не удалось обнаружить, «нулевую»
	дату 1'th January, 1970 year.
	"""
	match=re.search(DATE_REGEX, string)
	if match == None:
		return datetime.date(1970, 1, 1)
	day, month, year=match.groups()
	try:
		month=int(month)
	except:
		month=month.strip().lower()
		_temp=month
		for abbr in MONTHS_ABBRS:
			if month.startswith(abbr[1]) or month.startswith(abbr[0]):
				month=abbr[2]
				break
		if month == _temp:
			return datetime.date(1970, 1, 1)
		del _temp
	try:
		day=int(day)
		year=int(year)
	except:
		return datetime.date(1970, 1, 1)
	return datetime.date(year, month, day)

DEP_REGEX=r"( |^)(?=(Р|р))[а-яА-Яa-zA-Z -]+"
def ParseDepartamentName(name):
	"""Возвращает имя рассписания из имени его документа."""
	match=re.search(DEP_REGEX, name)
	if match == None:
		return f"'{name}'"
	return match.group().strip()

def ParseTable(document, without_first_column=False):
	"""Лексирует общую таблицу из документа.

	Все таблицы в документе объединяются в одну. Она нормализуется по
	среднему колличеству столбцов в строчках. Из этого вытекают
	возможные ошибки лексинга.

	Параметры
	---------
	document : collection.document.Document
		Лексируемый документ.

	without_first_column : bool
		Если True, то удаляет первый столбец из таблицы.

	Возврат
	-------
	return (table, shape, warnings)
	
	table : list
		Пролексированая таблица вида списка списков.

	shape : tuple
		Размер table вида (rows, columns).

	warnings : tuple
		Предупреждения о возможных ошибках лексирования. Кортеж строк.
	"""
	if not document.name.endswith(".docx"):
		raise ValueError("Поддерживается исключительно формат docx.")

	with zipfile.ZipFile(document.path, 'r') as archive:
		soup=bs4.BeautifulSoup(archive.read("word/document.xml"), "xml")

	retr=list()
	for table in soup.body.find_all("tbl"):
		for row in table.find_all("w:tr"):
			retr.append(list())
			for cell in row.find_all("w:tc"):
				lines=list()
				for line in cell.find_all("w:t"):
					lines.append(line.text)
				content='\n'.join(lines)
				retr[-1].append(content)
			if without_first_column and len(retr[-1]) != 0:
				del retr[-1][0]
	warnings=list()
	# Колличества столбцов в записях.
	counts=list(map(len, retr))
	if len(counts) == 0:
		raise Exception("В документе отсутствует таблица.")
	# Их среднее должно быть целочисленным.
	mean=sum(counts)/len(counts)
	if mean % 1 > 0:
		# Иначе таблица содержит дефекты.
		mean=int(mean)
		for index in range(len(retr)):
			while counts[index] != mean:
				if counts[index] < mean:
					retr.append("N/A")
					warnings.append(
						"При нормализации таблицы была добавлена "
					   +"отсутствующая ячейка. Возможна потеря данных.")
					counts[index] += 1

				elif counts[index] > mean:
					data=retr[index].pop(-1)
					warnings.append(
						"При нормализации таблицы была "
					  +f"удалена лишняя ячейка с значением '{data}'.")
					counts[index] -= 1
	shape=(len(retr), int(mean))
	return (retr, shape, tuple(warnings))
