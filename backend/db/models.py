"""SQLAlchemy ORM 模型定义（5 张表）"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class House(Base):
    __tablename__ = "houses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    district = Column(String(20), nullable=False)
    community = Column(String(100))
    layout = Column(String(20))
    area = Column(Float)
    price = Column(Integer)
    floor = Column(Integer)
    total_floors = Column(Integer)
    orientation = Column(String(10))
    window_type = Column(String(10), default="普通窗")
    building_type = Column(String(10))
    building_year = Column(Integer)
    distance_to_street = Column(Integer)
    has_business_below = Column(Boolean, default=False)
    landlord_phone_hash = Column(String(64))
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)

    reviews = relationship("Review", back_populates="house", cascade="all, delete-orphan")
    price_records = relationship("PriceHistory", back_populates="house", cascade="all, delete-orphan")
    images = relationship("ListingImage", back_populates="house", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    platform = Column(String(20))
    content = Column(Text)
    rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    house = relationship("House", back_populates="reviews")


class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    price = Column(Integer)
    record_date = Column(DateTime, default=datetime.now)
    house = relationship("House", back_populates="price_records")


class Landlord(Base):
    __tablename__ = "landlords"
    phone_hash = Column(String(64), primary_key=True)
    name = Column(String(50))
    type = Column(String(20))
    complaint_count = Column(Integer, default=0)
    risk_tags = Column(String(200))


class ListingImage(Base):
    __tablename__ = "listing_images"
    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    image_path = Column(String(500))
    source_url = Column(Text)
    sort_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    house = relationship("House", back_populates="images")
