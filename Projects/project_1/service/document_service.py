"""
Document Service.

Handles business logic for user document management, uploads, verification, and retrieval.
Receives DocumentDAO via constructor injection to facilitate unit testing with mock DAOs.
"""

from models.document import UserDocument


class DocumentService:
    """
    Service layer handling user verification document operations.
    """

    def __init__(self, document_dao):
        """
        Constructor injection of the DocumentDAO dependency.

        :param document_dao: DocumentDAO instance (or fake/mock DAO in tests)
        """
        self.document_dao = document_dao

    def get_documents_for_user(self, user_id):
        """Retrieve all documents belonging to a specific user."""
        return self.document_dao.get_documents_for_user(user_id)

    def get_document_by_id(self, document_id):
        """Retrieve a specific user document by ID."""
        document = self.document_dao.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found.")
        return document

    def upload_document(self, user_id: int, doc_type: str, file_path: str):
        """
        Create and persist a new UserDocument record.

        :param user_id: User identifier owning the document
        :param doc_type: Type of document (e.g. 'Aadhaar', 'Passport', 'Govt ID')
        :param file_path: Server file path where document is stored
        :return: Persisted UserDocument instance
        """
        if not user_id:
            raise ValueError("user_id is required.")
        if not file_path:
            raise ValueError("file_path is required.")

        doc_type_clean = (doc_type or "Govt ID").strip()
        document = UserDocument(
            user_id=user_id,
            doc_type=doc_type_clean,
            file_path=file_path.strip(),
            verified=False
        )
        return self.document_dao.save_document(document)

    def verify_document(self, document_id: int, verified: bool = True):
        """
        Update verification status for a document.

        :param document_id: Document primary key
        :param verified: Verification status flag
        :return: Updated UserDocument instance
        """
        document = self.get_document_by_id(document_id)
        document.verified = verified
        return self.document_dao.update_document(document)

    def delete_document(self, document_id: int):
        """Delete a document record."""
        document = self.get_document_by_id(document_id)
        return self.document_dao.delete_document(document)
