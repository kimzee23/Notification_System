from dataclasses import dataclass, field
from datetime import datetime



@dataclass
class DeliveryAttempt:
    provider:    str
    success:     bool
    reason:      str      = ''
    provider_id: str      = ''
    attempted_at: datetime = field(default_factory=datetime.utcnow)