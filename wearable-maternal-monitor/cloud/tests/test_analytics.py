from cloud.src.analytics import zscore_flags, cluster_distance, FEATURES
import pandas as pd
import numpy as np

def test_zscore_flags_basic():
    idx = pd.date_range("2024-01-01", periods=120, freq="min")
    df = pd.DataFrame({
        "hr": np.r_[np.random.normal(80, 3, 110), np.repeat(110, 10)],
        "spo2": np.r_[np.random.normal(98, 1, 110), np.repeat(90, 10)],
        "temp": np.random.normal(36.7, 0.2, 120),
        "env_temp": np.random.normal(22, 1.0, 120),
        "motion": np.random.normal(0.1, 0.05, 120),
    }, index=idx)
    flags = zscore_flags(df.reset_index().rename(columns={"index":"ts"}).set_index("ts"), 2.5)
    assert flags.iloc[-1] >= 1
