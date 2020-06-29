def init():
    global PREFIX
    PREFIX = "$r "

    global bot
    bot = None

    global root_ids
    root_ids = None

    global attack_options, defence_options
    attack_options = None
    defence_options = None

    global base_village_price
    base_village_price = None

    global db_conn, db_cur
    db_conn = None
    db_cur = None
