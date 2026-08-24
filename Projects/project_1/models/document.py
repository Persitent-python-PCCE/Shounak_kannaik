
from config.database import db


class UserDocument(db.Model):
    __tablename__ = "user_documents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=db.func.now())


    user = db.relationship("User", back_populates="documents")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "doc_type": self.doc_type,
            "file_path": self.file_path,
            "verified": self.verified,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
