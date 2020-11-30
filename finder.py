try:
	import tqdm
except:
	pass

import collection
import texttable
import traceback

def compare(obj, objects):
	"""Аналог any([obj == c_obj for c_obj in objects]), но без лишних проходов."""
	for c_obj in objects:
		if obj.find(c_obj) != -1:
			return True
	return False

def inspect(document):
	(departament, _warnings)=document.GetDepartament()
	headed=False
	for group in departament.groups:
		for lesson in group.lessons:
			if compare(lesson.name.lower(), to_find):
				if not headed:
					table.add_row(("*"*5, departament.name, document.date))
					headed=True
				table.add_row((lesson.time, lesson.name, lesson.room))

def main():
	try:
		a = tqdm.tqdm(docs)
	except:
		a = docs
	for document in a:
		try:
			inspect(document)
		except Exception as error:
			print("<%s/error> " % document.name + str(error))

if __name__ == "__main__":

	docs=collection.Documents()
	docs.load("documents.json")
	docs.refresh()

	table=texttable.Texttable()

	to_find=list()
	_c=str()
	print("Кого ищем? ['ok' для выхода]")
	while (_c := input(">>> ")) != "ok":
		to_find.append(_c.lower())
	del _c

	try:
		main()
		print(table.draw())
	except:
		print("\n::PANIC::\n")
		traceback.print_exc()
