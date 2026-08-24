
from config.database import db


event_genres = db.Table(
    "event_genres",
    db.Column("event_id", db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),

)


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    events = db.relationship("Event", secondary=event_genres, back_populates = "genres")

    def to_dict(self):
        return {
            "id": self.id,
            "genre_name": self.genre_name,
            "description": self.description,
        }
