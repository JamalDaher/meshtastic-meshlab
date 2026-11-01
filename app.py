"""MeshLab interactive simulation dashboard."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from meshlab.simulator import simulate
from meshlab.topology import build_graph, shortest_route, network_summary

st.set_page_config(page_title="MeshLab", page_icon="📡", layout="wide")
st.title("📡 MeshLab")
st.caption("Mesh network simulation and monitoring • privacy-first")
with st.sidebar:
    st.header("Workspace")
    mode = st.radio("Data source", ["Simulation", "Live radio (local only)"])
    count = st.slider("Virtual nodes", 2, 30, 10)
    seed = st.number_input("Simulation seed", 0, 100000, 42)
    radius = st.slider("Illustrative radio range", 1.0, 10.0, 5.0, 0.5)
if mode != "Simulation":
    from meshlab.monitor import Monitor
    from meshlab.gateway import RadioGateway
    if "radio_gateway" not in st.session_state:
        st.session_state.radio_gateway = RadioGateway(Monitor())
    gateway = st.session_state.radio_gateway
    st.subheader("Local radio connection")
    transport = st.radio("Connection type", ["USB serial", "TCP / Wi-Fi"], horizontal=True)
    st.warning("Run locally on a trusted network. Do not expose a connected dashboard publicly.")
    target = st.text_input("Serial port" if transport == "USB serial" else "Private radio IP",
                           placeholder="COM3 or /dev/ttyUSB0" if transport == "USB serial" else "192.168.1.50")
    left, right = st.columns(2)
    with left:
        if st.button("Connect", disabled=gateway.connected):
            try:
                gateway.connect(target, "serial" if transport == "USB serial" else "tcp")
                st.success("Connected")
            except Exception as exc:
                st.error(f"Connection failed: {type(exc).__name__}: {exc}")
    with right:
        if st.button("Disconnect", disabled=not gateway.connected):
            try:
                gateway.disconnect()
                st.success("Disconnected")
            except Exception as exc:
                st.error(f"Disconnect failed: {type(exc).__name__}: {exc}")
    st.write("Status:", "Connected" if gateway.connected else "Disconnected")
    if st.button("Refresh received telemetry"):
        st.rerun()
    snapshot = gateway.monitor.snapshot()
    from meshlab.analytics import node_activity, signal_series, export_csv
    events = snapshot["events"]
    stats = node_activity(events)
    m1, m2, m3 = st.columns(3)
    m1.metric("Observed nodes", len(snapshot["nodes"]))
    m2.metric("Packets in memory", len(events))
    m3.metric("Active nodes (5 min)", sum(row["active"] for row in stats))
    st.subheader("Signal history")
    selected = st.selectbox("Node", ["All nodes"] + sorted(n["node"] for n in snapshot["nodes"]))
    series = signal_series(events, None if selected == "All nodes" else selected)
    if series:
        df = pd.DataFrame(series)
        df["time"] = pd.to_datetime(df["time"], utc=True)
        st.line_chart(df, x="time", y=["snr", "rssi"], height=280)
        st.caption("SNR is in dB; RSSI is in dBm. Their scales differ.")
    else:
        st.info("No received signal readings yet.")
    st.subheader("Node activity")
    st.dataframe(pd.DataFrame(stats), hide_index=True, use_container_width=True)
    st.download_button("Export metadata CSV", export_csv(events),
                       file_name="meshlab-telemetry.csv", mime="text/csv", disabled=not events)
    st.subheader("Latest node readings")
    st.dataframe(pd.DataFrame(snapshot["nodes"]), hide_index=True, use_container_width=True)
    st.subheader("Recent packet metadata")
    st.dataframe(pd.DataFrame(snapshot["events"]), hide_index=True, use_container_width=True)
    st.caption("Only sender ID, reception time, RSSI and SNR are stored in memory. "
               "No message text, payload or position is retained.")
    st.stop()

data = simulate(count, int(seed), radius)
nodes, links = data["nodes"], data["links"]
graph = build_graph(data)
summary = network_summary(graph)
a, b, c, d = st.columns(4)
a.metric("Nodes", len(nodes))
b.metric("Links", len(links))
c.metric("Connected groups", summary["components"])
d.metric("Average battery", f"{sum(n['battery'] for n in nodes)/len(nodes):.0f}%")

st.subheader("Interactive network topology")
node_by_id = {n["node_id"]: n for n in nodes}
fig = go.Figure()
for link in links:
    src, dst = node_by_id[link["source"]], node_by_id[link["target"]]
    fig.add_trace(go.Scatter(
        x=[src["x"], dst["x"]], y=[src["y"], dst["y"]],
        mode="lines", line=dict(width=1.8, color="#4f8fa5"),
        hoverinfo="skip", showlegend=False))
fig.add_trace(go.Scatter(
    x=[n["x"] for n in nodes], y=[n["y"] for n in nodes],
    mode="markers+text", text=[n["name"] for n in nodes],
    textposition="top center", customdata=[[n["node_id"], n["battery"]] for n in nodes],
    marker=dict(size=16, color=[n["battery"] for n in nodes],
                colorscale="Viridis", showscale=True, colorbar=dict(title="Battery %"),
                line=dict(width=1, color="#d8e5ef")),
    hovertemplate="%{text}<br>ID: %{customdata[0]}<br>Battery: %{customdata[1]}%<extra></extra>",
    showlegend=False))
fig.update_layout(template="plotly_dark", height=530, margin=dict(l=15,r=15,t=15,b=15),
                  xaxis=dict(title="Synthetic X", range=[-0.5, 10.5]),
                  yaxis=dict(title="Synthetic Y", range=[-0.5, 10.5],
                             scaleanchor="x", scaleratio=1))
st.plotly_chart(fig, use_container_width=True)
st.caption("Synthetic coordinates and illustrative links; this is not a geographic map or validated RF model.")

st.subheader("Route explorer")
names = {n["name"]: n["node_id"] for n in nodes}
left, right = st.columns(2)
with left:
    source_name = st.selectbox("Source node", list(names))
with right:
    target_name = st.selectbox("Destination node", list(names), index=len(names)-1)
route = shortest_route(graph, names[source_name], names[target_name])
if route is None:
    st.warning("No route exists between those nodes with the selected range.")
else:
    id_to_name = {v:k for k,v in names.items()}
    st.success(" → ".join(id_to_name[n] for n in route))
    st.caption(f"{len(route)-1} simulated hop(s); routing is shortest-hop graph analysis, "
               "not a reproduction of Meshtastic firmware routing.")

tab1, tab2 = st.tabs(["Nodes", "Links"])
with tab1:
    st.dataframe(pd.DataFrame(nodes), hide_index=True, use_container_width=True)
with tab2:
    st.dataframe(pd.DataFrame(links), hide_index=True, use_container_width=True)
