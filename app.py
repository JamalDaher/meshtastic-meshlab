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
from meshlab.rf_simulator import simulate_rf
from meshlab.rf_coverage import margin_color, margin_category, coverage_summary
from meshlab.rf_exports import encode_rf_scenario, decode_rf_scenario, build_rf_report
from meshlab.geo import geographic_links, validate_nodes
from meshlab.coverage import theoretical_radius_km, coverage_ring
from meshlab.terrain import analyze_terrain_profile
from meshlab.elevation import sample_geographic_path, fetch_elevations

def apply_rf_preset(settings):
    """Button callback runs before widget construction on the next rerun."""
    profile = settings["profile"]
    st.session_state["sim_count"] = settings["count"]
    st.session_state["sim_seed"] = settings["seed"]
    st.session_state["connectivity_mode"] = "Ideal free-space RF"
    st.session_state["km_per_unit"] = settings["km_per_unit"]
    for key, field in (
        ("rf_frequency", "frequency_mhz"), ("rf_tx_power", "tx_power_dbm"),
        ("rf_sensitivity", "receiver_sensitivity_dbm"),
        ("rf_tx_gain", "tx_gain_dbi"), ("rf_rx_gain", "rx_gain_dbi"),
        ("rf_cable_loss", "cable_loss_db")
    ):
        st.session_state[key] = float(profile[field])
    st.session_state["rf_preset_applied"] = True

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
            count = st.slider("Virtual nodes", 2, 30, 10, key="sim_count")
            seed = st.number_input("Simulation seed", 0, 100000, 42, key="sim_seed")
            connectivity_mode = st.radio("Connectivity model", ["Distance threshold", "Ideal free-space RF"], key="connectivity_mode")
            if connectivity_mode == "Distance threshold":
                radius = st.slider("Illustrative radio range", 1.0, 10.0, 5.0, 0.5)
            else:
                km_per_unit = st.number_input("Kilometers per synthetic coordinate unit",
                                              min_value=0.01, max_value=100.0, value=0.5, key="km_per_unit")
                rf_frequency = st.number_input("RF frequency (MHz)", 1.0, 10000.0, 906.875, key="rf_frequency")
                rf_tx_power = st.number_input("RF transmit power (dBm)", -30.0, 40.0, 22.0, key="rf_tx_power")
                rf_sensitivity = st.number_input("RF receiver sensitivity (dBm)", -160.0, -50.0, -130.0, key="rf_sensitivity")
                rf_tx_gain = st.number_input("RF TX antenna gain (dBi)", -20.0, 40.0, 2.0, key="rf_tx_gain")
                rf_rx_gain = st.number_input("RF RX antenna gain (dBi)", -20.0, 40.0, 2.0, key="rf_rx_gain")
                rf_cable_loss = st.number_input("RF total cable loss (dB)", 0.0, 100.0, 0.0, key="rf_cable_loss")
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

radius = 5.0  # Legacy distance-model scenario and report tools retain their own range.
if connectivity_mode == "Ideal free-space RF":
    profile = RadioProfile(frequency_mhz=rf_frequency, tx_power_dbm=rf_tx_power,
                           tx_gain_dbi=rf_tx_gain, rx_gain_dbi=rf_rx_gain,
                           cable_loss_db=rf_cable_loss, receiver_sensitivity_dbm=rf_sensitivity)
    data = simulate_rf(count, int(seed), km_per_unit, profile)
    st.caption("Connectivity: ideal free-space RF threshold. Synthetic coordinate spacing is scaled to km; no terrain, fading, or LoRa packet modeling.")
    st.info("Timeline, range comparisons, saved scenarios and JSON report still use the legacy distance model. RF settings are not included in those exports yet.")
else:
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
    color_by_margin = connectivity_mode == "Ideal free-space RF" and st.toggle("Color links by RF margin", value=True)
    if color_by_margin:
        margin_counts = coverage_summary(overlay["active_links"])
        st.caption(f"RF margins: {margin_counts['high margin']} high (≥15 dB), {margin_counts['moderate margin']} moderate (6–15 dB), {margin_counts['low margin']} low (0–6 dB). Below-sensitivity links are absent.")
    for link in overlay["active_links"]:
        src, dst = node_by_id[link["source"]], node_by_id[link["target"]]
        is_bridge = tuple(sorted((link["source"], link["target"]))) in bridge_links
        fig.add_trace(go.Scatter(
            x=[src["x"], dst["x"]], y=[src["y"], dst["y"]],
            mode="lines", line=dict(width=3.5 if is_bridge else 1.8,
                                    color=margin_color(link["link_margin_db"]) if color_by_margin else "#ff9f43" if is_bridge else "#4f8fa5"),
            hoverinfo="text" if color_by_margin else "skip",
            text=(f"RF margin: {link['link_margin_db']:.1f} dB · {margin_category(link['link_margin_db'])}") if color_by_margin else None,
            showlegend=False))
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
    if connectivity_mode == "Ideal free-space RF" and links:
        st.dataframe(pd.DataFrame(links)[["source", "target", "distance_km", "path_loss_db", "rssi", "link_margin_db"]], hide_index=True, use_container_width=True)
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
    if connectivity_mode == "Ideal free-space RF":
        from dataclasses import asdict
        rf_settings = {"count": count, "seed": int(seed), "km_per_unit": km_per_unit,
                       "profile": asdict(profile)}
        st.subheader("RF scenario and report exports")
        st.caption("These exports include the active ideal RF settings and calculated RF topology.")
        st.download_button("Save RF scenario JSON", encode_rf_scenario(rf_settings),
                           file_name="meshlab-rf-scenario.json", mime="application/json")
        st.download_button("Download RF simulation report JSON",
                           export_json(build_rf_report(rf_settings)),
                           file_name="meshlab-rf-report.json", mime="application/json")
        rf_uploaded = st.file_uploader("Inspect saved RF scenario", type=["json"], key="rf_scenario_upload")
        if rf_uploaded is not None:
            try:
                restored = decode_rf_scenario(rf_uploaded.getvalue().decode("utf-8"))
                st.success("Valid RF scenario.")
                st.json(restored)
                if restored["count"] > 30:
                    st.warning("This preset exceeds the dashboard limit of 30 nodes and cannot be applied here.")
                else:
                    st.button("Apply RF scenario to simulation", on_click=apply_rf_preset,
                              args=(restored,), type="primary")
            except (ValueError, UnicodeError) as exc:
                st.error(f"Invalid RF scenario: {exc}")
        if st.session_state.pop("rf_preset_applied", False):
            st.success("RF scenario settings applied to the simulator.")
        st.divider()
    st.subheader("Scenario planner")
    st.caption("Legacy distance-model scenario tools are shown below. RF presets and reports are separate and versioned.")
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

    st.divider()
    st.subheader("Geographic RF planner · v1.3 preview")
    st.caption("Enter real latitude/longitude for proposed nodes. This is a separate planning tool, not a replacement for the synthetic topology.")
    if "geo_nodes" not in st.session_state:
        st.session_state.geo_nodes = pd.DataFrame([
            {"name": "Site A", "lat": 34.25, "lon": -88.40},
            {"name": "Site B", "lat": 34.26, "lon": -88.39},
        ])
    edited_geo = st.data_editor(st.session_state.geo_nodes, num_rows="dynamic",
                                use_container_width=True, key="geo_editor")
    geo_frequency = st.number_input("Geographic RF frequency (MHz)", 1.0, 10000.0, 906.875, key="geo_frequency")
    geo_tx_power = st.number_input("Geographic RF TX power (dBm)", -30.0, 40.0, 22.0, key="geo_tx_power")
    geo_sensitivity = st.number_input("Geographic RF sensitivity (dBm)", -160.0, -50.0, -130.0, key="geo_sensitivity")
    geo_tx_gain = st.number_input("Geographic TX gain (dBi)", -20.0, 40.0, 2.0, key="geo_tx_gain")
    geo_rx_gain = st.number_input("Geographic RX gain (dBi)", -20.0, 40.0, 2.0, key="geo_rx_gain")
    geo_loss = st.number_input("Geographic cable loss (dB)", 0.0, 100.0, 0.0, key="geo_loss")
    try:
        geo_nodes = validate_nodes(edited_geo.to_dict("records"))
        geo_profile = RadioProfile(frequency_mhz=geo_frequency, tx_power_dbm=geo_tx_power,
                                   receiver_sensitivity_dbm=geo_sensitivity, tx_gain_dbi=geo_tx_gain,
                                   rx_gain_dbi=geo_rx_gain, cable_loss_db=geo_loss)
        geo_links = geographic_links(geo_nodes, geo_profile)
        geo_by_name = {n["name"]: n for n in geo_nodes}
        geo_fig = go.Figure()
        show_coverage = st.toggle("Show theoretical coverage rings", value=False, key="geo_show_coverage")
        reserve_margin = st.slider("Coverage reserve margin (dB)", 0, 30, 10, 1, key="geo_reserve_margin",
                                   disabled=not show_coverage)
        if show_coverage:
            radius_km = theoretical_radius_km(geo_profile, reserve_margin)
            st.caption(f"Ideal free-space sensitivity radius: {radius_km:,.1f} km per node with {reserve_margin} dB reserve. This is not a reliable coverage forecast.")
            if radius_km > 100:
                st.warning("Radius exceeds 100 km. Rings are hidden at this scale to avoid misleading regional coverage displays.")
            else:
                for geo_node in geo_nodes:
                    ring = coverage_ring(geo_node["lat"], geo_node["lon"], radius_km)
                    geo_fig.add_trace(go.Scattermapbox(
                        lat=[p[0] for p in ring], lon=[p[1] for p in ring],
                        mode="lines", line=dict(width=1, color="#64748b"),
                        hoverinfo="text", text=[f"{geo_node['name']}: ideal {radius_km:.1f} km radius"] * len(ring),
                        showlegend=False))
        show_below = st.toggle("Show below-sensitivity links", value=False, key="geo_show_below")
        for geo_link in geo_links:
            if not geo_link["above_sensitivity"] and not show_below:
                continue
            start = geo_by_name[geo_link["source"]]
            end = geo_by_name[geo_link["target"]]
            margin = geo_link["link_margin_db"]
            geo_fig.add_trace(go.Scattermapbox(
                lat=[start["lat"], end["lat"]], lon=[start["lon"], end["lon"]],
                mode="lines",
                line=dict(width=3, color=margin_color(margin)),
                hoverinfo="text",
                text=[f"{geo_link['source']} → {geo_link['target']}: {geo_link['distance_km']:.2f} km, {margin:+.1f} dB margin"] * 2,
                showlegend=False))
        geo_fig.add_trace(go.Scattermapbox(
            lat=[n["lat"] for n in geo_nodes], lon=[n["lon"] for n in geo_nodes],
            mode="markers+text", text=[n["name"] for n in geo_nodes],
            textposition="top right", marker=dict(size=13, color="#3178c6"),
            hoverinfo="text", hovertext=[n["name"] for n in geo_nodes],
            showlegend=False))
        geo_fig.update_layout(
            mapbox=dict(style="open-street-map",
                        center=dict(lat=sum(n["lat"] for n in geo_nodes) / len(geo_nodes),
                                    lon=sum(n["lon"] for n in geo_nodes) / len(geo_nodes)),
                        zoom=10),
            margin=dict(l=0, r=0, t=0, b=0), height=470)
        st.plotly_chart(geo_fig, use_container_width=True)
        st.caption("Link colors: teal ≥15 dB, amber 6–15 dB, red 0–6 dB, gray below sensitivity. Zoom and pan the map to inspect nodes.")
        st.write("Estimated pairwise geographic links")
        st.dataframe(pd.DataFrame(geo_links), hide_index=True, use_container_width=True)
        st.download_button("Export geographic links CSV", pd.DataFrame(geo_links).to_csv(index=False),
                           file_name="meshlab-geographic-links.csv", mime="text/csv")
        st.caption("Links and optional rings are ideal free-space estimates, not measured links or guaranteed coverage. Terrain, obstruction, fading and interference are not modeled.")
    except (ValueError, TypeError) as exc:
        st.warning(f"Geographic planner: {exc}")

    with st.expander("Terrain line-of-sight profile · v1.3 preview"):
        st.caption("Paste sampled ground elevations (distance_km,elevation_m). This does not download terrain data.")
        st.caption("Optional: select two geographic nodes and request elevations from Open-Meteo. Node coordinates will be sent to that service.")
        if "geo_nodes" in st.session_state:
            node_names = [n["name"] for n in geo_nodes] if "geo_nodes" in locals() else []
            if len(node_names) >= 2:
                terrain_start = st.selectbox("Elevation path start", node_names, index=0, key="terrain_start")
                terrain_end = st.selectbox("Elevation path end", node_names, index=1, key="terrain_end")
                terrain_points = st.slider("Elevation sample points", 2, 100, 21, key="terrain_points")
                if st.button("Fetch elevation profile", key="terrain_fetch"):
                    try:
                        start_node = next(n for n in geo_nodes if n["name"] == terrain_start)
                        end_node = next(n for n in geo_nodes if n["name"] == terrain_end)
                        path = sample_geographic_path(start_node["lat"], start_node["lon"],
                                                      end_node["lat"], end_node["lon"], terrain_points)
                        elevations = fetch_elevations(path)
                        st.session_state["terrain_samples"] = "\n".join(
                            f"{distance:.6f},{height:.2f}" for distance, height in elevations)
                        st.success("Elevation samples loaded. Review the profile below.")
                    except (ValueError, OSError, TimeoutError) as exc:
                        st.error(f"Elevation lookup failed: {exc}")
        profile_csv = st.text_area("Elevation samples (km, meters above sea level)",
                                   value="0,100\\n0.5,100\\n1,100", key="terrain_samples")
        tx_h = st.number_input("TX antenna height above ground (m)", 0.0, 1000.0, 5.0, key="terrain_tx_height")
        rx_h = st.number_input("RX antenna height above ground (m)", 0.0, 1000.0, 5.0, key="terrain_rx_height")
        try:
            terrain_samples = []
            for line in profile_csv.splitlines():
                if line.strip():
                    fields = line.split(",")
                    if len(fields) != 2:
                        raise ValueError("Each line must contain distance_km,elevation_m")
                    terrain_samples.append((float(fields[0]), float(fields[1])))
            terrain_result = analyze_terrain_profile(terrain_samples, tx_h, rx_h)
            st.metric("Minimum interior terrain clearance", f"{terrain_result['minimum_interior_clearance_m']:.1f} m")
            st.write("Geometric line of sight:", "Clear" if terrain_result["clear_line_of_sight"] else "Obstructed")
            profile_df = pd.DataFrame(terrain_result["samples"])
            st.line_chart(profile_df.set_index("distance_km")[["terrain_elevation_m", "sightline_elevation_m"]])
            st.dataframe(profile_df, hide_index=True, use_container_width=True)
            st.caption("Earth curvature uses an approximate 4/3 effective Earth radius. Clearance calculations include curvature, while the simple line chart does not plot the curvature bulge. Fresnel clearance and clutter are not modeled.")
        except (ValueError, TypeError) as exc:
            st.warning(f"Invalid terrain profile: {exc}")

    tab1, tab2 = st.tabs(["Nodes", "Links"])
    with tab1:
        st.dataframe(pd.DataFrame(nodes), hide_index=True, use_container_width=True)
    with tab2:
        st.dataframe(pd.DataFrame(links), hide_index=True, use_container_width=True)
