from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Restaurant(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Subscription details
    subscription_tier = Column(String, default="basic") # basic, pro, enterprise
    commission_rate = Column(Float, default=0.0)
    
    branches = relationship("Branch", back_populates="restaurant")
    menus = relationship("Menu", back_populates="restaurant")

class Branch(Base):
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"))
    name = Column(String, index=True) # e.g., "Downtown Branch"
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    restaurant = relationship("Restaurant", back_populates="branches")
