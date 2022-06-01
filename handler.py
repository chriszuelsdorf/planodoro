import curses
from datetime import timedelta
import pathlib
import pygame

from objs import planodoro, ptimer


class Handler:
    def __init__(self, styles: dict):
        self.pomo = ptimer(25 * 60)
        self.plan = planodoro()
        self.styles = styles
        pygame.mixer.init()
        pygame.mixer.music.load(
            str(pathlib.Path(__file__).parent.absolute()) + "432.wav"
        )

    def handleme(self, inp: str, nlin, ncol):
        # this should return a dict
        # 'supd' is what to put in the status update
        # 'update_screen' is whether or not to update the screen
        # 'screen_updates' is the details if you want to update the screen
        # handler has custody of lines `2` to `nlin-3`
        def valslot(slot):
            if (
                int(slot[:2]) not in range(24)
                or int(slot[2:]) not in range(60)
                or len(slot) != 4
            ):
                return False
            return True

        if inp.startswith("pomo "):
            # pomo has custody of line 1 characters 1 to 6
            if inp == "pomo update":
                res = self.pomo.remains()
                if res["beep"] is True and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play()
                if res["beep"] is False and pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                if res["t_remain"] <= timedelta(seconds=0):
                    tts = "00:00"
                    sts = self.styles.get(
                        "notc_blink" if res["flash_t_remain"] else "norm"
                    )
                elif res["t_remain"] > timedelta(seconds=0):
                    tts = f"{res['t_remain'].seconds//60:>2}:{res['t_remain'].seconds%60:0>2}"
                    sts = self.styles.get(
                        "notc_blink" if res["flash_t_remain"] else "norm"
                    )
                return {
                    "supd": ["Pomo updated!", "norm"],
                    "update_screen": True,
                    "screen_updates": [[0, 1, tts, sts]],
                }
            elif inp.startswith("pomo start "):
                if not inp[11:].isdigit():
                    return {
                        "supd": [
                            f"Pomo start error - nan minutes `{inp[11:]}`!\a",
                            "norm_blink",
                        ],
                        "update_screen": False,
                    }
                self.pomo = ptimer(int(inp[11:]) * 60)
                self.pomo.start()
                return {"supd": ["Pomo Started!", "norm"], "update_screen": False}
            elif inp == "pomo pause":
                self.pomo.pause()
                return {"supd": ["Pomo Paused!", "norm"], "update_screen": False}
            elif inp == "pomo reset":
                self.pomo = ptimer(self.pomo.limit.total_seconds())
                return {"supd": ["Pomo Reset!", "norm"], "update_screen": False}
            elif inp == "pomo help":
                lines = [
                    "--> `pomo update` - updates the timer widget. This is done about",
                    "               every tenth of a second, so no need to do it manually.",
                    "--> `pomo start x` - starts a pomo timer for x minutes.",
                    "--> `pomo pause` - pauses or unpauses a pomo timer.",
                    "--> `pomo reset` - resets the pomo timer to the same time as the last",
                    "               one.",
                    "--> `pomo help` - shows this text.",
                ]
                return {
                    "supd": ["Pomo Help", "norm"],
                    "update_screen": True,
                    "screen_updates": [[2, 0, " " * ncol * (nlin - 4)]]
                    + [
                        [i + 2, 0, lines[i], self.styles.get("norm")]
                        for i in range(len(lines))
                    ],
                }
            else:
                return {
                    "supd": [
                        f"Pomo: Unrecognized command, use `pomo help` for help",
                        "norm_blink",
                    ],
                    "update_screen": False,
                }
        elif inp.startswith("plan "):
            if inp in ("plan show", "plan") or (
                inp.startswith("plan show ") and inp[10:].isdigit()
            ):
                return {
                    "supd": ["Plan", "norm"],
                    "update_screen": True,
                    "screen_updates": [
                        x + [self.styles.get("norm")]
                        for x in self.plan.showme(
                            nlin,
                            ncol,
                            0 if inp in ("plan show", "plan") else int(inp[10:]),
                        )
                    ],
                }
            elif inp.startswith("plan slot "):
                try:
                    slot = inp.split()[2]
                    desc = " ".join(inp.split()[3:])
                    if not valslot(slot):
                        raise ValueError("Bad slot")
                    self.plan.upsert_tslot(slot, desc)
                    return {
                        "supd": [f"Plan Slot: Slot {slot} updated", "norm"],
                        "update_screen": True,
                        "screen_updates": [
                            x + [self.styles.get("norm")]
                            for x in self.plan.showme(nlin, ncol, 0)
                        ],
                    }
                except Exception as e:
                    return {
                        "supd": [f"Plan Slot: Bad command `{inp}`", "norm_blink"],
                        "update_screen": False,
                    }
            elif inp.startswith("plan rem "):
                try:
                    slot = inp.split()[2]
                    res1 = self.plan.rem_tslot(slot)
                    return {
                        "supd": [
                            f"Plan Rem: Slot {slot} {'removed' if res1 else 'failed to remove, not present'}",
                            "norm",
                        ],
                        "update_screen": True,
                        "screen_updates": [
                            x + [self.styles.get("norm")]
                            for x in self.plan.showme(nlin, ncol, 0)
                        ],
                    }
                except Exception as e:
                    return {
                        "supd": [f"Plan Slot: Bad command `{inp}`", "norm_blink"],
                        "update_screen": False,
                    }
            elif inp == "plan help":
                lines = [
                    "--> `plan show` - updates or switches to the plan view. This is done",
                    "               automatically every update, but use it to swtich.",
                    "--> `plan slot x y` - adds or updates plan slot x with description y.",
                    "--> `plan rem x` - removes entry at slot x.",
                    "--> `plan help` - shows this text.",
                ]
                return {
                    "supd": ["Plan Help", "norm"],
                    "update_screen": True,
                    "screen_updates": [[2, 0, " " * ncol * (nlin - 4)]]
                    + [
                        [i + 2, 0, lines[i], self.styles.get("norm")]
                        for i in range(len(lines))
                    ],
                }
            return {
                "supd": [
                    f"Plan: Unrecognized command, use `plan help` for help",
                    "norm_blink",
                ],
                "update_screen": False,
            }
        elif inp == "help":
            lines = [
                "--> `plan help` - shows help for the plan command",
                "--> `pomo help` - shows help for the pomo command",
            ]
            return {
                "supd": ["Plan Help", "norm"],
                "update_screen": True,
                "screen_updates": [[2, 0, " " * ncol * (nlin - 4)]]
                + [
                    [i + 2, 0, lines[i], self.styles.get("norm")]
                    for i in range(len(lines))
                ],
            }
        else:
            curses.beep()
            return {
                "supd": ["Unknown command, use `help` for help!", "norm_blink"],
                "update_screen": False,
            }
