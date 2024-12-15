from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Ожидание')  # Поле для статуса
    # output_file = db.Column(db.String(100), nullable=True)  # Файл для вывода

    def __repr__(self):
        return f"<Task {self.id}: {self.filename}, Status: {self.status}>"