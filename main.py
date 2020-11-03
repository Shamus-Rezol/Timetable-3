"""Повседневное получение информации о рассписании."""

# FIXME, TODO
# Допустим скачивание файла провалилось. Конечно же, можно повторить
# попытку, но это НЕ РЕАЛИЗОВАНО, и это проблема.

# TODO Сделать контейнер хранения каких-то данных в пунктах меню.
# TODO Прокрутка при появлении новых конвертированых документов.
# TODO Исправить имена функций

__version__ = "3.0.0"
__author__  = "Shamus Rezol"

DOCS_FILE="documents.json"
PREFS_FILE="preferences.json"

import panic

import menu
import collection

from preferences import Preferences

import os
import time
import uuid
import subprocess
import traceback

import texttable

def show_help():
	"""Инициализирует меню помощи, помогающее разобраться с управлением."""
	mmenu.setup_batch_handler(None)
	mmenu.clear()

	mmenu.append(menu.Header, "СПРАВКА ОБ УПРАВЛЕНИИ")

	_=mmenu.append(menu.Button, "назад")
	_.connect(menu.event.click, main)

	mmenu.append(menu.Empty)

	text="Нажмите ВВОД для выполнения выделенного пункта."
	mmenu.append(menu.Label, text)

	_=mmenu.append(menu.Button, "Выполнить прыжок вниз.")
	_.connect(menu.event.click, mmenu.advance, 1)

	text="Для перемещения используйте стрелочки вверх/вниз."
	mmenu.append(menu.Label, text)

	_=mmenu.append(menu.Button, "..вверх.")
	_.connect(menu.event.click, mmenu.advance, -1)

	_=mmenu.append(menu.Button, "Звуковой сигнал.")
	_.connect(menu.event.click, menu.curses.beep)

	text="Пункты могут быть осложнены возможностью их выделения."
	mmenu.append(menu.Label, text)

	text="При переходе на них курсор (звездочка) меняет цвет."
	mmenu.append(menu.Label, text)
	mmenu.append(menu.Button, "Обычная кнопка", 4)
	mmenu.append(menu.Checkable, "Выделяемая", 4)

	text="Для выделения таких нажимается ПРОБЕЛ или стрелочки в бок."
	mmenu.append(menu.Label, text)

	for i in range(1, 10):
		text="Звуковой сигнал 0x%s" % str(i).rjust(8, '0')
		_=mmenu.append(menu.Checkable, text, 4)
		_.connect(menu.event.click, time.sleep, 0.4)
		_.connect(menu.event.click, menu.curses.beep)

	text="Для последовательного выполнения выделенных нажимается E (en)."
	mmenu.append(menu.Label, text)
	mmenu.append(menu.Label, "Для инвертации I.")
	mmenu.append(menu.Label, "Для сброса S.")

	mmenu.append(menu.Empty)

	_=mmenu.append(menu.Button, "В главное меню")
	_.connect(menu.event.click, main)

	mmenu.skip_non_selectable(1)
	mmenu.advance(1)

def SortDocsByPrefs(item):
	dep_name=item[0].lower()
	for i, dep in enumerate(prefs.departaments):
		if dep_name.find(dep) != -1:
			return 2**(10+i)
	return len(dep_name)

def show_departament(doc, dep):
	try:
		ROOT="./~tmp"
		file=uuid.uuid4().hex + ".tt"
		path=ROOT+'/'+file

		if not os.path.isdir(ROOT):
			os.mkdir(ROOT)

		tbl=texttable.Texttable()
		for group in dep.groups:
			if not group.name.lower() in prefs.groups:
				continue
			tbl.add_row(('№', "time", group.name, "room"))
			for lesson in group.lessons:
				tbl.add_row((lesson.number, lesson.time, lesson.name, lesson.room))
			tbl.add_row(('', '', '', ''))

		with open(path, 'w', encoding="utf-8") as fp:
			data=tbl.draw()
			fp.write(doc.name+'\n\n')
			fp.write(data if data != None else "Не найдена ни одна группа из '%s'."%PREFS_FILE)

		NOTEPAD="D:/Program Files/Sublime Text 3/sublime_text.exe"
		subprocess.Popen((NOTEPAD, path))
	except:
		raise

def view_departaments(document_names, departaments):
	try:
		ROOT="./~tmp"
		file=uuid.uuid4().hex + ".tt"
		path=ROOT+'/'+file

		if not os.path.isdir(ROOT):
			os.mkdir(ROOT)

		tables=list()
		for i, departament in enumerate(departaments):
			tbl=texttable.Texttable()
			for group in departament.groups:
				if not group.name.lower() in prefs.groups:
					continue
				tbl.add_row(('№', "time", group.name, "room"))
				for lesson in group.lessons:
					tbl.add_row((lesson.number, lesson.time, lesson.name, lesson.room))
			tables.append((document_names[i], tbl))

		with open(path, 'w', encoding="utf-8") as fp:
			for doc_name, tbl in tables:
				data=tbl.draw()
				fp.write(doc_name+'\n\n')
				fp.write(data+'\n\n' if data != None else "Не найдена ни одна группа из '%s'."%PREFS_FILE)

		NOTEPAD="D:/Program Files/Sublime Text 3/sublime_text.exe"
		subprocess.Popen((NOTEPAD, path))
	except:
		raise

