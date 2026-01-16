from typing import Optional
from pydantic import BaseModel

class SystemSettingsBase(BaseModel):
    base_delivery_fee: float = 2.0
    per_km_fee: float = 0.5
    free_delivery_threshold: float = 50.0
    max_delivery_distance: int = 15
    default_commission_rate: float = 0.15
    enable_whatsapp_notifications: bool = True
    business_name: str = "Lion Delivery"
    support_phone: Optional[str] = None
    support_email: Optional[str] = None
    default_language: str = "ar"
    operating_hours_start: str = "08:00"
    operating_hours_end: str = "23:00"

class SystemSettingsUpdate(SystemSettingsBase):
    pass

class SystemSettings(SystemSettingsBase):
    id: int

    class Config:
        from_attributes = True
