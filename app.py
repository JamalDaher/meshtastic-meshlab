"""MeshLab interactive simulation dashboard."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from meshlab.simulator import simulate
from meshlab.topology import build_graph, shortest_route, network_summary
from meshlab.resilience import analyze_failure, critical_nodes
from meshlab.timeline import generate_timeline
from meshlab.reliability import single_node_impact, range_comparison
from meshlab.report import build_report, export_json
from meshlab.scenarios import encode_scenario, decode_scenario, compare_scenarios
from meshlab.weak_points import weak_points
from meshlab.outage_overlay import outage_overlay

st.set_page_config(page_title="MeshLab", page_icon="📡", layout="wide")
st.title("📡 MeshLab")
st.caption("Mesh network simulation and monitoring • privacy-first")
with st.sidebar:
    st.header("Workspace")
    mode = st.radio("Data source", ["Simulation", "Live radio (local only)"])
    if mode == "Simulation":
        with st.expander("Simulation settings", expanded=True):
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
failed_names = st.multiselect("Simulate offline nodes", [n["name"] for n in nodes],
                              help="Offline nodes are greyed out and their links disappear from the active topology.")
failed_ids = [n["node_id"] for n in nodes if n["name"] in failed_names]
overlay = outage_overlay(data, failed_ids)
offline_ids = set(overlay["offline_nodes"])
st.caption(f"Active topology: {len(overlay['online_nodes'])} nodes, {len(overlay['active_links'])} links, {overlay['state']['components']} connected groups.")
node_by_id = {n["node_id"]: n for n in nodes}
fig = go.Figure()
weak = weak_points(data)
highlight_weak = st.toggle("Highlight critical nodes and bridge links", value=True)
bridge_links = set(weak["bridge_links"]) if highlight_weak else set()
critical_ids = set(weak["critical_nodes"]) if highlight_weak else set()
for link in overlay["active_links"]:
    src, dst = node_by_id[link["source"]], node_by_id[link["target"]]
    is_bridge = tuple(sorted((link["source"], link["target"]))) in bridge_links
    fig.add_trace(go.Scatter(
        x=[src["x"], dst["x"]], y=[src["y"], dst["y"]],
        mode="lines", line=dict(width=3.5 if is_bridge else 1.8,
                                color="#ff9f43" if is_bridge else "#4f8fa5"),
        hoverinfo="skip", showlegend=False))
fig.add_trace(go.Scatter(
    x=[n["x"] for n in nodes], y=[n["y"] for n in nodes],
    mode="markers+text", text=[n["name"] for n in nodes],
    textposition="top center", customdata=[[n["node_id"], n["battery"]] for n in nodes],
    marker=dict(size=[23 if n["node_id"] in critical_ids and n["node_id"] not in offline_ids else 16 for n in nodes],
                color=[n["battery"] if n["node_id"] not in offline_ids else -1 for n in nodes],
                colorscale=[[0, "#888888"], [0.01, "#440154"], [0.25, "#3b528b"], [0.5, "#21918c"], [0.75, "#5ec962"], [1, "#fde725"]],
                cmin=-1, cmax=100, showscale=False,
                line=dict(width=[3 if n["node_id"] in critical_ids and n["node_id"] not in offline_ids else 1 for n in nodes],
                          color=["#ff9f43" if n["node_id"] in critical_ids and n["node_id"] not in offline_ids else "#d8e5ef" for n in nodes])),
    hovertemplate="%{text}<br>ID: %{customdata[0]}<br>Battery: %{customdata[1]}%<extra></extra>",
    showlegend=False))
fig.update_layout(template="plotly_dark", height=530, margin=dict(l=15,r=15,t=15,b=15),
                  xaxis=dict(title="Synthetic X", range=[-0.5, 10.5]),
                  yaxis=dict(title="Synthetic Y", range=[-0.5, 10.5],
                             scaleanchor="x", scaleratio=1))
st.plotly_chart(fig, use_container_width=True)
st.caption("Synthetic coordinates and illustrative links; this is not a geographic map or validated RF model.")
st.caption("Grey nodes are offline in the selected scenario; only active links are drawn.")
st.caption(f"Graph weak points: {weak['critical_node_count']} critical node(s), {weak['bridge_link_count']} bridge link(s). Orange highlights show graph vulnerabilities, not measured RF risk.")

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

st.subheader("Network resilience lab")
st.caption("Remove virtual nodes to explore network fragmentation. This is graph analysis, not a real-world RF or packet-delivery prediction.")
critical = critical_nodes(data)
id_to_label = {n["node_id"]: n["name"] for n in nodes}
st.write("Critical bridge nodes:", ", ".join(id_to_label[n] for n in critical) if critical else "None")
failure = overlay["state"]
r1, r2, r3 = st.columns(3)
r1.metric("Remaining nodes", failure["remaining_nodes"])
r2.metric("Remaining links", failure["remaining_links"])
r3.metric("Connected groups", failure["components"],
          delta=failure["components"] - failure["baseline_components"],
          delta_color="inverse")
if failure["groups"]:
    st.write("Connected groups after failure:")
    for i, group in enumerate(failure["groups"], start=1):
        st.write(f"Group {i}: " + ", ".join(id_to_label[n] for n in group))
else:
    st.info("No nodes remain in this scenario.")

st.subheader("Simulation event timeline")
st.caption("Deterministic, illustrative node outages and recoveries—not observed radio events.")
steps = st.slider("Timeline steps", 5, 100, 25, 5)
timeline = generate_timeline(data, seed=int(seed), steps=steps)
timeline_df = pd.DataFrame(timeline)
t1, t2 = st.columns(2)
with t1:
    st.line_chart(timeline_df, x="step", y="active_nodes", height=240)
with t2:
    st.line_chart(timeline_df, x="step", y="connected_groups", height=240)
st.dataframe(timeline_df.assign(node=timeline_df["node"].map(id_to_label)),
             hide_index=True, use_container_width=True)
st.download_button("Export simulated events CSV",
                   timeline_df.to_csv(index=False),
                   file_name="meshlab-simulation-events.csv", mime="text/csv")

st.subheader("Network reliability comparison")
st.caption("Compare synthetic single-node failures and illustrative radio ranges; not measured reliability.")
impact_df = pd.DataFrame(single_node_impact(data))
st.write("Single-node outage sensitivity")
st.dataframe(impact_df, hide_index=True, use_container_width=True)
st.download_button("Export node impact CSV", impact_df.to_csv(index=False),
                   file_name="meshlab-node-impact.csv", mime="text/csv")
range_values = sorted(set([max(0.5, round(radius * factor, 2)) for factor in (0.5, 0.75, 1, 1.25, 1.5)]))
comparison_df = pd.DataFrame(range_comparison(count, int(seed), range_values))
st.write("Illustrative range comparison (same node positions)")
st.line_chart(comparison_df, x="range", y=["links", "connected_groups"], height=260)
st.dataframe(comparison_df, hide_index=True, use_container_width=True)

st.subheader("Scenario planner")
st.caption("Save simulation settings, reload them later, and compare two synthetic network configurations.")
current_scenario = {"count": count, "seed": int(seed), "radius": float(radius)}
st.download_button("Save current scenario JSON", encode_scenario(current_scenario),
                   file_name="meshlab-scenario.json", mime="application/json")
uploaded_scenario = st.file_uploader("Load a saved scenario JSON", type=["json"])
if uploaded_scenario is not None:
    try:
        loaded = decode_scenario(uploaded_scenario.getvalue().decode("utf-8"))
        st.success("Scenario loaded for comparison.")
        st.json(loaded)
    except (ValueError, UnicodeError) as exc:
        st.error(f"Invalid scenario file: {exc}")
        loaded = None
else:
    loaded = None
with st.expander("Compare two scenarios", expanded=False):
    st.caption("Scenario A uses current settings. Scenario B can use a loaded file or manual settings.")
    if loaded is not None:
        other_scenario = loaded
    else:
        b_count = st.slider("Scenario B nodes", 2, 30, count, key="scenario_b_count")
        b_seed = st.number_input("Scenario B seed", 0, 100000, int(seed), key="scenario_b_seed")
        b_radius = st.slider("Scenario B range", 1.0, 10.0, float(radius), 0.5, key="scenario_b_radius")
        other_scenario = {"count": b_count, "seed": int(b_seed), "radius": b_radius}
    st.dataframe(pd.DataFrame(compare_scenarios(current_scenario, other_scenario)),
                 hide_index=True, use_container_width=True)
    if current_scenario["count"] != other_scenario["count"] or current_scenario["seed"] != other_scenario["seed"]:
        st.info("Node count or seed differs. Results compare different node layouts, not only radio range.")

st.subheader("Reproducible simulation report")
st.caption("Download the simulation inputs, topology, connectivity summary, and node impact as JSON.")
st.download_button("Download simulation report JSON",
                   export_json(build_report(count, int(seed), radius)),
                   file_name="meshlab-simulation-report.json", mime="application/json")

tab1, tab2 = st.tabs(["Nodes", "Links"])
with tab1:
    st.dataframe(pd.DataFrame(nodes), hide_index=True, use_container_width=True)
with tab2:
    st.dataframe(pd.DataFrame(links), hide_index=True, use_container_width=True)
