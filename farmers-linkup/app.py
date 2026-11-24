"""Farmer's LinkUp - simplified prototype (Flask + Jinja + Bootstrap).

No database: all data lives in memory and resets when the server restarts.
Any email/password is accepted at login - this is a prototype only.
"""
from copy import deepcopy
from functools import wraps

from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for, abort)

app = Flask(__name__)
app.secret_key = "9f2c1e...your-long-random-string..."

SEED = {
    "farmer": {
        "name": "Emeka Okonkwo",
        "email": "emeka.farms@gmail.com",
        "phone": "+234 803 123 4567",
        "location": "Omor Farms Cluster, Ayamelum LGA, Anambra",
    },
    "listings": [
        {"id": 1, "crop": "Plum Tomatoes", "grade": "A", "qty": 500, "price": 250,
         "location": "Awka South LGA, Anambra", "status": "active", "hours_left": 14},
        {"id": 2, "crop": "Yellow Garri", "grade": "A", "qty": 800, "price": 420,
         "location": "Onitsha North LGA, Anambra", "status": "active", "hours_left": 48},
        {"id": 3, "crop": "Cassava Tubers", "grade": "B", "qty": 1200, "price": 375,
         "location": "Enugu North LGA, Enugu", "status": "sold", "hours_left": 0},
    ],
    "offers": [
        {"id": 1, "buyer": "GreenMart Foods", "place": "Onitsha Commercial Hub",
         "trust": 98, "crop": "Plum Tomatoes", "qty": 300, "batch_qty": 500,
         "price": 250, "pickup": "Today, 4:00 PM", "urgent": True, "status": "pending",
         "depot": "Amawbia Farmgate Depot, Awka South LGA"},
        {"id": 2, "buyer": "Owerri Fresh Caterers", "place": "Imo State",
         "trust": 94, "crop": "Yellow Garri", "qty": 500, "batch_qty": 800,
         "price": 410, "pickup": "Tomorrow, 10:00 AM", "urgent": False, "status": "pending",
         "depot": "Onitsha North Depot, Anambra"},
        {"id": 3, "buyer": "Ekeukwu Wholesalers", "place": "Aba Market Hub",
         "trust": 91, "crop": "Plum Tomatoes", "qty": 200, "batch_qty": 500,
         "price": 255, "pickup": "Tomorrow, 8:00 AM", "urgent": False, "status": "pending",
         "depot": "Amawbia Farmgate Depot, Awka South LGA"},
    ],
    "orders": [
        {"id": "ORD-2026-885", "buyer": "Onitsha Fresh Direct", "crop": "Yellow Garri",
         "qty": 500, "price": 240, "status": "awaiting", "date": "Today"},
        {"id": "ORD-2026-794", "buyer": "Enugu Central Mart", "crop": "Sweet Peppers",
         "qty": 400, "price": 275, "status": "paid", "date": "May 12"},
        {"id": "ORD-2026-742", "buyer": "Owerri Bulk Buyers", "crop": "Plantains",
         "qty": 250, "price": 340, "status": "paid", "date": "May 8"},
    ],
}
STATE = deepcopy(SEED)

CROPS = ["Plum Tomatoes", "Scotch Bonnet Peppers", "Yellow Garri",
         "Cassava Tubers", "Plantain", "Ugu (Fluted Pumpkin)"]
LOCATIONS = ["Awka South LGA, Anambra", "Onitsha North LGA, Anambra",
             "Owerri Municipal LGA, Imo", "Aba South LGA, Abia",
             "Enugu North LGA, Enugu"]


@app.template_filter("naira")
def naira(value):
    return "₦{:,}".format(int(value))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    pending = sum(1 for o in STATE["offers"] if o["status"] == "pending")
    return {"farmer": STATE["farmer"], "pending_count": pending}


def order_total(o):
    return o["qty"] * o["price"]


