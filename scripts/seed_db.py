import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, Base, SessionLocal
from app.models.schema import User, Product, Order, Payment

def seed_database():
    print("Resetting and creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        # 1. Create Users
        users = [
            User(name="Arun Kumar", email="arun@example.com", role="customer", created_at=now - timedelta(days=5)),
            User(name="Bala Ram", email="bala@example.com", role="customer", created_at=now - timedelta(days=2)),
            User(name="Ravi Shankar", email="ravi@example.com", role="admin", created_at=now - timedelta(days=40)),
            User(name="Priya Patel", email="priya@example.com", role="customer", created_at=now - timedelta(days=15)),
            User(name="Sneha Rao", email="sneha@example.com", role="manager", created_at=now - timedelta(days=60)),
            User(name="Vikram Singh", email="vikram@example.com", role="customer", created_at=now - timedelta(days=1)),
            User(name="Ananya Sharma", email="ananya@example.com", role="customer", created_at=now - timedelta(days=90)),
        ]
        db.add_all(users)
        db.commit()

        for u in users:
            db.refresh(u)

        # 2. Create Products
        products = [
            Product(title="UltraBook Pro 15", category="Electronics", price=1299.99, stock=15, created_at=now - timedelta(days=100)),
            Product(title="Wireless Noise-Canceling Headphones", category="Electronics", price=249.50, stock=45, created_at=now - timedelta(days=80)),
            Product(title="Ergonomic Office Chair", category="Furniture", price=349.00, stock=8, created_at=now - timedelta(days=60)),
            Product(title="Mechanical Gaming Keyboard", category="Electronics", price=119.99, stock=0, created_at=now - timedelta(days=50)),
            Product(title="Organic Coffee Beans (1kg)", category="Groceries", price=29.99, stock=120, created_at=now - timedelta(days=30)),
            Product(title="Stainless Steel Water Bottle", category="Accessories", price=19.99, stock=3, created_at=now - timedelta(days=20)),
        ]
        db.add_all(products)
        db.commit()

        for p in products:
            db.refresh(p)

        # 3. Create Orders
        orders = [
            Order(user_id=users[0].id, status="completed", total_amount=1549.49, created_at=now - timedelta(days=4)),
            Order(user_id=users[1].id, status="completed", total_amount=249.50, created_at=now - timedelta(days=1)),
            Order(user_id=users[1].id, status="pending", total_amount=119.99, created_at=now - timedelta(hours=5)),
            Order(user_id=users[3].id, status="completed", total_amount=378.99, created_at=now - timedelta(days=10)),
            Order(user_id=users[3].id, status="cancelled", total_amount=1299.99, created_at=now - timedelta(days=8)),
            Order(user_id=users[5].id, status="shipped", total_amount=29.99, created_at=now - timedelta(hours=12)),
            Order(user_id=users[6].id, status="completed", total_amount=698.00, created_at=now - timedelta(days=45)),
        ]
        db.add_all(orders)
        db.commit()

        for o in orders:
            db.refresh(o)

        # 4. Create Payments
        payments = [
            Payment(order_id=orders[0].id, payment_method="credit_card", status="successful", amount=1549.49, created_at=orders[0].created_at),
            Payment(order_id=orders[1].id, payment_method="upi", status="successful", amount=249.50, created_at=orders[1].created_at),
            Payment(order_id=orders[2].id, payment_method="paypal", status="pending", amount=119.99, created_at=orders[2].created_at),
            Payment(order_id=orders[3].id, payment_method="credit_card", status="successful", amount=378.99, created_at=orders[3].created_at),
            Payment(order_id=orders[4].id, payment_method="bank_transfer", status="failed", amount=1299.99, created_at=orders[4].created_at),
            Payment(order_id=orders[5].id, payment_method="upi", status="successful", amount=29.99, created_at=orders[5].created_at),
            Payment(order_id=orders[6].id, payment_method="credit_card", status="successful", amount=698.00, created_at=orders[6].created_at),
        ]
        db.add_all(payments)
        db.commit()

        print("Successfully seeded sample database!")
        print(f"Stats: {len(users)} users, {len(products)} products, {len(orders)} orders, {len(payments)} payments.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
