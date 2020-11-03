from timetable.lesson import Lesson

class Group(object):
    """Класс Group описывает рассписание группы.

    Аттрибуты
    ---------
    name : str
        Название группы.

    lessons : list
        Дисциплины группы.

    Методы
    ------
    append(nubmer, time, name, room)
        Добавляет дисциплину.
    """
    def __init__(self, name):
        """
        Параметры
        ---------
        name : str
            Название группы.
        """
        self.name=name
        self.lessons=list()

    def append(self, number, time, name, room):
        """Добавляет дисциплину."""
        _=Lesson(number, time, name, room)
        self.lessons.append(_)

    def __str__(self):
        """Возвращает текстовое представление дисциплин в виде таблицы."""
        
        # FIXME

        # table = texttable.Texttable()
        # table.add_row(['#', "time", self.Name, "room"])
        # for lesson in self.Lessons:
        #     table.add_row([lesson.Enum, lesson.Time, lesson.Name, lesson.Room])
        # return table.draw()
        return "FIXME"
        