# ---------- Public pages ----------
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        if not (name and email and pw):
            flash("Please fill in every field.", "danger")
        elif pw != request.form.get("confirm", ""):
            flash("Passwords do not match.", "danger")
        else:
            STATE["farmer"]["name"] = name
            STATE["farmer"]["email"] = email
            session["user"] = email
            flash("Welcome to Farmer's LinkUp!", "success")
            return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("email") and request.form.get("password"):
            session["user"] = request.form["email"]
            return redirect(url_for("dashboard"))
        flash("Enter your email and password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


# ---------- App pages ----------
@app.route("/dashboard")
@login_required
def dashboard():
    active = [l for l in STATE["listings"] if l["status"] == "active"]
    pending = [o for o in STATE["offers"] if o["status"] == "pending"]
    paid = [o for o in STATE["orders"] if o["status"] == "paid"]
    earned = sum(order_total(o) for o in paid)
    recent = STATE["orders"][:3]
    return render_template("dashboard.html", active=active, pending=pending,
                           earned=earned, trades=len(paid), recent=recent,
                           order_total=order_total)


@app.route("/produce")
@login_required
def produce():
    tab = request.args.get("tab", "active")
    items = [l for l in STATE["listings"] if l["status"] == tab]
    return render_template("produce.html", tab=tab, items=items,
                           n_active=sum(l["status"] == "active" for l in STATE["listings"]),
                           n_sold=sum(l["status"] == "sold" for l in STATE["listings"]))


@app.route("/produce/new", methods=["GET", "POST"])
@login_required
def produce_new():
    if request.method == "POST":
        try:
            qty = int(request.form["qty"])
            price = int(request.form["price"])
            assert qty > 0 and price > 0
        except (KeyError, ValueError, AssertionError):
            flash("Enter a valid quantity and price.", "danger")
            return render_template("produce_new.html", crops=CROPS, locations=LOCATIONS)
        STATE["listings"].insert(0, {
            "id": max(l["id"] for l in STATE["listings"]) + 1,
            "crop": request.form["crop"], "grade": request.form.get("grade", "A"),
            "qty": qty, "price": price, "location": request.form["location"],
            "status": "active", "hours_left": int(request.form.get("hours", 48)),
        })
        flash("Produce listed. Buyers can now see it.", "success")
        return redirect(url_for("produce"))
    return render_template("produce_new.html", crops=CROPS, locations=LOCATIONS)


@app.route("/requests")
@login_required
def requests_page():
    pending = [o for o in STATE["offers"] if o["status"] == "pending"]
    return render_template("requests.html", offers=pending)


def get_offer(oid):
    for o in STATE["offers"]:
        if o["id"] == oid:
            return o
    abort(404)


@app.route("/requests/<int:oid>/decline", methods=["POST"])
@login_required
def decline(oid):
    get_offer(oid)["status"] = "declined"
    flash("Offer declined.", "secondary")
    return redirect(url_for("requests_page"))


@app.route("/requests/<int:oid>/review")
@login_required
def review(oid):
    offer = get_offer(oid)
    if offer["status"] != "pending":
        return redirect(url_for("requests_page"))
    return render_template("order.html", o=offer, total=offer["qty"] * offer["price"])


@app.route("/requests/<int:oid>/confirm", methods=["POST"])
@login_required
def confirm(oid):
    offer = get_offer(oid)
    if offer["status"] == "pending":
        offer["status"] = "accepted"
        STATE["orders"].insert(0, {
            "id": "ORD-2026-%03d" % (900 + oid), "buyer": offer["buyer"],
            "crop": offer["crop"], "qty": offer["qty"], "price": offer["price"],
            "status": "awaiting", "date": "Today"})
        flash("Order confirmed. Funds are held in escrow.", "success")
    return redirect(url_for("sales"))


@app.route("/sales")
@login_required
def sales():
    awaiting = [o for o in STATE["orders"] if o["status"] == "awaiting"]
    paid = [o for o in STATE["orders"] if o["status"] == "paid"]
    return render_template("sales.html", awaiting=awaiting, paid=paid,
                           earned=sum(order_total(o) for o in paid),
                           order_total=order_total)


@app.route("/sales/<oid>/signoff", methods=["POST"])
@login_required
def signoff(oid):
    for o in STATE["orders"]:
        if o["id"] == oid and o["status"] == "awaiting":
            try:
                weighed = int(request.form.get("weighed", o["qty"]))
            except ValueError:
                weighed = o["qty"]
            o["qty"] = max(weighed, 1)
            o["status"] = "paid"
            flash("Signed off. %s released to your bank." % naira(order_total(o)), "success")
    return redirect(url_for("sales"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


if __name__ == "__main__":
    app.run(debug=True)
