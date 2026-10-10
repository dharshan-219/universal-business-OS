from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import (
    db, User, Business, Customer, Product, Sale,
    Supplier, Purchase, Expense, Employee, Project,
    SupportTicket
)

from datetime import datetime

app = Flask(__name__)


import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "local-development-only-change-me"
)

database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///business_os.db"
)

# Render may provide postgres:// or postgresql://.
# Use the installed Psycopg 3 driver.
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


# HOME
@app.route("/")
def home():
    return render_template("home.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.")

        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/business/<int:business_id>")
@login_required
def business_workspace(business_id):

    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    return render_template(
        "workspace.html",
        business=business
    )
# DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():

    businesses = Business.query.filter_by(
        owner_id=current_user.id
    ).all()

    return render_template(
        "dashboard.html",
        businesses=businesses
    )


# CREATE BUSINESS
@app.route("/create-business", methods=["GET", "POST"])
@login_required
def create_business():

    if request.method == "POST":

        name = request.form["name"]
        business_type = request.form["business_type"]
        country = request.form["country"]
        currency = request.form["currency"]

        business = Business(
            name=name,
            business_type=business_type,
            country=country,
            currency=currency,
            owner_id=current_user.id
        )

        db.session.add(business)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("create_business.html")


# LOGOUT
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("home"))

@app.route("/business/<int:business_id>/customers")
@login_required
def customers(business_id):

    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    customer_list = Customer.query.filter_by(
        business_id=business.id
    ).all()

    return render_template(
        "customers.html",
        business=business,
        customers=customer_list
    )

@app.route(
    "/business/<int:business_id>/customers/add",
    methods=["POST"]
)
@login_required
def add_customer(business_id):

    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    customer = Customer(
        name=request.form["name"],
        phone=request.form.get("phone"),
        email=request.form.get("email"),
        address=request.form.get("address"),
        notes=request.form.get("notes"),
        business_id=business.id
    )

    db.session.add(customer)
    db.session.commit()

    return redirect(
        url_for(
            "customers",
            business_id=business.id
        )
    )

@app.route("/business/<int:business_id>/products")
@login_required
def products(business_id):

    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    product_list = Product.query.filter_by(
        business_id=business.id
    ).all()

    return render_template(
        "products.html",
        business=business,
        products=product_list
    )


