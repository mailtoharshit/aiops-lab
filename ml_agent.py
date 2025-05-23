# ml_agent.py

from sklearn.ensemble import IsolationForest
import pandas as pd

class EventAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)

    def train(self, event_data: pd.DataFrame):
        features = self._prepare_features(event_data)
        self.model.fit(features)

    def predict(self, event_data: pd.DataFrame):
        features = self._prepare_features(event_data)
        event_data['anomaly_score'] = self.model.decision_function(features)
        event_data['is_anomaly'] = self.model.predict(features)
        # Convert -1/1 to True/False
        event_data['is_anomaly'] = event_data['is_anomaly'].apply(lambda x: True if x == -1 else False)
        return event_data

    def _prepare_features(self, df):
        # Replace this with real feature engineering logic
        df = df.copy()
        df['severity'] = df['severity'].astype(float)
        df['timestamp'] = pd.to_numeric(pd.to_datetime(df['timestamp'], errors='coerce'))
        df['source_node_id'] = df['source_node'].astype('category').cat.codes
        return df[['severity', 'timestamp', 'source_node_id']]
