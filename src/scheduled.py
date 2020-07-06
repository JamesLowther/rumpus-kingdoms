import schedule
import threading
import time

import cfg

def reset_tax_collected_flag():
    cfg.db_cur.execute("UPDATE Users SET tax_collected=0;")
    cfg.db_con.commit()

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
schedule.every().day.at("23:59").do(reset_tax_collected_flag)
#schedule.every(3).seconds.do(test)