def show_departaments():
	"""Инициализирует меню департаментов."""
	def batch_handler(*items):
		def batch_handler2(*items):
			deps=list()
			names=list()
			for i in items:
				if "__document" in dir(i) and "__departament" in dir(i):
					doc=i.__document
					dep=i.__departament
					names.append(doc.name)
					deps.append(dep)
			view_departaments(names, deps)

		mmenu.setup_batch_handler(batch_handler2, True)
		mmenu.clear()

		mmenu.append(menu.Header, "Просмотр")

		_=mmenu.append(menu.Button, "назад")
		_.connect(menu.event.click, show_departaments)

		mmenu.append(menu.Empty)

		for i in items:
			if "__document" in dir(i):
				doc=i.__document

				mmenu.append(menu.Label, doc.name)
				try:
					(dep, warnings)=doc.GetDepartament()

					if len(warnings) != 0:
						whats="Предупреждения о возможных ошибках:"
						_=mmenu.append(menu.Button, "Предупреждения", 2)
						_.connect(menu.event.click, panic.info, whats,
							'\n'.join(warnings), (232, 199), (51, 232),
							mmenu.refresh)
					_=mmenu.append(menu.Checkable, "Просмотр", 2)
					_.connect(menu.event.click, show_departament, doc, dep)
					_.__document=doc
					_.__departament=dep
				except:
					whats="Критическая ошибка (пропущена):"
					exc=traceback.format_exc()
					_=mmenu.append(menu.Button, "Критическая ошибка.", 2)
					_.connect(menu.event.click, panic.info, whats,
						exc, (231, 4), (51, 232), mmenu.refresh)
				mmenu.append(menu.Empty)
				mmenu.refresh()
		mmenu.skip_non_selectable(1)
		mmenu.advance(1)

	mmenu.setup_batch_handler(batch_handler, True)
	mmenu.clear()

	mmenu.append(menu.Header, "Меню конвертации документов")

	_=mmenu.append(menu.Button, "назад")
	_.connect(menu.event.click, main)

	mmenu.append(menu.Empty)

	groups=dict()
	for document in docs:
		group=document.departament_name
		if not group in groups.keys():
			groups[group]=list()
		groups[group].append(document)
	groups=sorted(groups.items(), key=SortDocsByPrefs, reverse=True)

	for group, documents in groups:
		mmenu.append(menu.WaveDown, group)
		for document in documents:
			text=document.date.strftime("%Y-%m-%d")

			if text == "1970-01-01":
				text=document.name

			if document.with_changes:
				text+=" [изменения]"

			_=mmenu.append(menu.Checkable, text, 2)
			_.connect(menu.event.click, batch_handler, _)
			_.__document=document
		mmenu.append(menu.Empty)
	mmenu.skip_non_selectable(1)
	mmenu.advance(1)

def show_warnings():
	"""Показывает список предупреждений, возникших в ходе получения списка документов."""
	whats="Предупреждения об возможных ошибках в списке документов:"
	message='\n'.join(docs.warnings)
	panic.info(whats, message, (232, 199), (51, 232), refresh=mmenu.refresh)

def main():
	"""Инициализирует главное меню."""
	mmenu.setup_batch_handler(None)
	mmenu.clear()

	text="Timetable Application [v{}]"
	mmenu.append(menu.Header, text.format(__version__))

	text="Список обновлялся "
	mmenu.append(menu.Label, text+docs.timestamp)

	_=mmenu.append(menu.Button, "Обновить список")
	_.connect(menu.event.click, docs.refresh)
	_.connect(menu.event.click, docs.dump, DOCS_FILE)
	_.connect(menu.event.click, main)

	mmenu.append(menu.Empty)

	_=mmenu.append(menu.Button, "Отделения")
	_.connect(menu.event.click, show_departaments)

	if len(docs.warnings) != 0:
		text="Предупреждения (%d)"%len(docs.warnings)
		_=mmenu.append(menu.Button, text)
		_.connect(menu.event.click, show_warnings)

	mmenu.append(menu.Empty)

	_=mmenu.append(menu.Button, "Справка")
	_.connect(menu.event.click, show_help)

	_=mmenu.append(menu.Button, "Выход")
	_.connect(menu.event.click, exit)

	mmenu.skip_non_selectable(1)

if __name__ == "__main__":
	menu.init()
	try:
		mmenu=menu.Menu()
		
		docs=collection.Documents()
		docs.load(DOCS_FILE)

		prefs=Preferences(PREFS_FILE)

		main()
		mmenu.run()
	except SystemExit:
		pass
	except:
		panic.panic()
