from src.extensions import db
from src.utils.db_utils import CreatedAt, UUIDGenerator

class Image(db.Model):
    __tablename__ = 'images_url_table'
    id = UUIDGenerator(db,'images')
    entity_id = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=False)
    tag = db.Column(db.String, nullable=True)
    uploaded_at = CreatedAt(db)

    __table_args__ = (
        db.Index('league_trophies_idx', 'entity_id', 'tag'),
    )

    def to_json(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "image_url": self.image_url,
            "tag": self.tag,
            "uploaded_at": self.uploaded_at.isoformat()
        }