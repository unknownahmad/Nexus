from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String)
    bookings = relationship("Booking", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    resources = relationship("Resource", back_populates="category")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="resources")
    bookings = relationship("Booking", back_populates="resource")
    reviews = relationship("Review", back_populates="resource")
    maintenance = relationship("Maintenance", back_populates="resource")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    user = relationship("User", back_populates="bookings")
    resource = relationship("Resource", back_populates="bookings")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    rating = Column(Integer)
    comment = Column(String)
    resource = relationship("Resource", back_populates="reviews")

class Maintenance(Base):
    __tablename__ = "maintenance"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    status = Column(String) # e.g., "Active", "Broken"
    last_check = Column(DateTime, default=datetime.datetime.utcnow)
    resource = relationship("Resource", back_populates="maintenance")