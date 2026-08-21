"""
Document Service.

Handles business logic for user document management.
Receives DocumentDAO via constructor injection to facilitate unit testing with mock DAOs.
"""


class DocumentService:
    """
    Service layer handling user verification document retrieval.
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
