from datetime import datetime


class GUULogging:
    def __init__(self):
        self.log: str = "[[GUU EVENT LOG - START]]\n"

    def new(self, lvl: int, isr: int, string: str):
        levels = {1: "Info", 2: "Warning", 3: "Error"}
        issuers = {1: "GUU", 2: "API", 3: "CLT"}

        info = "[{} | {} | {}] ".format(datetime.now().strftime("%H:%M:%S"),
                                        levels[lvl], issuers[isr])
        text = info + string
        self.log += text
        self.log += "\n"
        print(text)

    def get(self):
        self.log += "[[GUU EVENT LOG - END]]\n"
        return self.log
