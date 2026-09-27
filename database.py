import sqlite3

DATABASE = "blood_bridge.db"


def create_database():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_banks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            units INTEGER NOT NULL,
            location TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_blood_bank(name, blood_group, units, location, phone):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO blood_banks
        (name, blood_group, units, location, phone)
        VALUES (?, ?, ?, ?, ?)
    """, (name, blood_group, units, location, phone))

    connection.commit()
    connection.close()


def get_blood_banks():
    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM blood_banks")

    banks = cursor.fetchall()

    connection.close()

    return [dict(bank) for bank in banks]