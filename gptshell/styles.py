from enum import Enum
# import click
from cmd2 import (
    Bg,
    Fg,
    style,
)

# class syntax
class Style(Enum):
    YOU = 1
    BOT = 2
    SYSTEM = 3
    INFO = 4
    IMPORTANT = 5
    PROMPT = 6
    ERROR = 7

    def style(self, text):
        if self == Style.YOU:
            return style(text, fg=Fg.WHITE)
        elif self == Style.BOT:
            return style(text, fg=Fg.DARK_GRAY)
        elif self == Style.SYSTEM:
            return style(text, bold=True, fg=Fg.GREEN)
        elif self == Style.INFO:
            return style(text, fg=Fg.LIGHT_BLUE)
        elif self == Style.IMPORTANT:
            return style(text, fg=Fg.LIGHT_RED)
        elif self == Style.PROMPT:
            return style(text, fg=Fg.BLUE)
        else: # Error
            return style(text, bold=True, fg=Fg.RED)


    