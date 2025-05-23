from ml_agent import EventAnomalyDetector

# Example injection into simulation pipeline
detector = EventAnomalyDetector()
event_df = pd.DataFrame(events)  # assuming your events are list of dicts
detector.train(event_df)  # train on initial batch
analyzed = detector.predict(event_df)  # get anomaly flags
# Inside simulator.py (or main processor loop)

from ml_agent import EventAnomalyDetector
import pandas as pd

# Convert your event list into DataFrame
event_df = pd.DataFrame(event_list)  # event_list = list of dicts

# ML processing
detector = EventAnomalyDetector()
detector.train(event_df)  # Initial training (could be skipped if online)
event_df = detector.predict(event_df)

# Continue using `event_df` – now includes is_anomaly flag
for _, event in event_df.iterrows():
    print(f"Event at {event['source_node']} is_anomaly={event['is_anomaly']}")

from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="AIOps Event Summary with Anomaly Detection")

table.add_column("Source Node", justify="center")
table.add_column("Severity", justify="center")
table.add_column("Anomaly", justify="center")
table.add_column("Score", justify="center")

for _, row in event_df.iterrows():
    table.add_row(
        row['source_node'],
        str(row['severity']),
        "✅" if row['is_anomaly'] else "❌",
        f"{row['anomaly_score']:.3f}"
    )

console.print(table)
