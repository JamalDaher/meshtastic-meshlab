"""MeshLab interactive simulation dashboard."""
import os
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
from meshlab.recovery import recovery_options, recovery_sequence
from meshlab.dashboard import simulation_dashboard
from meshlab.rf import RadioProfile, link_budget

st.set_page_config(page_title="MeshLab", page_icon="📡", layout="wide")
st.title("📡 MeshLab")
st.caption("Explore simulated mesh connectivity, failures and recovery • privacy-first")
st.markdown("**[Open live app](https://meshlab.streamlit.app/) · [Source code](https://github.com/JamalDaher/meshtastic-meshlab) · Simulation data is illustrative, not measured RF performance.")
with st.sidebar:
    st.header("Workspace")
    hosted = os.environ.get("MESHLAB_SIMULATION_ONLY", "").lower() in {"1", "true", "yes"}
    modes = ["Simulation"] if hosted else ["Simulation", "Live radio (local only)"]
    mode = st.radio("Data source", modes)
    if hosted:
        st.caption("Hosted demo: simulation only. Connect physical radios using a local installation.")
    if mode == "Simulation":
        with st.expander("Simulation settings", expanded=False):
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
st.subheader("Simulation at a glance")
failed_names = st.multiselect("Offline nodes (applies to all workspace tabs)",
                              [n["name"] for n in nodes], key="offline_nodes",
                              help="Change this to update topology, routes, resilience, and dashboard together.")
failed_ids = [n["node_id"] for n in nodes if n["name"] in failed_names]
overlay = outage_overlay(data, failed_ids)
offline_ids = set(overlay["offline_nodes"])
dashboard = simulation_dashboard(data, failed_ids)
a, b, c, d = st.columns(4)
a.metric("Online nodes", f"{dashboard['online_nodes']} / {dashboard['total_nodes']}")
b.metric("Active links", dashboard["active_links"])
c.metric("Connected groups", dashboard["connected_groups"])
d.metric("Largest group", f"{dashboard['largest_group_pct']:.0f}%")
with st.expander("Connectivity and vulnerability details"):
    st.caption("Largest group percentage is the share of online nodes in the largest connected component.")
    st.write(f"Offline nodes: {dashboard['offline_nodes']} · Critical nodes: {dashboard['critical_nodes']} · Bridge links: {dashboard['bridge_links']}")
    st.caption("Graph metrics are synthetic and do not predict actual RF performance.")

workspace_network, workspace_resilience, workspace_analysis, workspace_scenarios = st.tabs(
    ["🕸️ Network", "🛡️ Resilience", "📈 Analysis", "💾 Scenarios"]
)

