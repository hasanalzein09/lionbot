from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base_class import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    base_delivery_fee = Column(Float, default=2.0)
    per_km_fee = Column(Float, default=0.5)
    free_delivery_threshold = Column(Float, default=50.0)
    max_delivery_distance = Column(Integer, default=15)
    default_commission_rate = Column(Float, default=0.15)
    enable_whatsapp_notifications = Column(Boolean, default=True)
    business_name = Column(String, default="Lion Delivery")
    support_phone = Column(String, nullable=True)
    support_email = Column(String, nullable=True)
    default_language = Column(String, default="ar")
    operating_hours_start = Column(String, default="08:00")
    operating_hours_end = Column(String, default="23:00")
