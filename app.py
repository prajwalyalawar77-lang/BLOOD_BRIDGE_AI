from flask import Flask, render_template, request
from database import create_database, add_blood_bank, get_blood_banks

app = Flask(__name__)
create_database()


# ==================================================
# BLOOD BANK DATA
# ==================================================

blood_data = [
    {
        "name": "Belagavi Life Care Blood Bank",
        "blood_group": "B-",
        "units": 3,
        "location": "Belagavi",
        "distance": 7.4,
        "phone": "9876543210"
    },
    {
        "name": "Belagavi Emergency Blood Centre",
        "blood_group": "AB-",
        "units": 2,
        "location": "Belagavi",
        "distance": 9.0,
        "phone": "9876543211"
    },
    {
        "name": "Belagavi Hope Blood Bank",
        "blood_group": "O+",
        "units": 8,
        "location": "Belagavi",
        "distance": 11.5,
        "phone": "9876543212"
    },
    {
        "name": "Belagavi Central Blood Bank",
        "blood_group": "A+",
        "units": 5,
        "location": "Belagavi",
        "distance": 5.2,
        "phone": "9876543213"
    },
    {
        "name": "Bengaluru Central Blood Bank",
        "blood_group": "O-",
        "units": 6,
        "location": "Bengaluru",
        "distance": 145,
        "phone": "9876543214"
    },
    {
        "name": "Bengaluru Life Blood Centre",
        "blood_group": "A-",
        "units": 7,
        "location": "Bengaluru",
        "distance": 148,
        "phone": "9876543215"
    },
    {
        "name": "Mysuru Blood Care Centre",
        "blood_group": "O+",
        "units": 10,
        "location": "Mysuru",
        "distance": 165,
        "phone": "9876543216"
    },
    {
        "name": "Hubballi Blood Bank",
        "blood_group": "B+",
        "units": 6,
        "location": "Hubballi",
        "distance": 105,
        "phone": "9876543217"
    },
    {
        "name": "Dharwad Life Saver Blood Bank",
        "blood_group": "AB+",
        "units": 4,
        "location": "Dharwad",
        "distance": 110,
        "phone": "9876543218"
    },
    {
        "name": "Mangaluru Emergency Blood Centre",
        "blood_group": "O-",
        "units": 4,
        "location": "Mangaluru",
        "distance": 325,
        "phone": "9876543219"
    }
]


# ==================================================
# BLOOD COMPATIBILITY
# ==================================================

compatibility = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"]
}


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# REGISTER BLOOD BANK
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        bank_name = request.form.get("bank_name", "").strip()
        blood_group = request.form.get("blood_group", "").strip().upper()
        units_text = request.form.get("units", "0").strip()
        location = request.form.get("location", "").strip()
        phone = request.form.get("phone", "").strip()

        try:
            units = int(units_text)
        except ValueError:
            units = 0

        if (
            bank_name
            and blood_group
            and units > 0
            and location
            and phone
        ):

            add_blood_bank(
                bank_name,
                blood_group,
                units,
                location,
                phone
            )

            new_bank = {
                "name": bank_name,
                "blood_group": blood_group,
                "units": units,
                "location": location,
                "phone": phone
            }

            return render_template(
                "register.html",
                success=True,
                bank=new_bank
            )

    return render_template(
        "register.html",
        success=False
    )

# ==================================================
# EMERGENCY
# ==================================================

@app.route("/emergency")
def emergency():
    return render_template("emergency.html")


# ==================================================
# MATCHING
# ==================================================



@app.route("/matches")
def matches():

    requested_blood = request.args.get(
        "blood_group",
        ""
    ).strip().upper()

    units_text = request.args.get(
        "units",
        "1"
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    emergency_level = request.args.get(
        "emergency",
        "Normal"
    ).strip()

    try:
        units_required = int(units_text)
    except ValueError:
        units_required = 1

    if units_required < 1:
        units_required = 1

    compatible_groups = compatibility.get(
        requested_blood,
        []
    )

    database_banks = get_blood_banks()

    matches_list = []

    for bank in database_banks:

        if bank["blood_group"] not in compatible_groups:
            continue

        if bank["units"] < units_required:
            continue

        match = bank.copy()

        if bank["blood_group"] == requested_blood:
            match["match_type"] = "Exact Match"
            match["priority"] = 1
        else:
            match["match_type"] = "Compatible Match"
            match["priority"] = 2

        if (
            location
            and location.lower() in bank["location"].lower()
        ):
            match["location_match"] = True
            match["priority"] -= 0.5
        else:
            match["location_match"] = False

        match["distance"] = 0

        matches_list.append(match)

    matches_list.sort(
        key=lambda x: (
            x["priority"],
            x["distance"]
        )
    )

    return render_template(
        "matches.html",
        matches=matches_list,
        blood_group=requested_blood,
        units=units_required,
        location=location,
        emergency=emergency_level
    )
# ==================================================
# START SERVER
# ==================================================

if __name__ == "__main__":
    create_database()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )