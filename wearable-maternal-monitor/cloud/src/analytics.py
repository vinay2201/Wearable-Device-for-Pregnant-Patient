from __future__ import annotations
import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans

FEATURES = ["hr","spo2","temp","env_temp","motion"]

def zscore_flags(df: pd.DataFrame, threshold: float) -> pd.Series:
    # z-score per feature over rolling window (per user handled upstream)
    z = (df[FEATURES] - df[FEATURES].rolling(30, min_periods=10).mean()) / (df[FEATURES].rolling(30, min_periods=10).std(ddof=0) + 1e-6)
    z = z.abs() >= threshold
    # N-of-M rule: at time t, if at least N features are flagged, anomaly
    flags = z.sum(axis=1)
    return flags

def cluster_distance(df: pd.DataFrame, k: int = 3) -> pd.Series:
    # Fit MiniBatchKMeans to user's historical distribution (lightweight online-ish behavior)
    hist = df[FEATURES].dropna()
    if len(hist) < max(30, k*10):
        return pd.Series(np.zeros(len(df)), index=df.index)
    model = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=64)
    model.fit(hist.values)
    # distance to nearest centroid for each point
    from numpy.linalg import norm
    dists = []
    for row in df[FEATURES].values:
        if np.any(pd.isna(row)):
            dists.append(0.0); continue
        d = np.min(norm(model.cluster_centers_ - row, axis=1))
        dists.append(float(d))
    # normalize distances
    s = pd.Series(dists, index=df.index)
    return (s - s.rolling(50, min_periods=10).median()) / (s.rolling(50, min_periods=10).std(ddof=0) + 1e-6)
