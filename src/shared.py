import cfg

# Check if a user can afford a certain price
def check_funds_available(ctx, price, amount):
    total_price = price * amount

    cfg.db_cur.execute("SELECT doubloons FROM Users WHERE uid=?;", (ctx.author.id,))
    result = cfg.db_cur.fetchone()

    return result["doubloons"] >= total_price


def detract_funds(ctx, price):
    cfg.db_cur.execute(
        "UPDATE Users SET doubloons=doubloons - ? WHERE uid=?",
        (price, str(ctx.author.id)),
    )

    cfg.db_conn.commit()


# Creates a table from the data in a discord markup string
# headers and key lists must be the same length
def create_table(category, headers, keys, data, offset):
    assert len(headers) == len(keys)

    # Category
    to_send = "**" + category + "**\n"

    # Get header sizes
    header_size = []

    for i in range(len(keys)):
        key_size = 0
        for element in data:
            key_size = max(key_size, len(str(element[keys[i]])))
        header_size.append(max(key_size, len(headers[i])))

    to_send += "```"

    # Headers
    headers_to_send = "Index | "

    for i in range(len(headers)):
        headers_to_send += str(headers[i]).ljust(header_size[i])
        headers_to_send += " | "
    headers_to_send = headers_to_send[:-3] + "\n"

    to_send += headers_to_send
    to_send += "-" * len(headers_to_send)
    to_send += "\n"

    # Data
    for i in range(len(data)):
        to_send += f"{i+1+offset:02d}".ljust(5) + " | "
        for j in range(len(keys)):
            to_send += str(data[i][keys[j]]).ljust(header_size[j])
            to_send += " | "
        to_send = to_send[:-3] + "\n"

    to_send += "```"

    return to_send
