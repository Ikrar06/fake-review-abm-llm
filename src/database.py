# Database models and helper functions using SQLAlchemy

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

# Create base class for declarative models
Base = declarative_base()


class Product(Base):
    """
    Product model representing headphones in the marketplace
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer)  # in Rupiah
    base_quality = Column(String)  # 'High', 'Medium', 'Low'

    # Product attributes (0-10 scale)
    sound_quality = Column(Float)
    build_quality = Column(Float)
    battery_life = Column(Float)
    comfort = Column(Float)

    # Dynamic state (updated during simulation)
    current_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    # Relationships
    reviews = relationship("Review", back_populates="product")
    transactions = relationship("Transaction", back_populates="product")


class Review(Base):
    """
    Review model representing user reviews (both genuine and fake)
    """
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))

    # Agent information
    agent_type = Column(String)  # 'Genuine' or 'Fake'
    agent_personality = Column(String, nullable=True)  # For genuine: 'Critical', 'Balanced', 'Lenient'

    # Review content
    rating = Column(Integer)  # 1-5 stars
    text = Column(Text)

    # Metadata
    is_fake = Column(Boolean)
    iteration = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="reviews")


class Transaction(Base):
    """
    Transaction model representing purchase decisions by shoppers
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))

    # Shopper information
    buyer_persona = Column(String)  # 'Impulsive', 'Careful', 'Skeptical'

    # Decision
    decision = Column(String)  # 'BUY' or 'NO_BUY'
    reasoning = Column(Text)  # LLM-generated explanation

    # Context for analysis
    reviews_read = Column(Integer)
    fake_in_sample = Column(Integer)  # Ground truth: how many fake reviews in sample

    # Metadata
    iteration = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="transactions")


def init_database(db_path):
    """
    Create all tables in the database

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLAlchemy engine object
    """
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """
    Get a SQLAlchemy session for database operations

    Args:
        engine: SQLAlchemy engine object

    Returns:
        SQLAlchemy session object
    """
    Session = sessionmaker(bind=engine)
    return Session()
