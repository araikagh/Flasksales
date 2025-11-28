from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
import os
from models import db, Product, Customer, Order, Category

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("SECRET_KEY", "devsecret")

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "sales")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset={DB_CHARSET}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # register blueprints
    from api.products import bp as products_bp
    from api.customers import bp as customers_bp
    from api.categories import bp as categories_bp
    from api.orders import bp as orders_bp

    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(orders_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    # unified login page (chooses role)
    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method == "POST":
            role = request.form.get("role")
            if role == "customer":
                return redirect(url_for("login_customer"))
            if role == "admin":
                return redirect(url_for("login_admin"))
        return render_template("login.html")

    @app.route("/login/customer", methods=["GET", "POST"])
    def login_customer():
        if request.method == "POST":
            name = request.form.get("customer_name", "").strip()
            if not name:
                return render_template("login.html", error="Введите имя")
            customer = Customer.query.filter_by(FirstName=name).first()
            if not customer:
                customer = Customer(FirstName=name)
                db.session.add(customer)
                db.session.commit()
            session["customer_id"] = customer.idCustomers
            session["customer_name"] = customer.FirstName
            return redirect(url_for("catalog"))
        return render_template("login.html", role="customer")

    @app.route("/login/admin", methods=["GET", "POST"])
    def login_admin():
        if request.method == "POST":
            pwd = request.form.get("admin_password", "")
            env_pass = os.getenv("DB_PASS")
            if pwd == env_pass or pwd == "qwerty.789456":
                session["is_admin"] = True
                return redirect(url_for("admin"))
            return render_template("login.html", role="admin", error="Неверный пароль")
        return render_template("login.html", role="admin")

    @app.route("/catalog")
    def catalog():
        if not session.get("customer_id"):
            return redirect(url_for("login_customer"))
        return render_template("catalog.html", customer_name=session.get("customer_name"))

    @app.route("/admin")
    def admin():
        if not session.get("is_admin"):
            return redirect(url_for("login_admin"))
        return render_template("admin.html")

    @app.route("/api/stats")
    def stats():
        total_orders = Order.query.count()
        total_customers = Customer.query.count()
        total_products = Product.query.count()
        total_sales = db.session.query(db.func.sum(Order.Price * Order.ProductCount)).scalar() or 0
        return jsonify({
            "ok": True,
            "total_orders": total_orders,
            "total_customers": total_customers,
            "total_products": total_products,
            "total_sales": float(total_sales)
        })

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
