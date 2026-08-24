
from models.document import UserDocument


class DocumentService:

    def __init__(self, document_dao):
        self.document_dao = document_dao

    def get_documents_for_user(self, user_id):
        return self.document_dao.get_documents_for_user(user_id)

    def get_document_by_id(self, document_id):
        document = self.document_dao.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found.")
        return document

    def upload_document(self, user_id: int, doc_type: str, file_path: str):
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
        document = self.get_document_by_id(document_id)
        document.verified = verified
        return self.document_dao.update_document(document)

    def delete_document(self, document_id: int):
        document = self.get_document_by_id(document_id)
        return self.document_dao.delete_document(document)
