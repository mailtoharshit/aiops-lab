# dashboard.py

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from ml_agent import EventAnomalyDetector
import random
import datetime

st.set_page_config(layout="wide")
st.title("🌐 AIOps Simulation & Root Cause Dashboard")

def simulate_events(n=100):
    sources = ['web-server', 'auth-db', 'api-gateway', 'cache-node', 'app-node', 'worker-1', 'worker-2']
    tools = ['CloudWatch', 'Datadog', 'Prometheus']
    now = datetime.datetime.now()
    data = []
    for _ in range(n):
        data.append({
            'source_node': random.choice(sources),
            'severity': random.randint(1, 5),
            'timestamp': now - datetime.timedelta(minutes=random.randint(0, 300)),
            'tool': random.choice(tools)
        })
    return pd.DataFrame(data)

def build_correlation_graph(df):
    G = nx.DiGraph()
    nodes = df['source_node'].unique().tolist()
    for i in range(len(nodes) - 1):
        G.add_edge(nodes[i], nodes[i+1])
    return G

def render_graph(G, anomalies):
    pos = nx.spring_layout(G, seed=42)
    color_map = ['#FF4B4B' if node in anomalies else '#4CAF50' for node in G.nodes()]
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=color_map, edge_color='gray', node_size=1200, font_weight='bold')
    st.pyplot(fig)

def detect_anomalies(df):
    agent = EventAnomalyDetector()
    agent.train(df)
    return agent.predict(df)

def render_event_logs(df):
    st.subheader("📟 Real-Time Event Logs")
    logs = []
    for _, row in df.iterrows():
        emoji = "🚨" if row['is_anomaly'] else "✅"
        logs.append(f"{emoji} [{row['timestamp']}] {row['source_node']} via {row['tool']} - Severity {row['severity']}")
    st.code("\n".join(logs), language="shell")

def explain_event(row):
    if row['is_anomaly']:
        return f"🔎 {row['source_node']} triggered a critical anomaly via {row['tool']} with severity {row['severity']}."
    else:
        return f"ℹ️ {row['source_node']} is normal. No issues detected."

def show_llm_analysis(df):
    st.subheader("🧠 Event Intelligence (LLM-style Analysis)")
    for _, row in df.iterrows():
        st.markdown(f"- {explain_event(row)}")

# Sidebar controls
num_events = st.sidebar.slider("🎚️ Number of Events", min_value=10, max_value=200, value=50)
run = st.sidebar.button("🔁 Simulate & Analyze")

if run:
    df = simulate_events(num_events)
    df = detect_anomalies(df)
    anomalies = df[df['is_anomaly'] == True]['source_node'].unique()
    tool_counts = df['tool'].value_counts().to_dict()

    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧾 Total Events", len(df))
    col2.metric("🚨 Anomalies", df['is_anomaly'].sum())
    col3.metric("📍 Root Causes", len(anomalies))
    col4.metric("🔧 Tools Used", ', '.join(tool_counts.keys()))

    st.subheader("🌐 Service Dependency Graph")
    G = build_correlation_graph(df)
    render_graph(G, anomalies)

    render_event_logs(df)

    st.subheader("📊 Event Table")
    st.dataframe(df[['timestamp', 'source_node', 'severity', 'tool', 'is_anomaly', 'anomaly_score']])

    st.download_button("📥 Download CSV", df.to_csv(index=False), "aiops_events.csv", "text/csv")

    show_llm_analysis(df)

    st.success("✅ Simulation complete!")
