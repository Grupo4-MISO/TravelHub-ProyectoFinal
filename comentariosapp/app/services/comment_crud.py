from app.db.models import Review, db
from sqlalchemy.exc import IntegrityError
from uuid import UUID

class ReviewCrud:

    def create_review(self, data: dict):
        try:
            review = Review(
                hospedajeId=data.get("hospedajeId"),
                userId=data.get("userId"),
                userName=data.get("userName"),
                rating=data.get("rating"),
                comment=data.get("comment")
            )

            db.session.add(review)
            db.session.commit()
            return review

        except IntegrityError:
            db.session.rollback()
            return None

        except IntegrityError:
            db.session.rollback()
            return None

    def get_review_by_id(self, review_id: UUID):
        return Review.query.get(review_id)

    def get_all_reviews_by_hospedaje_id(self, hospedaje_id: UUID):
        return Review.query.filter(Review.hospedajeId == hospedaje_id).all()

    def update_review(self, review_id: UUID, data: dict):
        review = self.get_review_by_id(review_id)
        if not review:
            return None

        try:
            for key, value in data.items():
                if hasattr(review, key) and value is not None:
                    setattr(review, key, value)

            db.session.commit()
            return review

        except IntegrityError:
            db.session.rollback()
            return None

    def delete_review(self, review_id: UUID):
        review = self.get_review_by_id(review_id)
        if not review:
            return False

        db.session.delete(review)
        db.session.commit()
        return True


comment_crud = ReviewCrud()
