"""MeshLab dashboard — offline simulation by default."""
import networkx as nx
import pandas as pd
import streamlit as st
from meshlab.simulator import simulate

st.set_page_config(page_title="MeshLab", page_icon="📡", layout="wide")
st.title("📡 MeshLab")
st.caption("Meshtastic network exploration • simulation-first, privacy-conscious")
with st.sidebar:
    st.header("Workspace")
    mode = st.radio("Data source", ["Simulation", "Live radio (local only)"])
    count = st.slider("Virtual nodes", 2, 30, 10)
    seed = st.number_input("Simulation seed", 0, 100000, 42)
    radius = st.slider("Illustrative radio range", 1.0, 10.0, 5.0, 0.5)
if mode != "Simulation":
    st.info("Live radio support is provided by the optional local Python adapter. "
            "A persistent background gateway and safe connection controls are planned "
            "for the next milestone. This hosted dashboard does not access local USB devices.")
    st.stop()
data = simulate(count, int(seed), radius)
nodes, links = data["nodes"], data["links"]
a, b, c = st.columns(3)
a.metric("Nodes", len(nodes))
b.metric("Observed links (simulated)", len(links))
c.metric("Average battery", f"{sum(n['battery'] for n in nodes)/len(nodes):.0f}%")
st.subheader("Network topology")
graph = nx.Graph()
for node in nodes:
    graph.add_node(node["node_id"], label=node["name"])
for link in links:
    graph.add_edge(link["source"], link["target"])
positions = {node["node_id"]: (node["x"], node["y"]) for node in nodes}
edges = pd.DataFrame([{"x": [positions[u][0], positions[v][0]],
                       "y": [positions[u][1], positions[v][1]]} for u, v in graph.edges])
# Plotly is optional in the core; Streamlit's built-in chart handles positions.
st.scatter_chart(pd.DataFrame(nodes), x="x", y="y", color="battery",
                 size=100, height=400)
st.caption("Node positions are synthetic coordinates, not geographic locations. "
           "Links are listed below; this first chart does not draw edges.")
left, right = st.columns(2)
with left:
    st.subheader("Nodes")
    st.dataframe(pd.DataFrame(nodes), hide_index=True, use_container_width=True)
with right:
    st.subheader("Simulated links")
    st.dataframe(pd.DataFrame(links), hide_index=True, use_container_width=True)
st.caption("Simulation metrics are illustrative and must not be interpreted as RF predictions.")