with workspace_network:
    with st.expander("RF link budget explorer · ideal free space", expanded=False):
        st.caption("Independent analytical estimate; does not change synthetic topology or LoRa packet-delivery behavior.")
        rf1, rf2 = st.columns(2)
        with rf1:
            frequency = st.number_input("Frequency (MHz)", min_value=1.0, max_value=10000.0, value=906.875, step=0.125)
            tx_power = st.number_input("Transmit power (dBm)", min_value=-30.0, max_value=40.0, value=22.0)
            distance = st.number_input("Link distance (km)", min_value=0.001, max_value=1000.0, value=1.0)
        with rf2:
            tx_gain = st.number_input("Transmit antenna gain (dBi)", min_value=-20.0, max_value=40.0, value=2.0)
            rx_gain = st.number_input("Receive antenna gain (dBi)", min_value=-20.0, max_value=40.0, value=2.0)
            cable_loss = st.number_input("Total cable loss (dB)", min_value=0.0, max_value=100.0, value=0.0)
            sensitivity = st.number_input("Receiver sensitivity (dBm)", min_value=-160.0, max_value=-50.0, value=-130.0)
        rf_profile = RadioProfile(frequency_mhz=frequency, tx_power_dbm=tx_power,
                                  tx_gain_dbi=tx_gain, rx_gain_dbi=rx_gain,
                                  cable_loss_db=cable_loss, receiver_sensitivity_dbm=sensitivity)
        budget = link_budget(distance, rf_profile)
        rf_a, rf_b, rf_c = st.columns(3)
        rf_a.metric("Free-space loss", f"{budget['path_loss_db']:.1f} dB")
        rf_b.metric("Received power", f"{budget['received_power_dbm']:.1f} dBm")
        rf_c.metric("Link margin", f"{budget['link_margin_db']:+.1f} dB")
        st.caption("Ideal unobstructed line-of-sight estimate only. Terrain, fading, polarization, interference, regional rules, and LoRa settings are not modeled.")
    st.subheader("Network overview")
    st.caption("Use the outage selector to explore how failures affect the topology. Orange outlines mark graph weak points.")
    st.caption(f"Active topology: {len(overlay['online_nodes'])} nodes, {len(overlay['active_links'])} links, {overlay['state']['components']} connected groups.")
    node_by_id = {n["node_id"]: n for n in nodes}
    fig = go.Figure()
    weak = weak_points(data)
    highlight_weak = st.toggle("Highlight critical nodes and bridge links", value=True)
    show_labels = st.toggle("Show node labels", value=True)
    show_route = st.toggle("Highlight selected route", value=True)
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
        mode="markers+text" if show_labels else "markers", text=[n["name"] for n in nodes],
        textposition="top center", customdata=[[n["node_id"], n["battery"]] for n in nodes],
        marker=dict(size=[23 if n["node_id"] in critical_ids and n["node_id"] not in offline_ids else 16 for n in nodes],
                    color=[n["battery"] if n["node_id"] not in offline_ids else -1 for n in nodes],
                    colorscale=[[0, "#888888"], [0.01, "#440154"], [0.25, "#3b528b"], [0.5, "#21918c"], [0.75, "#5ec962"], [1, "#fde725"]],
                    cmin=-1, cmax=100, showscale=False,
                    line=dict(width=[3 if n["node_id"] in critical_ids and n["node_id"] not in offline_ids else 1 for n in nodes],
                              color=["#ff9f43" if n["node_id"] in critical_ids and n["node_id"] not in offline_ids else "#d8e5ef" for n in nodes])),
        hovertemplate="%{text}<br>ID: %{customdata[0]}<br>Battery: %{customdata[1]}%<extra></extra>",
        showlegend=False))
    fig.update_layout(template="plotly_dark", height=470, margin=dict(l=5,r=5,t=5,b=5),
                      xaxis=dict(title="Synthetic X", range=[-0.5, 10.5]),
                      yaxis=dict(title="Synthetic Y", range=[-0.5, 10.5],
                                 scaleanchor="x", scaleratio=1))
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": False})
    st.caption("Synthetic coordinates and illustrative links; this is not a geographic map or validated RF model.")
    st.caption("Grey nodes are offline in the selected scenario; only active links are drawn.")
    st.caption(f"Graph weak points: {weak['critical_node_count']} critical node(s), {weak['bridge_link_count']} bridge link(s). Orange highlights show graph vulnerabilities, not measured RF risk.")

    st.divider()
    st.subheader("Route explorer")
    names = {n["name"]: n["node_id"] for n in nodes}
    left, right = st.columns(2)
    with left:
        source_name = st.selectbox("Source node", list(names))
    with right:
        target_name = st.selectbox("Destination node", list(names), index=len(names)-1)
    active_graph = graph.copy()
    active_graph.remove_nodes_from(offline_ids)
    source_id, target_id = names[source_name], names[target_name]
    route = (shortest_route(active_graph, source_id, target_id)
             if source_id in active_graph and target_id in active_graph else None)
    if source_id in offline_ids or target_id in offline_ids:
        st.warning("A selected endpoint is offline. Restore it to calculate a route.")
    elif route is None:
        st.warning("No active route exists between these nodes with the selected outages and range.")
    else:
        id_to_name = {v:k for k,v in names.items()}
        st.success(" → ".join(id_to_name[n] for n in route))
        if show_route and len(route) > 1:
            route_x = [node_by_id[node]["x"] for node in route]
            route_y = [node_by_id[node]["y"] for node in route]
            route_fig = go.Figure()
            route_fig.add_trace(go.Scatter(x=route_x, y=route_y, mode="lines+markers+text",
                text=[id_to_name[node] for node in route], textposition="top center",
                line=dict(color="#ffca65", width=4), marker=dict(size=12, color="#ffca65"),
                hovertemplate="%{text}<extra></extra>"))
            route_fig.update_layout(template="plotly_dark", height=260,
                margin=dict(l=5,r=5,t=5,b=5), showlegend=False,
                xaxis=dict(range=[-0.5, 10.5], title="Synthetic X"),
                yaxis=dict(range=[-0.5, 10.5], title="Synthetic Y", scaleanchor="x", scaleratio=1))
            st.plotly_chart(route_fig, use_container_width=True, config={"displaylogo": False})
        st.caption(f"{len(route)-1} simulated hop(s); routing is shortest-hop graph analysis, "
                   "not a reproduction of Meshtastic firmware routing.")

with workspace_resilience:
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

    st.divider()
    st.subheader("Network recovery planner")
    st.caption("Rank offline nodes by the increase in largest connected group if restored. Greedy graph planning, not a prediction of actual radio recovery.")
    if failed_ids:
        recovery_rows = recovery_options(data, failed_ids)
        if recovery_rows:
            best = recovery_rows[0]
            st.success(f"Restore {id_to_label[best['node_id']]} first: largest connected group gains {best['largest_group_gain']} node(s).")
            st.dataframe(pd.DataFrame(recovery_rows).assign(
                node=lambda df: df["node_id"].map(id_to_label)),
                hide_index=True, use_container_width=True)
            sequence_df = pd.DataFrame(recovery_sequence(data, failed_ids))
            st.write("Suggested step-by-step recovery order")
            st.dataframe(sequence_df.assign(node=sequence_df["node_id"].map(id_to_label)),
                         hide_index=True, use_container_width=True)
            st.download_button("Export recovery sequence CSV", sequence_df.to_csv(index=False),
                               file_name="meshlab-recovery-sequence.csv", mime="text/csv")
    else:
        st.info("Select one or more offline nodes above to see recovery priorities.")

with workspace_analysis:
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

    st.divider()
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

with workspace_scenarios:
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

    st.divider()
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
