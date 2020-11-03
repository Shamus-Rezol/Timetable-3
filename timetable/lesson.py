import datetime

class Lesson(object):
    """Класс Lesson описывает дисциплину.

    Аттрибуты
    ---------
    number : str
        Номер в рассписании группы.
        
    time : datetime.time
        Время начала.

    name : str
        Название.

    room : str
        Аудитория.
    """

    def __init__(self, number, time, name, room):
        """
        Параметры
        ---------
        number : str
            Номер дисциплины в рассписании группы.

        time : tuple
            Время начала дисциплины. Является кортежем вида (hour,
            minute).

        name : str
            Название дисциплины.

        room : str
            Аудитория дисциплины.
        """
        self.number=number
        self.time=datetime.time(*time)
        self.name=name
        self.room=room
