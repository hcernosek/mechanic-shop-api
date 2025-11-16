
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from datetime import date

# Creating our Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)


# ======================================================================
# ASSOCIATION TABLE
# ======================================================================

service_mechanic = db.Table(
    "service_mechanic",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"))
)

# ======================================================================
# ASSOCIATION MODEL
# ======================================================================

class ServiceInventory(Base):
    __tablename__ = "service_inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=False)
    inventory_id: Mapped[int] = mapped_column(db.ForeignKey("inventory.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    inventory: Mapped["Inventory"] = db.relationship(back_populates="service_inventory")
    service_ticket: Mapped["ServiceTicket"] = db.relationship(back_populates="service_inventory")

# ======================================================================
# MODELS
# ======================================================================

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates="customer")

class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"), nullable=False)

    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates="service_tickets")
    service_inventory: Mapped[List["ServiceInventory"]] = db.relationship(back_populates="service_ticket")

class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanic, back_populates="mechanics")  

class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_inventory: Mapped[List["ServiceInventory"]] = db.relationship(back_populates="inventory")


