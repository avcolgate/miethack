def get_joined_ids(sql):
    names = sql.execute(f"SELECT names.ID, names.name FROM names INNER JOIN users ON users.ID = names.ID").fetchall() # Уже не понимаю почему так написано, мб баг
    return names

def get_joined_master_ids(sql):
    master_ids = sql.execute(f"SELECT users.master_id, names.name FROM names INNER JOIN users ON users.master_id = names.master_id").fetchall()
    return master_ids

def get_ids(sql):
    names_len = len(sql.execute(f"SELECT names.ID FROM names").fetchall())
    return names_len

def get_names(sql):
    names = sql.execute(f"SELECT names.name FROM names").fetchall()
    names = ''.join(str(x[0] + '\n\n') for x in names)
    return names


def get_masters(sql):
    masters = sql.execute(f"SELECT names.master_id FROM names ").fetchall()
    masters = ''.join(str(x[0] + '\n\n') for x in masters)
    return masters

def check_user_id(sql, master_id):
    names = sql.execute(f"SELECT master_id FROM names").fetchall()
    names = ''.join(str(x[0] + '\n\n') for x in names)
    if names != 0:
        return master_id not in names
    else:
        return 0