import secrets
import hashlib
from datetime import datetime, timedelta
from models import db

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_hash = db.Column(db.String(128), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('reset_tokens', lazy=True, cascade='all, delete-orphan'))

    @classmethod
    def generate_token_for_user(cls, user_id):
        # Invalidate any existing active tokens for this user
        cls.query.filter_by(user_id=user_id, used=False).update({'used': True})
        
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        expires = datetime.utcnow() + timedelta(minutes=30)
        
        token_entry = cls(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires,
            used=False
        )
        db.session.add(token_entry)
        db.session.commit()
        
        return raw_token

    @classmethod
    def verify_token(cls, raw_token):
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        entry = cls.query.filter_by(token_hash=token_hash, used=False).first()
        
        if not entry:
            return None
            
        if datetime.utcnow() > entry.expires_at:
            entry.used = True
            db.session.commit()
            return None
            
        return entry
