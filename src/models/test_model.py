from src.extensions import db

class TestModel(db.Model):
    __tablename__ =  'test_table'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False, unique=True)