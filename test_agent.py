# test_agent.py

import pandas as pd
from ml_agent import EventAnomalyDetector

def test_anomaly_detection():
    data = pd.DataFrame([
        {'severity': 3, 'timestamp': '2025-05-01T10:00:00', 'source_node': 'A'},
        {'severity': 1, 'timestamp': '2025-05-01T10:01:00', 'source_node': 'B'},
        {'severity': 5, 'timestamp': '2025-05-01T10:02:00', 'source_node': 'C'},
        {'severity': 1, 'timestamp': '2025-05-01T10:03:00', 'source_node': 'D'},
        {'severity': 4, 'timestamp': '2025-05-01T10:04:00', 'source_node': 'E'}
    ])
    
    detector = EventAnomalyDetector()
    detector.train(data)
    result = detector.predict(data)
    assert 'is_anomaly' in result.columns
    print(result[['source_node', 'is_anomaly', 'anomaly_score']])
