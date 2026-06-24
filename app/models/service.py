import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Protocol(str, enum.Enum):
    TCP = "TCP"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SSH = "SSH"


class ServiceStatus(str, enum.Enum):
    UP = "UP"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    host_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hosts.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    protocol: Mapped[Protocol] = mapped_column(Enum(Protocol), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    check_interval_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    status: Mapped[ServiceStatus] = mapped_column(
        Enum(ServiceStatus), default=ServiceStatus.UNKNOWN, nullable=False
    )
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_checked: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Service {self.name} ({self.protocol}:{self.port}) → {self.status}>"