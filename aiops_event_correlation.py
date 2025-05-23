# aiops_event_correlation.py

import networkx as nx
import matplotlib
matplotlib.use("Agg")  # ✅ Fix for macOS thread-safe rendering
import matplotlib.pyplot as plt
import random
from datetime import datetime
import time
import json
import csv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# --- Setup for FastAPI Templates and Static Files ---
templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Event Generator ---
class EventGenerator:
    def __init__(self, nodes, tools):
        self.nodes = nodes
        self.tools = tools

    def generate_event(self, node):
        severities = ["INFO", "WARNING", "ERROR", "CRITICAL"]
        return {
            "id": f"evt_{random.randint(100000,999999)}",
            "source": node,
            "severity": random.choices(severities, [0.4, 0.3, 0.2, 0.1])[0],
            "timestamp": datetime.utcnow().isoformat(),
            "tool": random.choice(self.tools)
        }

    def generate_batch(self, count):
        return [self.generate_event(random.choice(self.nodes)) for _ in range(count)]

# --- Correlator ---
class EventCorrelator:
    def __init__(self, graph):
        self.graph = graph
        self.algorithm = "Graph Traversal (Dependency Heuristics)"
        self.telemetry = {}

    def attach_events(self, events):
        for event in events:
            self.graph.nodes[event["source"]].setdefault("alerts", []).append(event)

    def find_root_causes(self):
        start_time = time.time()
        roots = []
        for node in self.graph.nodes:
            alerts = self.graph.nodes[node].get("alerts", [])
            if any(a["severity"] in ["ERROR", "CRITICAL"] for a in alerts):
                children = list(self.graph.successors(node))
                if all(not self.graph.nodes[c].get("alerts") for c in children):
                    roots.append(node)
        self.telemetry = {
            "algorithm": self.algorithm,
            "time_taken_sec": round(time.time() - start_time, 5),
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "correlated_nodes": len(roots)
        }
        return roots

    def export_to_json(self, filename="alerts.json"):
        data = {
            node: self.graph.nodes[node].get("alerts", [])
            for node in self.graph.nodes if self.graph.nodes[node].get("alerts")
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def export_to_csv(self, filename="alerts.csv"):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["source", "severity", "timestamp", "tool"])
            for node in self.graph.nodes:
                for alert in self.graph.nodes[node].get("alerts", []):
                    writer.writerow([alert["source"], alert["severity"], alert["timestamp"], alert["tool"]])

    def visualize_graph(self):
        pos = nx.spring_layout(self.graph)
        plt.figure(figsize=(10, 8))
        colors = []
        for node in self.graph.nodes:
            if self.graph.nodes[node].get("alerts"):
                severities = [a["severity"] for a in self.graph.nodes[node]["alerts"]]
                if "CRITICAL" in severities:
                    colors.append("red")
                elif "ERROR" in severities:
                    colors.append("orange")
                elif "WARNING" in severities:
                    colors.append("yellow")
                else:
                    colors.append("green")
            else:
                colors.append("lightgray")
        nx.draw(self.graph, pos, with_labels=True, node_color=colors, node_size=1200, font_size=10, edge_color="gray")
        plt.title("Infrastructure Graph with Alerts")
        plt.savefig("static/graph.png")
        plt.close()

    def get_graph_data(self):
        nodes_data = []
        edges_data = []
        for node in self.graph.nodes:
            alerts = self.graph.nodes[node].get("alerts", [])
            severity = alerts[-1]["severity"] if alerts else "INFO"
            nodes_data.append({"id": node, "label": node, "severity": severity})
        for src, dst in self.graph.edges:
            edges_data.append({"source": src, "target": dst})
        return {"nodes": nodes_data, "edges": edges_data}

# --- App State ---
correlator = None
all_events = []

def build_infra():
    G = nx.DiGraph()
    nodes = [f"Service{i}" for i in range(1, 16)]
    for node in nodes:
        G.add_node(node)
    for _ in range(25):
        src, dst = random.sample(nodes, 2)
        G.add_edge(src, dst)
    return G, nodes

# --- Routes ---
@app.get("/run")
def run_event_analysis():
    global correlator, all_events
    graph, nodes = build_infra()
    tools = ["CloudWatch", "Datadog"]
    generator = EventGenerator(nodes, tools)
    correlator = EventCorrelator(graph)
    all_events = generator.generate_batch(200)
    correlator.attach_events(all_events)
    roots = correlator.find_root_causes()
    correlator.export_to_json()
    correlator.export_to_csv()
    correlator.visualize_graph()
    return JSONResponse({"root_causes": roots, "telemetry": correlator.telemetry})

@app.get("/graph-data")
def graph_data():
    if correlator:
        return JSONResponse(content=correlator.get_graph_data())
    else:
        return JSONResponse(content={"nodes": [], "edges": []})

@app.get("/graph")
def graph_ui(request: Request):
    return templates.TemplateResponse("graph.html", {"request": request})
