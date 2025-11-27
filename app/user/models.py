from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    provider = Column(String, default="local")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    shorts = relationship("app.models.Shorts", back_populates="owner")
