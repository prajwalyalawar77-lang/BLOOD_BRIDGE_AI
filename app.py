from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# =========================================================
# DEMO BLOOD DATABASE
# =========================================================

blood_database = [

    {
        "name": "City Blood Bank",
        "type": "O+",
        "units": 5,
        "location": "Bengaluru",
        "distance": 3.2
    },

    {
        "name": "Regional Blood Centre",
        "type": "O-",
        "units": 3,
        "location": "Bengaluru",
        "distance": 5.7
    },

    {
        "name": "Community Blood Centre",
        "type": "A+",
        "units": 4,
        "location": "Bengaluru",
        "distance": 7.4
    },

    {
        "name": "Life Care Blood Bank",
        "type": "B+",
        "units": 2,
        "location": "Bengaluru",
        "distance": 9.1
    },

    {
        "name": "Hope Blood Bank",
        "type": "AB+",
        "units": 6,
        "location": "Bengaluru",
        "distance": 11.2
    },

    {
        "name": "Emergency Blood Centre",
        "type": "O-",
        "units": 5,
        "location": "Mysuru",
        "distance": 145
    }

]


# =========================================================
# BLOOD COMPATIBILITY
# =========================================================

compatible_blood = {

    "A+": ["A+", "A-", "O+", "O-"],

    "A-": ["A-", "O-"],

    "B+": ["B+", "B-", "O+", "O-"],

    "B-": ["B-", "O-"],

    "AB+": [
        "AB+",
        "AB-",
        "A+",
        "A-",
        "B+",
        "B-",
        "O+",
        "O-"
    ],

    "AB-": [
        "AB-",
        "A-",
        "B-",
        "O-"
    ],

    "O+": ["O+", "O-"],

    "O-": ["O-"]

}


# =========================================================
# MATCHING ENGINE
# =========================================================

def find_matches(
    required_blood,
    required_units,
    location,
    urgency
):

    matches = []


    # -----------------------------------------------------
    # CHECK EVERY BLOOD BANK
    # -----------------------------------------------------

    for bank in blood_database:

        bank_type = bank["type"]


        # -------------------------------------------------
        # BLOOD COMPATIBILITY
        # -------------------------------------------------

        if bank_type not in compatible_blood.get(
            required_blood,
            []
        ):
            continue


        # -------------------------------------------------
        # AVAILABILITY
        # -------------------------------------------------

        if bank["units"] <= 0:
            continue


        # -------------------------------------------------
        # LOCATION SCORE
        # -------------------------------------------------

        distance = bank["distance"]


        if distance <= 5:

            location_score = 40

        elif distance <= 10:

            location_score = 30

        elif distance <= 25:

            location_score = 20

        else:

            location_score = 10


        # -------------------------------------------------
        # BLOOD SCORE
        # -------------------------------------------------

        if bank_type == required_blood:

            blood_score = 40

        elif bank_type == "O-":

            blood_score = 35

        else:

            blood_score = 25


        # -------------------------------------------------
        # AVAILABILITY SCORE
        # -------------------------------------------------

        if bank["units"] >= required_units:

            availability_score = 20

        else:

            availability_score = 10


        # -------------------------------------------------
        # TOTAL SCORE
        # -------------------------------------------------

        score = (
            blood_score
            + location_score
            + availability_score
        )


        # -------------------------------------------------
        # URGENCY BONUS
        # -------------------------------------------------

        if urgency == "Critical":

            score += 5

        elif urgency == "Urgent":

            score += 3


        # Maximum theoretical score = 105
        score = min(score, 100)


        # -------------------------------------------------
        # MATCH RESULT
        # -------------------------------------------------

        match = {

            "name": bank["name"],

            "type": bank["type"],

            "units": bank["units"],

            "location": bank["location"],

            "distance": bank["distance"],

            "score": score,

            "exact_match":
                bank_type == required_blood,

            "enough_units":
                bank["units"] >= required_units

        }


        matches.append(match)


    # -----------------------------------------------------
    # SORT BEST MATCH FIRST
    # -----------------------------------------------------

    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )


    return matches


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# EMERGENCY PAGE
# =========================================================

@app.route("/emergency")
def emergency():

    return render_template(
        "emergency.html"
    )


# =========================================================
# MATCHING PAGE
# =========================================================

@app.route("/matches")
def matches():

    return render_template(
        "matches.html"
    )


# =========================================================
# ACTUAL AI MATCHING API
# =========================================================

@app.route(
    "/api/match",
    methods=["POST"]
)
def api_match():

    data = request.get_json()


    blood_group = data.get(
        "bloodGroup"
    )

    units = int(
        data.get(
            "units",
            1
        )
    )

    location = data.get(
        "location",
        ""
    )

    urgency = data.get(
        "urgency",
        "Normal"
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not blood_group:

        return jsonify({

            "success": False,

            "message":
                "Blood group is required."

        })


    # -----------------------------------------------------
    # RUN MATCHING ENGINE
    # -----------------------------------------------------

    matches = find_matches(

        blood_group,

        units,

        location,

        urgency

    )


    return jsonify({

        "success": True,

        "request": {

            "bloodGroup":
                blood_group,

            "units":
                units,

            "location":
                location,

            "urgency":
                urgency

        },

        "matches":
            matches

    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )