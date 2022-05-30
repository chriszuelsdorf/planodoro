import curses


def main(stdscr):
    curses.init_color(0, 0, 0, 0)
    curses.init_color(1, 680, 0, 0)
    curses.init_color(2, 0, 680, 0)
    curses.init_color(3, 680, 680, 0)
    curses.init_color(4, 0, 0, 680)
    curses.init_color(5, 680, 0, 680)
    curses.init_color(6, 0, 680, 680)
    curses.init_color(7, 680, 680, 680)
    curses.init_color(8, 0, 0, 0)
    curses.init_color(9, 1000, 0, 0)
    curses.init_color(10, 0, 1000, 0)
    curses.init_color(11, 1000, 1000, 0)
    curses.init_color(12, 0, 0, 1000)
    curses.init_color(13, 1000, 0, 1000)
    curses.init_color(14, 0, 1000, 1000)
    curses.init_color(15, 1000, 1000, 1000)


if __name__ == "__main__":
    curses.wrapper(main)
