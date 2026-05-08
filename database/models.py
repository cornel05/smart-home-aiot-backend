from datetime import datetime
from sqlalchemy import Integer, String, Float, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class NodeMetadata(Base):
    __tablename__ = "node_metadata"

    node_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    installation_date: Mapped[datetime] = mapped_column(default=func.now())
    status: Mapped[str] = mapped_column(String(50), default="active")


class SensorTelemetry(Base):
    __tablename__ = "sensor_telemetry"

    timestamp: Mapped[datetime] = mapped_column(primary_key=True, default=func.now())
    node_id: Mapped[int] = mapped_column(ForeignKey("node_metadata.node_id"), primary_key=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    humidity: Mapped[float] = mapped_column(Float, nullable=True)
    light_intensity: Mapped[float] = mapped_column(Float, nullable=True)
    gas_ppm: Mapped[float] = mapped_column(Float, nullable=True)
    door_open: Mapped[bool] = mapped_column(Boolean, nullable=True)


class SystemEvent(Base):
    __tablename__ = "system_events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(default=func.now())
    node_id: Mapped[int] = mapped_column(ForeignKey("node_metadata.node_id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100))
    trigger_source: Mapped[str] = mapped_column(String(50), default="automatic")
    target_device: Mapped[str] = mapped_column(String(100), nullable=True)
    value: Mapped[float] = mapped_column(Float, nullable=True)
