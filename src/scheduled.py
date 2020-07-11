import schedule
import threading
import time

import cfg
import currency


def test():
    print("here")


class Scheduler:
    def __init__(self):
        self.running = True

        self.t = threading.Thread(target=self.schedule_loop)
        self.t.start()

    def shutdown_threads(self):
        self.running = False
        self.t.join()
        print("Scheduler stopped")

    def schedule_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)


# Add scheduled events here
schedule.every().day.at("23:59").do(currency.calculate_new_tax_rate)
# schedule.every(3).seconds.do(test)
