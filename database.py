from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Task {self.id}: {self.filename}>"