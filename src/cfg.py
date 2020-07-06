def init():
    global PREFIX
    PREFIX = "$r "

    global bot
    bot = None

    global config
    config = {}

    global scheduler
    scheduler = None

    global db_con, db_cur
    db_con = None
    db_cur = None
