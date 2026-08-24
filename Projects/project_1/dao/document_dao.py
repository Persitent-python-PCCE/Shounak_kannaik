
from models.document import UserDocument
from config.database import db


class DocumentDAO:

    def get_documents_for_user(self, user_id):
        """Fetch all documents belonging to a specific user."""
        return db.session.execute(
            db.select(UserDocument).where(UserDocument.user_id == user_id)
        ).scalars().all()

    def get_by_id(self, document_id):
        """Fetch a user document by primary key ID."""
        return db.session.get(UserDocument, document_id)

    def save_document(self, document):
        """Persist a newly uploaded user document."""
        db.session.add(document)
        db.session.commit()
        return document

    def update_document(self, document):
        """Commit modifications made to a user document record."""
        db.session.commit()
        return document

    def delete_document(self, document):
        """Delete a user document record from the database."""
        db.session.delete(document)
        db.session.commit()
        return True

    def get_by_doc_type(self, user_id, doc_type):
        """Fetch user documents filtered by user ID and document type."""
        return db.session.execute(
            db.select(UserDocument).where(
                UserDocument.user_id == user_id,
                UserDocument.doc_type == doc_type,
            )
        ).scalars().all()
