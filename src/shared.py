from cfg import bot

import cfg

# Check if a user can afford a certain price
def check_funds_available(ctx, price, amount):
    total_price = price * amount

    cfg.db_cur.execute("SELECT doubloons FROM Users WHERE uid=?;", (ctx.author.id,))
    result = cfg.db_cur.fetchone()

    return result["doubloons"] >= total_price


def detract_funds(ctx, price):
    cfg.db_cur.execute(
        "UPDATE Users SET doubloons=doubloons - ? WHERE uid=?;",
        (price, str(ctx.author.id)),
    )

    cfg.db_con.commit()


# Creates a table from the data in a discord markup string
# headers and key lists must be the same length
def create_table(category, headers, keys, data, offset, index=True):
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
    if index:
        headers_to_send = "Index | "
    else:
        headers_to_send = ""

    for i in range(len(headers)):
        headers_to_send += str(headers[i]).ljust(header_size[i])
        headers_to_send += " | "
    headers_to_send = headers_to_send[:-3] + "\n"

    to_send += headers_to_send
    to_send += "-" * len(headers_to_send)
    to_send += "\n"

    # Data
    for i in range(len(data)):
        if index:
            to_send += f"{i+1+offset:02d}".ljust(5) + " | "
        for j in range(len(keys)):
            to_send += str(data[i][keys[j]]).ljust(header_size[j])
            to_send += " | "
        to_send = to_send[:-3] + "\n"

    to_send += "```"

    return to_send


# Takes ids from a query and turns the id into a name
# Returns a list of dicts similar to a sqlite row object
def convert_id_to_name_key(data, key_to_change, new_key):
    new_list = []
    
    for row in data:
        new_dict = dict(row)

        user = bot.get_user(int(row[key_to_change]))

        # Check if user was found
        if user:
            username = user.name
        else:
            username = "Username not found"

        new_dict[new_key] = username
        new_list.append(new_dict)

    return new_list