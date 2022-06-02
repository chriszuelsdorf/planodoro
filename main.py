import curses, _curses
import string
import datetime
import time
from handler import Handler


PROG_VERSION = "v1.2.0 b.458"


def submain(stdscr: _curses.window):
    # curses.init_color(24, 800, 0, 0)
    curses.init_pair(25, curses.COLOR_WHITE, 24)
    tcolor_alert = curses.color_pair(25)
    curses.init_color(26, 804, 517, 204)
    curses.init_pair(27, 26, curses.COLOR_BLACK)
    tcolor_reg = curses.color_pair(27)
    curses.init_color(29, 800, 800, 0)
    curses.init_pair(28, 29, curses.COLOR_BLACK)
    tcolor_notice = curses.color_pair(28)
    curses.init_pair(30, curses.COLOR_RED, curses.COLOR_BLACK)
    tcolor_red = curses.color_pair(30)

    BOXCHAR_VERTLINE = "│"
    BOXCHAR_HORILINE = "─"
    BOXCHAR_INVERTEDT = "┴"

    def showsizewarn(stdscr: _curses.window = stdscr):
        curses.update_lines_cols()
        if curses.LINES < 24 or curses.COLS < 70:
            stdscr.clear()
            stdscr.addstr(
                3,
                0,
                f"Size is {curses.LINES}x{curses.COLS}, must be at least 24x70 to properly use planodoro!",
                tcolor_alert | curses.A_BLINK,
            )
            stdscr.refresh()
        else:
            stdscr.addstr(0, 12, " " * (curses.COLS - 12))
        return curses.LINES < 24 or curses.COLS < 70, curses.LINES, curses.COLS

    # stdscr.nodelay(True) # This proved largely too problematic - took up wayyy too much CPU!
    curses.halfdelay(1)
    szwarn, nlin, ncol = showsizewarn()

    style_di = {
        "norm": tcolor_reg,
        "norm_blink": tcolor_reg | curses.A_BLINK,
        "notc": tcolor_notice,
        "notc_blink": tcolor_notice | curses.A_BLINK,
        "alert": tcolor_alert,
        "alert_blink": tcolor_alert | curses.A_BLINK,
        "red": tcolor_red,
        "red_blink": tcolor_red | curses.A_BLINK,
    }

    hand = Handler(style_di)

    def supd(string, styles="norm"):
        # this has custody of line 1 cols 8 to -10 but must include 4 chars of padding before & after
        nonlocal style_di
        sts = string[: ncol - 21]
        stdscr.addstr(0, 9, " " * (ncol - 21))
        temp_style = style_di.get(styles)
        # stdscr.addstr(2, 0, f"{styles}, {temp_style}", tcolor_reg)
        if temp_style is not None:
            stdscr.addstr(
                0, (9 + int((ncol - 21) / 2)) - int(len(sts) / 2), sts, temp_style
            )
        else:
            stdscr.addstr(
                0, (9 + int((ncol - 21) / 2)) - int(len(sts) / 2), sts, tcolor_reg
            )
        stdscr.refresh()

    def addcursor(stdscr, buff):
        toadd = ">>> " + buff + (" " * (ncol - 5 - len(buff)))
        if len(toadd) >= ncol:
            supd("Max character length exceeded!")
        else:
            stdscr.addstr(nlin - 1, 0, toadd, tcolor_reg)
            stdscr.addstr(nlin - 1, len(buff) + 4, "_", tcolor_reg | curses.A_BLINK)
            stdscr.refresh()

    def updtime(stdscr):
        stdscr.addstr(
            0,
            ncol - 10,
            " " + datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S") + " ",
            tcolor_reg,
        )
        stdscr.refresh()

    def callhand(opt_buf=None, supd_off=False):
        tmp_args = hand.handleme(opt_buf if opt_buf else buf, nlin, ncol)
        try:
            if not supd_off and "supd" in tmp_args:
                supd(*tmp_args["supd"])
            if tmp_args["update_screen"] is True:
                for upd in tmp_args["screen_updates"]:
                    stdscr.addstr(*upd)
        except Exception as e:
            if upd:
                print(len(upd))
                print(upd)
                time.sleep(3)
            print(tmp_args)
            time.sleep(3)
            raise e
        stdscr.refresh()

    buf = ""
    hasnorm = False
    debugmode = False
    stdscr.addstr(nlin - 1, 0, "_ ", tcolor_reg | curses.A_BLINK)
    addcursor(stdscr, buf)
    callhand("plan show")
    stdscr.refresh()
    bufhist = []
    lastcall = {"plan show": ""}
    curscreen = None
    while True:
        try:
            # time.sleep(0.016) # was using this to slow loop when nodelay was True
            updtime(stdscr)
            callhand("pomo update", supd_off=True)
            if curscreen is not None:
                callhand(lastcall[curscreen])
            inp = stdscr.getkey()
            if debugmode:
                supd("key: `" + inp + "`", "notc")
                time.sleep(0.35)
        except _curses.error as e:
            inp = None
        if inp == "KEY_RESIZE":
            szwarn, nlin, ncol = showsizewarn()
        if (hasnorm is False) or (inp is not None):
            if debugmode:
                supd("Refreshed Norms")
            hasnorm = True
            stdscr.addstr(
                1,
                0,
                (BOXCHAR_HORILINE * 7)
                + BOXCHAR_INVERTEDT
                + (BOXCHAR_HORILINE * (ncol - 19))
                + BOXCHAR_INVERTEDT
                + ((BOXCHAR_HORILINE * 10)),
                tcolor_reg,
            )
            stdscr.addstr(nlin - 2, 0, BOXCHAR_HORILINE * ncol, tcolor_reg)
            stdscr.addstr(0, 7, BOXCHAR_VERTLINE + " ", tcolor_reg)
            stdscr.addstr(0, ncol - 12, " " + BOXCHAR_VERTLINE + " ", tcolor_reg)
        if szwarn is False and isinstance(inp, str) and len(inp) == 1:
            if inp == curses.KEY_ENTER or ord(inp) == 10:
                curscreen = None
                if debugmode:
                    supd("Enter key")
                bufhist.append(inp)
                if len(bufhist) > 500:
                    bufhist = bufhist[:500]
                if buf in ["exit", "quit"]:
                    break
                elif buf == "debug":
                    debugmode = not debugmode
                    supd(
                        f"Debug Mode {'ON - 0.35s delay & extra statuses' if debugmode is True else 'OFF'}",
                        "notc",
                    )
                elif buf == "test":
                    supd(
                        f"This is a test message!",
                        "alert_blink",
                    )
                elif buf == "version":
                    supd(f"planodoro {PROG_VERSION}", "notc")
                else:
                    callhand()
                # update lastcall
                if buf.startswith("plan") and "help" not in buf:
                    curscreen = "plan show"
                    lastcall["plan show"] = "plan show"
                buf = ""
                addcursor(stdscr, buf)
            elif inp == curses.KEY_BACKSPACE or ord(inp) == 127:
                if debugmode:
                    supd("backspace")
                if len(buf) > 0:
                    buf = buf[: len(buf) - 1]
                    addcursor(stdscr, buf)
                    stdscr.refresh()
            elif inp in string.ascii_letters + string.digits + string.punctuation + " ":
                if len(buf) + 1 < ncol - 5:
                    if debugmode:
                        supd(f"inputbox - `{inp}` - buf was `{buf}`")
                    buf += inp
                    addcursor(stdscr, buf)
                else:
                    supd("Attemped to exceed max input length!", "notc_blink")
            else:
                supd(f"Non-accepted key `{inp}`", "notc_blink")


def main(stdscr):
    curses.curs_set(0)
    try:
        submain(stdscr)
    finally:
        curses.curs_set(1)


if __name__ == "__main__":
    curses.wrapper(main)
