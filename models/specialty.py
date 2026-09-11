from models import db

class Specialty(db.Model):
    __tablename__ = 'specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='fa-tooth')
    is_active = db.Column(db.Boolean, default=True)

    doctors = db.relationship('Doctor', backref='specialty_rel', lazy=True)

    def __repr__(self):
        return f'<Specialty {self.name}>'
