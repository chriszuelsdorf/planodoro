from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(order=True)
class timeslot:
    slotname: str
    slotdesc: str


class planodoro:
    def __init__(self) -> None:
        self.tslots = {}

    def upsert_tslot(self, name, desc) -> None:
        if (
            int(name[:2]) not in range(24)
            or int(name[2:]) not in range(60)
            or len(name) != 4
        ):
            raise ValueError("Invalid name")
        self.tslots[name] = timeslot(name, desc)

    def rem_tslot(self, name) -> bool:
        if name in self.tslots:
            del self.tslots[name]
            return True
        return False

    def gslots(self) -> list:
        """Get a sorted list of timeslots"""
        return sorted(list(self.tslots.values()))

    def showme(self, nlin, ncol, slin):
        need_to_show = [" TIME : TASK", f" ---- : {'-' * (ncol-9)} "]
        like_to_show = [
            f" {x.slotname} : {x.slotdesc[:ncol-9]} " for x in self.gslots()
        ]
        # like to show has nlin-6 lines
        if len(like_to_show) <= (nlin - 6):
            to_show = need_to_show + like_to_show
        else:
            t_available_lin = nlin - 6
            # There is a fixed point at len(like_to_show) - t_available_lin
            offset = min(slin, len(like_to_show) - t_available_lin)
            to_show = need_to_show + like_to_show[offset : offset + t_available_lin]
        return [[2, 0, " " * ncol * (nlin - 4)]] + [
            [i + 2, 0, to_show[i]] for i in range(len(to_show))
        ]


class ptimer:
    def __init__(self, limit_secs: float):
        self.accum = timedelta(seconds=0)
        self.stime = datetime.now() - timedelta(minutes=limit_secs + 1)
        self.active = False
        self.limit = timedelta(seconds=limit_secs)

    def remains(self):
        if self.active:
            # this is the running or finished case
            tremain = self.limit - self.accum - (datetime.now() - self.stime)
            if tremain <= timedelta(seconds=0):
                # this is the finished case
                return {"t_remain": tremain, "flash_t_remain": True, "beep": True}
            else:
                # this is the running case
                return {"t_remain": tremain, "flash_t_remain": False, "beep": False}
        elif not self.active and self.accum > timedelta(seconds=0):
            # this is the paused case
            tremain = self.limit - self.accum
            return {"t_remain": tremain, "flash_t_remain": True, "beep": False}
        else:
            # this is the not-yet-started case
            return {
                "t_remain": timedelta(seconds=0),
                "flash_t_remain": self.active,
                "beep": False,
            }

    def pause(self):
        if self.active:
            self.accum += datetime.now() - self.stime
            self.active = False
        else:
            self.start()

    def start(self):
        if not self.active:
            self.stime = datetime.now()
            self.active = True
