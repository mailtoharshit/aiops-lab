# ml_agent.py

from sklearn.ensemble import IsolationForest
import pandas as pd

class EventAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)

    def train(self, df: pd.DataFrame):
        features = self._prepare(df)
        self.model.fit(features)

    def predict(self, df: pd.DataFrame):
        features = self._prepare(df)
        df['anomaly_score'] = self.model.decision_function(features)
        df['is_anomaly'] = self.model.predict(features).tolist()
        df['is_anomaly'] = df['is_anomaly'].apply(lambda x: True if x == -1 else False)
        return df

    def _prepare(self, df):
        df = df.copy()
        df['severity'] = df['severity'].astype(float)
        df['timestamp'] = pd.to_numeric(pd.to_datetime(df['timestamp'], errors='coerce'))
        df['source_node_id'] = df['source_node'].astype('category').cat.codes
        return df[['severity', 'timestamp', 'source_node_id']]
