from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

FEATURES = ["temperature", "humidity", "light_intensity", "gas_ppm"]
WINDOW_SIZE = 60


async def extract(db_session, hours: int = 24) -> pd.DataFrame:
    from sqlalchemy import select
    from database.models import SensorTelemetry

    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db_session.execute(
        select(SensorTelemetry)
        .where(SensorTelemetry.timestamp >= since)
        .order_by(SensorTelemetry.timestamp.asc())
    )
    rows = result.scalars().all()

    if not rows:
        return pd.DataFrame(columns=["timestamp"] + FEATURES)

    return pd.DataFrame(
        [
            {
                "timestamp": r.timestamp,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "light_intensity": r.light_intensity,
                "gas_ppm": r.gas_ppm,
            }
            for r in rows
        ]
    )


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp").sort_index()
    df = df[FEATURES].resample("1min").mean()
    df = df.interpolate(method="time").fillna(method="bfill").fillna(method="ffill")

    for col in FEATURES:
        col_min, col_max = df[col].min(), df[col].max()
        if col_max > col_min:
            df[col] = (df[col] - col_min) / (col_max - col_min)
        else:
            df[col] = 0.0

    return df


def build_windows(df: pd.DataFrame, window: int = WINDOW_SIZE) -> np.ndarray:
    values = df[FEATURES].values
    if len(values) < window:
        return np.empty((0, window, len(FEATURES)))
    return np.stack([values[i : i + window] for i in range(len(values) - window)])


if HAS_TORCH:
    class LSTMModel(nn.Module):
        def __init__(self, input_size: int = 4, hidden_size: int = 64, num_layers: int = 2):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size, hidden_size, num_layers, batch_first=True, dropout=0.2
            )
            self.fc = nn.Linear(hidden_size, 1)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out, _ = self.lstm(x)
            return torch.sigmoid(self.fc(out[:, -1, :]))
