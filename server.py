import json

from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for

app = Flask(__name__)
app.secret_key = "something_special"


def load_clubs():
    with open("clubs.json") as c:
        list_of_clubs = json.load(c)["clubs"]
        return list_of_clubs


def load_competitions():
    with open("competitions.json") as comps:
        list_of_competitions = json.load(comps)["competitions"]
        return list_of_competitions


competitions = load_competitions()
clubs = load_clubs()


def check_competitions_date():
    """check the competitions if ongoing or done
    and transform to a boolean value"""

    competitions_ongoing = []
    competitions_done = []
    today = datetime.now().replace(microsecond=0)

    for competition in competitions:
        if competition["date"] > str(today):
            competitions_ongoing.append(competition)
        else:
            competitions_done.append(competition)

    return competitions_ongoing, competitions_done


@app.route("/")
def index():
    """renders the index.html home page"""

    return render_template("index.html")


@app.route("/show-summary", methods=["POST"])
def show_summary():
    """check if the email address is correct
    renders the list of competitions"""

    competitions_ongoing, competitions_done = check_competitions_date()

    matching_clubs = [club for club in clubs if club["email"] == request.form["email"]]

    if matching_clubs:
        club = matching_clubs[0]
        return render_template(
            "welcome.html",
            club=club,
            competitions_ongoing=competitions_ongoing,
            competitions_done=competitions_done,
        )
    else:
        flash("Sorry, that email was not found.")
        return render_template("index.html")


@app.route("/book/<competition>/<club>")
def book(competition, club):
    """renders the chosen competition to book a place"""

    competitions_ongoing, competitions_done = check_competitions_date()

    found_club = [c for c in clubs if c["name"] == club][0]
    found_competition = [c for c in competitions if c["name"] == competition][0]
    if found_club and found_competition:
        return render_template(
            "booking.html", club=found_club, competition=found_competition
        )
    else:
        flash("Something went wrong-please try again")
        return render_template(
            "welcome.html",
            club=club,
            competitions_ongoing=competitions_ongoing,
            competitions_done=competitions_done,
        )


@app.route("/purchase-places", methods=["POST"])
def purchase_places():
    """
    checks if the secretary is trying to book:
        - more than 12 places at once
        - more places than available
        - more places than she can book
        - 0 places
    """

    competitions_ongoing, competitions_done = check_competitions_date()

    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    places_required = int(request.form["places"])

    if places_required <= 0 or places_required > 12:
        if places_required <= 0:
            flash("Please enter a number between 1 and 12.")
        else:
            flash("You can not use more than 12 points!")
        return render_template("booking.html", club=club, competition=competition)

    if places_required > int(competition["number_of_places"]):
        flash("You are about to use more points than you have!")
        return render_template("booking.html", club=club, competition=competition)

    competition["number_of_places"] = (
        int(competition["number_of_places"]) - places_required
    )
    club["points"] = int(club["points"]) - places_required
    flash("Great-booking complete!")
    return render_template(
        "welcome.html",
        club=club,
        competitions_ongoing=competitions_ongoing,
        competitions_done=competitions_done,
    )


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", clubs=clubs)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