@app.route("/business/<int:business_id>/inventory")
@login_required
def inventory(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    products = Product.query.filter_by(
        business_id=business.id
    ).order_by(Product.name).all()

    low_stock_count = sum(
        1 for product in products
        if 0 < product.stock_quantity <= 5
    )

    out_of_stock_count = sum(
        1 for product in products
        if product.stock_quantity <= 0
    )

    return render_template(
        "inventory.html",
        business=business,
        products=products,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count
    )
@app.route(
    "/business/<int:business_id>/products/add",
    methods=["POST"]
)
@login_required
def add_product(business_id):

    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    product = Product(
        name=request.form["name"],
        sku=request.form.get("sku"),
        category=request.form.get("category"),
        selling_price=float(
            request.form.get("selling_price") or 0
        ),
        purchase_price=float(
            request.form.get("purchase_price") or 0
        ),
        stock_quantity=float(
            request.form.get("stock_quantity") or 0
        ),
        unit=request.form.get("unit") or "piece",
        business_id=business.id
    )

    db.session.add(product)
    db.session.commit()

    return redirect(
        url_for(
            "products",
            business_id=business.id
        )
    )

@app.route("/business/<int:business_id>/sales")
@login_required
def sales(business_id):

    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    customer_list = Customer.query.filter_by(
        business_id=business.id
    ).all()

    product_list = Product.query.filter_by(
        business_id=business.id
    ).all()

    sale_list = Sale.query.filter_by(
        business_id=business.id
    ).order_by(
        Sale.id.desc()
    ).all()

    return render_template(
        "sales.html",
        business=business,
        customers=customer_list,
        products=product_list,
        sales=sale_list
    )


# ADD SALE
@app.route("/business/<int:business_id>/sales/add", methods=["POST"])
@login_required
def add_sale(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    customer = Customer.query.filter_by(
        id=request.form["customer_id"],
        business_id=business.id
    ).first_or_404()

    product = Product.query.filter_by(
        id=request.form["product_id"],
        business_id=business.id
    ).first_or_404()

    try:
        quantity = float(request.form["quantity"])
    except (ValueError, TypeError):
        flash("Please enter a valid quantity.")
        return redirect(url_for("sales", business_id=business.id))

    if quantity <= 0:
        flash("Quantity must be greater than zero.")
        return redirect(url_for("sales", business_id=business.id))

    if quantity > product.stock_quantity:
        flash("Not enough stock available.")
        return redirect(url_for("sales", business_id=business.id))

    unit_price = product.selling_price
    total_amount = quantity * unit_price

    sale = Sale(
        customer_id=customer.id,
        product_id=product.id,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        business_id=business.id,
        created_at=datetime.utcnow()
    )

    try:
        product.stock_quantity -= quantity
        db.session.add(sale)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    flash("Sale created successfully.")

    return redirect(url_for("sales", business_id=business.id))



# PURCHASES PAGE
@app.route("/business/<int:business_id>/purchases")
@login_required
def purchases(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    suppliers = Supplier.query.filter_by(
        business_id=business.id
    ).order_by(Supplier.name).all()

    products = Product.query.filter_by(
        business_id=business.id
    ).order_by(Product.name).all()

    purchase_list = Purchase.query.filter_by(
        business_id=business.id
    ).order_by(Purchase.id.desc()).all()

    return render_template(
        "purchases.html",
        business=business,
        suppliers=suppliers,
        products=products,
        purchases=purchase_list
    )


# ADD SUPPLIER
@app.route(
    "/business/<int:business_id>/suppliers/add",
    methods=["POST"]
)
@login_required
def add_supplier(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    name = request.form.get("name", "").strip()

    if not name:
        flash("Supplier name is required.")
        return redirect(url_for(
            "purchases", business_id=business.id
        ))

    supplier = Supplier(
        name=name,
        phone=request.form.get("phone", "").strip(),
        email=request.form.get("email", "").strip(),
        address=request.form.get("address", "").strip(),
        business_id=business.id
    )

    db.session.add(supplier)
    db.session.commit()

    flash("Supplier added successfully.")
    return redirect(url_for(
        "purchases", business_id=business.id
    ))


# RECORD PURCHASE AND UPDATE STOCK
@app.route(
    "/business/<int:business_id>/purchases/add",
    methods=["POST"]
)
@login_required
def add_purchase(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    try:
        supplier_id = int(request.form["supplier_id"])
        product_id = int(request.form["product_id"])
        quantity = float(request.form["quantity"])
        unit_cost = float(request.form["unit_cost"])
    except (KeyError, ValueError, TypeError):
        flash("Please enter valid purchase details.")
        return redirect(url_for(
            "purchases", business_id=business.id
        ))

    if quantity <= 0 or unit_cost < 0:
        flash("Quantity must be positive and cost cannot be negative.")
        return redirect(url_for(
            "purchases", business_id=business.id
        ))

    supplier = Supplier.query.filter_by(
        id=supplier_id,
        business_id=business.id
    ).first()

    product = Product.query.filter_by(
        id=product_id,
        business_id=business.id
    ).first()

    if supplier is None or product is None:
        flash("Invalid supplier or product.")
        return redirect(url_for(
            "purchases", business_id=business.id
        ))

    purchase = Purchase(
        supplier_id=supplier.id,
        product_id=product.id,
        quantity=quantity,
        unit_cost=unit_cost,
        total_amount=quantity * unit_cost,
        business_id=business.id
    )

    # Increase stock exactly once for this purchase.
    product.stock_quantity += quantity

    try:
        db.session.add(purchase)
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to save purchase")
        flash("Purchase could not be saved. Please try again.")
        return redirect(url_for(
            "purchases", business_id=business.id
        ))

    flash("Purchase recorded and stock updated successfully.")
    return redirect(url_for(
        "purchases", business_id=business.id
    ))


from datetime import datetime, date

@app.route("/business/<int:business_id>/expenses")
@login_required
def expenses(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    expense_list = Expense.query.filter_by(
        business_id=business.id
    ).order_by(Expense.id.desc()).all()

    total_expenses = sum(
        expense.amount for expense in expense_list
    )

    return render_template(
        "expenses.html",
        business=business,
        expenses=expense_list,
        total_expenses=total_expenses
    )


@app.route(
    "/business/<int:business_id>/expenses/add",
    methods=["POST"]
)
@login_required
def add_expense(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()

    try:
        amount = float(request.form.get("amount", "0"))
        expense_date = date.fromisoformat(
            request.form.get("expense_date", "")
        )
    except (ValueError, TypeError):
        flash("Enter a valid amount and expense date.")
        return redirect(
            url_for("expenses", business_id=business.id)
        )

    if not title or not category or amount <= 0:
        flash("Enter a title, category, and amount greater than zero.")
        return redirect(
            url_for("expenses", business_id=business.id)
        )

    expense = Expense(
        title=title,
        category=category,
        amount=amount,
        description=description or None,
        expense_date=expense_date,
        business_id=business.id
    )

    db.session.add(expense)
    db.session.commit()

    flash("Expense recorded successfully.")
    return redirect(
        url_for("expenses", business_id=business.id)
    )

@app.route("/business/<int:business_id>/finance")
@login_required
def finance(business_id):
    from datetime import datetime
    from collections import defaultdict

    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    sale_list = Sale.query.filter_by(
        business_id=business.id
    ).all()

    purchase_list = Purchase.query.filter_by(
        business_id=business.id
    ).all()

    expense_list = Expense.query.filter_by(
        business_id=business.id
    ).all()

    # Total revenue
    total_revenue = sum(
        sale.total_amount for sale in sale_list
    )

    # Total purchases
    total_purchases = sum(
        purchase.total_amount for purchase in purchase_list
    )

    # Total expenses
    total_expenses = sum(
        expense.amount for expense in expense_list
    )

    # Estimated gross profit
    estimated_gross_profit = sum(
        (
            sale.unit_price - sale.product.purchase_price
        ) * sale.quantity
        for sale in sale_list
    )

    # Estimated net profit
    estimated_net_profit = (
        estimated_gross_profit - total_expenses
    )

    # Monthly sales chart data
    monthly_sales = defaultdict(float)

    for sale in sale_list:
        if sale.created_at:
            month_key = sale.created_at.strftime("%Y-%m")
            monthly_sales[month_key] += sale.total_amount

    # Show the latest 6 months, including months with zero sales
    current_month = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    chart_labels = []
    chart_values = []

    for offset in range(5, -1, -1):
        month_date = current_month.replace(day=1)

        # Move backwards by the required number of months
        month_number = month_date.month - offset
        year = month_date.year

        while month_number <= 0:
            month_number += 12
            year -= 1

        month_date = month_date.replace(
            year=year,
            month=month_number
        )

        month_key = month_date.strftime("%Y-%m")

        chart_labels.append(month_date.strftime("%b %Y"))
        chart_values.append(round(monthly_sales.get(month_key, 0), 2))

    return render_template(
        "finance.html",
        business=business,
        total_revenue=total_revenue,
        total_purchases=total_purchases,
        total_expenses=total_expenses,
        estimated_gross_profit=estimated_gross_profit,
        estimated_net_profit=estimated_net_profit,
        chart_labels=chart_labels,
        chart_values=chart_values
    )


# EMPLOYEES PAGE
@app.route("/business/<int:business_id>/employees")
@login_required
def employees(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    employee_list = Employee.query.filter_by(
        business_id=business.id
    ).order_by(Employee.name).all()

    return render_template(
        "employees.html",
        business=business,
        employees=employee_list
    )


# ADD EMPLOYEE
@app.route(
    "/business/<int:business_id>/employees/add",
    methods=["POST"]
)
@login_required
def add_employee(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    name = request.form.get("name", "").strip()
    job_title = request.form.get("job_title", "").strip()

    if not name or not job_title:
        flash("Employee name and job title are required.")
        return redirect(
            url_for("employees", business_id=business.id)
        )

    try:
        salary = float(request.form.get("salary") or 0)
        if salary < 0:
            raise ValueError
    except (ValueError, TypeError):
        flash("Please enter a valid salary.")
        return redirect(
            url_for("employees", business_id=business.id)
        )

    employee = Employee(
        name=name,
        job_title=job_title,
        email=request.form.get("email", "").strip() or None,
        phone=request.form.get("phone", "").strip() or None,
        salary=salary,
        business_id=business.id
    )

    db.session.add(employee)
    db.session.commit()

    flash("Employee added successfully.")
    return redirect(
        url_for("employees", business_id=business.id)
    )


# PROJECTS PAGE
@app.route("/business/<int:business_id>/projects")
@login_required
def projects(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    project_list = Project.query.filter_by(
        business_id=business.id
    ).order_by(Project.id.desc()).all()

    return render_template(
        "projects.html",
        business=business,
        projects=project_list
    )


# ADD PROJECT
@app.route(
    "/business/<int:business_id>/projects/add",
    methods=["POST"]
)
@login_required
def add_project(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "Planned")

    allowed_statuses = {
        "Planned", "In Progress", "Completed", "On Hold"
    }

    if not name:
        flash("Project name is required.")
        return redirect(
            url_for("projects", business_id=business.id)
        )

    if status not in allowed_statuses:
        flash("Please select a valid project status.")
        return redirect(
            url_for("projects", business_id=business.id)
        )

    try:
        budget = float(request.form.get("budget") or 0)

        if budget < 0:
            raise ValueError

        deadline_text = request.form.get("deadline", "").strip()
        deadline = (
            date.fromisoformat(deadline_text)
            if deadline_text else None
        )
    except (ValueError, TypeError):
        flash("Enter a valid budget and deadline.")
        return redirect(
            url_for("projects", business_id=business.id)
        )

    project = Project(
        name=name,
        description=description or None,
        budget=budget,
        deadline=deadline,
        status=status,
        business_id=business.id
    )

    db.session.add(project)
    db.session.commit()

    flash("Project created successfully.")
    return redirect(
        url_for("projects", business_id=business.id)
    )

# SUPPORT PAGE
@app.route("/business/<int:business_id>/support")
@login_required
def support(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    tickets = SupportTicket.query.filter_by(
        business_id=business.id
    ).order_by(
        SupportTicket.id.desc()
    ).all()

    return render_template(
        "support.html",
        business=business,
        tickets=tickets
    )


# CREATE SUPPORT TICKET
@app.route(
    "/business/<int:business_id>/support/add",
    methods=["POST"]
)
@login_required
def add_support_ticket(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    subject = request.form.get("subject", "").strip()
    customer_name = request.form.get("customer_name", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")

    allowed_priorities = {"Low", "Medium", "High"}

    if not subject or not customer_name or not description:
        flash("Please fill in all required support ticket fields.")
        return redirect(
            url_for("support", business_id=business.id)
        )

    if priority not in allowed_priorities:
        flash("Please select a valid priority.")
        return redirect(
            url_for("support", business_id=business.id)
        )

    ticket = SupportTicket(
        subject=subject,
        customer_name=customer_name,
        description=description,
        priority=priority,
        status="Open",
        business_id=business.id
    )

    db.session.add(ticket)
    db.session.commit()

    flash("Support ticket created successfully.")
    return redirect(
        url_for("support", business_id=business.id)
    )

# REPORTS PAGE
@app.route("/business/<int:business_id>/reports")
@login_required
def reports(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    total_customers = Customer.query.filter_by(
        business_id=business.id
    ).count()

    total_employees = Employee.query.filter_by(
        business_id=business.id
    ).count()

    total_projects = Project.query.filter_by(
        business_id=business.id
    ).count()

    total_tickets = SupportTicket.query.filter_by(
        business_id=business.id
    ).count()

    sales_list = Sale.query.filter_by(
        business_id=business.id
    ).all()

    purchase_list = Purchase.query.filter_by(
        business_id=business.id
    ).all()

    expense_list = Expense.query.filter_by(
        business_id=business.id
    ).all()

    total_sales = sum(
        float(item.total_amount or 0)
        for item in sales_list
    )

    total_purchases = sum(
        float(item.total_amount or 0)
        for item in purchase_list
    )

    total_expenses = sum(
        float(item.amount or 0)
        for item in expense_list
    )

    return render_template(
        "reports.html",
        business=business,
        total_customers=total_customers,
        total_employees=total_employees,
        total_projects=total_projects,
        total_tickets=total_tickets,
        total_sales=total_sales,
        total_purchases=total_purchases,
        total_expenses=total_expenses
    )

# BUSINESS SETTINGS PAGE
@app.route(
    "/business/<int:business_id>/settings",
    methods=["GET", "POST"]
)
@login_required
def business_settings(business_id):
    business = Business.query.filter_by(
        id=business_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        business_type = request.form.get(
            "business_type", ""
        ).strip()
        country = request.form.get("country", "").strip()
        currency = request.form.get("currency", "").strip()

        if not all([name, business_type, country, currency]):
            flash("Please fill in all settings fields.")
            return redirect(
                url_for(
                    "business_settings",
                    business_id=business.id
                )
            )

        if (
            len(name) > 150
            or len(business_type) > 100
            or len(country) > 100
            or len(currency) > 20
        ):
            flash("One or more fields exceed the allowed length.")
            return redirect(
                url_for(
                    "business_settings",
                    business_id=business.id
                )
            )

        business.name = name
        business.business_type = business_type
        business.country = country
        business.currency = currency

        db.session.commit()

        flash("Business settings updated successfully.")
        return redirect(
            url_for(
                "business_settings",
                business_id=business.id
            )
        )

    return render_template(
        "settings.html",
        business=business
    )

if __name__ == "__main__":
    app.run(debug=True)