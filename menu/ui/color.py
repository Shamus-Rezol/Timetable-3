"""Модуль color инициализирует цвета и предоставляет их индексы.

Необходимо инициализировать главное окно curses.initscr() и
инициализировать переменные модуля init().
"""
import curses

'''
Ключи colors будут глобальными переменными со значениями индекса цвета.
То есть для каждого k, v инициализируется цвет curses.init_pair(i, *v),
где v - кортеж цвета вида (fore, back), а i - его индекс. global k; k=i.
'''
colors=\
{"cursor": (226, 16),
 "cursor2": (118, 16),
 "label": (3, 16),
 "hightlighted": (208, 16),
 "hightlighted2": (228, 232),
 "header": (129, 255),
 "button": (117, 232),
 "checkable": (39, 232)}

def init():
    """Инициализирует переменные модуля и цвета curses.

    Первым необходимо инициализировать главное окно curses.
    """
    global colors

    curses.start_color()
    curses.use_default_colors()

    counter=1
    for attr, color in colors.items():
        curses.init_pair(counter, *color)
        globals()[attr]=counter
        counter+=1
