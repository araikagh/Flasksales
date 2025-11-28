from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Numeric, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    CategoryName: Mapped[str] = mapped_column(String(100), nullable=False)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "CategoryName": self.CategoryName}

class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ProductName: Mapped[str] = mapped_column(String(45), nullable=False)
    Manufacturer: Mapped[str] = mapped_column(String(45), nullable=False)
    ProductCount: Mapped[int] = mapped_column(Integer, nullable=True)
    Price: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    CategoryId: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)

    category = relationship("Category", back_populates="products")

    def to_dict(self):
        return {
            "id": self.id,
            "ProductName": self.ProductName,
            "Manufacturer": self.Manufacturer,
            "ProductCount": int(self.ProductCount or 0),
            "Price": float(self.Price),
            "CategoryId": self.CategoryId,
            "CategoryName": self.category.CategoryName if self.category else None
        }

class Customer(db.Model):
    __tablename__ = "customers"
    idCustomers: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    FirstName: Mapped[str] = mapped_column(String(30), nullable=False)

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

    def to_dict(self):
        return {"idCustomers": self.idCustomers, "FirstName": self.FirstName}

class Order(db.Model):
    __tablename__ = "orders"
    idorders: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ProductId: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    CustomerId: Mapped[int] = mapped_column(Integer, ForeignKey("customers.idCustomers"), nullable=True)
    CreatedAt = mapped_column(DateTime, server_default=func.now())
    ProductCount: Mapped[int] = mapped_column(Integer, default=1)
    Price: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    # totalpay is VIRTUAL in DB (ProductCount * Price). We'll compute for API responses as well.

    product = relationship("Product")
    customer = relationship("Customer", back_populates="orders")

    def to_dict(self):
        total = None
        try:
            total = float(self.ProductCount) * float(self.Price)
        except:
            total = None
        return {
            "idorders": self.idorders,
            "ProductId": self.ProductId,
            "ProductName": self.product.ProductName if self.product else None,
            "CustomerId": self.CustomerId,
            "CustomerName": self.customer.FirstName if self.customer else None,
            "CreatedAt": self.CreatedAt.isoformat() if self.CreatedAt else None,
            "ProductCount": int(self.ProductCount or 0),
            "Price": float(self.Price),
            "totalpay": total
        }
