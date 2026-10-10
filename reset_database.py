
from app import app
from models import (
    db, User, Business, Customer, Product, Sale,
    Supplier, Purchase, Expense, Employee, Project,
    SupportTicket
)

with app.app_context():
    confirmation = input(
        "This will delete ALL saved application data. "
        "Type RESET to continue: "
    )

    if confirmation != "RESET":
        print("Cancelled. No data was deleted.")
    else:
        try:
            # Delete dependent records before parent records.
            db.session.query(Sale).delete(
                synchronize_session=False
            )
            db.session.query(Purchase).delete(
                synchronize_session=False
            )
            db.session.query(Customer).delete(
                synchronize_session=False
            )
            db.session.query(Product).delete(
                synchronize_session=False
            )
            db.session.query(Supplier).delete(
                synchronize_session=False
            )
            db.session.query(Expense).delete(
                synchronize_session=False
            )
            db.session.query(Employee).delete(
                synchronize_session=False
            )
            db.session.query(Project).delete(
                synchronize_session=False
            )
            db.session.query(SupportTicket).delete(
                synchronize_session=False
            )
            db.session.query(Business).delete(
                synchronize_session=False
            )
            db.session.query(User).delete(
                synchronize_session=False
            )

            db.session.commit()
            print("All saved records have been cleared.")
            print("You can now register a new account.")

        except Exception:
            db.session.rollback()
            print("Reset failed. Changes were rolled back.")
            raise
