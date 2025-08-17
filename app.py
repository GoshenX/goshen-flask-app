import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure app using .env variables
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///site.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ----------------- MODELS -----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    link = db.Column(db.String(500), nullable=False)
    featured = db.Column(db.Boolean, default=False)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- ADMIN CREDENTIALS -----------------
ADMIN_EMAIL = "maildesk.gss@gmail.com"
ADMIN_PASSWORD = "Goshen"  # change to something secure

# ----------------- ROUTES -----------------
@app.route("/")
def home():
    featured_products = Product.query.filter_by(featured=True).all()
    ads = Ad.query.order_by(Ad.date_posted.desc()).all()
    return render_template("index.html", featured=featured_products, ads=ads, year=datetime.now().year)

@app.route("/store")
def store():
    products = Product.query.all()
    return render_template("store.html", products=products, year=datetime.now().year)

@app.route("/about")
def about():
    return render_template("about.html", year=datetime.now().year)

# --------------- ADMIN LOGIN ---------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash("✅ Logged in as admin", "success")
            return redirect(url_for("home"))
        else:
            flash("❌ Invalid credentials", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("✅ Logged out successfully", "success")
    return redirect(url_for("home"))

# ----------------- ADD PRODUCT -----------------
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if not session.get("admin"):
        flash("⚠️ Please log in as admin to add products.", "warning")
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        link = request.form.get("link")
        featured = "featured" in request.form

        if not (name and description and price and link):
            flash("All fields are required!", "danger")
            return redirect(url_for("add_product"))

        new_product = Product(
            name=name,
            description=description,
            price=float(price),
            link=link,
            featured=featured
        )
        db.session.add(new_product)
        db.session.commit()
        flash("✅ Product added successfully!", "success")
        return redirect(url_for("store"))

    return render_template("add_product.html")

# ----------------- DELETE PRODUCT -----------------
@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if not session.get("admin"):
        flash("⚠️ Admin access required", "warning")
        return redirect(url_for("login"))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("✅ Product deleted successfully!", "success")
    return redirect(url_for("store"))

# ----------------- ADD AD -----------------
@app.route("/add_ad", methods=["GET", "POST"])
def add_ad():
    if not session.get("admin"):
        flash("⚠️ Admin access required", "warning")
        return redirect(url_for("login"))
    if request.method == "POST":
        content = request.form.get("content")
        if not content:
            flash("Ad content cannot be empty!", "danger")
            return redirect(url_for("add_ad"))
        new_ad = Ad(content=content)
        db.session.add(new_ad)
        db.session.commit()
        flash("✅ Ad added successfully!", "success")
        return redirect(url_for("home"))
    return render_template("add_ad.html")

# ----------------- DELETE AD -----------------
@app.route("/delete_ad/<int:ad_id>", methods=["POST"])
def delete_ad(ad_id):
    if not session.get("admin"):
        flash("⚠️ Admin access required", "warning")
        return redirect(url_for("login"))
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    flash("✅ Ad deleted successfully!", "success")
    return redirect(url_for("home"))

# ----------------- ERROR HANDLER -----------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# ----------------- RUN APP -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
