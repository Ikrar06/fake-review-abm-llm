# Product management class for handling product operations

from src.database import Product, Review


class ProductManager:
    """
    Manager class for product-related operations
    """

    def __init__(self, session):
        """
        Initialize ProductManager with database session

        Args:
            session: SQLAlchemy session object
        """
        self.session = session

    def get_product(self, product_id):
        """
        Get product by ID

        Args:
            product_id: int - Product ID

        Returns:
            Product object or None
        """
        return self.session.query(Product).filter_by(id=product_id).first()

    def update_rating(self, product_id):
        """
        Recalculate product rating based on all reviews

        Args:
            product_id: int - Product ID

        Returns:
            float: Updated average rating
        """
        # Get all reviews for this product
        reviews = self.session.query(Review).filter_by(product_id=product_id).all()

        if not reviews:
            return 0.0

        # Calculate average rating
        avg_rating = sum(r.rating for r in reviews) / len(reviews)

        # Update product
        product = self.get_product(product_id)
        product.current_rating = round(avg_rating, 2)
        product.review_count = len(reviews)
        self.session.commit()

        return avg_rating

    def get_recent_reviews(self, product_id, limit=10):
        """
        Get recent reviews for a product

        IMPORTANT: Returns actual Review objects, not dicts
        This avoids N+1 query problem in agents.py

        Args:
            product_id: int - Product ID
            limit: int - Maximum number of reviews to return

        Returns:
            list of Review objects
        """
        reviews = (self.session.query(Review)
                   .filter_by(product_id=product_id)
                   .order_by(Review.iteration.desc())
                   .limit(limit)
                   .all())

        return reviews
