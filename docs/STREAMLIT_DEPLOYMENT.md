# Deploy MeshLab to Streamlit Community Cloud

MeshLab is already a Streamlit app (`app.py`). The hosted deployment should run in **simulation-only** mode, because Community Cloud cannot access USB radios on your computer and should not be used to connect to private-network radios.

## Deployment steps

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Choose **Create app** → **Deploy a public app from GitHub**.
3. Select repository `JamalDaher/meshtastic-meshlab`, branch `main`, main file `app.py`.
4. Under **Advanced settings**, set Python to a supported 3.11+ version if offered.
5. Set environment variable `MESHLAB_SIMULATION_ONLY=1` in the app's settings/secrets environment if supported. If that option is unavailable, use the default simulation mode and do not enable live radio connections.
6. Deploy and open the resulting `*.streamlit.app` URL. Do not assume a particular subdomain until Cloud assigns it.
7. Test the topology, outage selector, scenario comparison, and JSON/CSV downloads on desktop and mobile.

## Safety and troubleshooting

- Do not add radio keys, Wi-Fi credentials, serial device paths or private IP addresses to the hosted app.
- Community Cloud hosts the simulation UI; live USB/TCP monitoring is intended only for local trusted installations.
- If imports fail, check `requirements.txt` and the app logs.
- If the app sleeps when unused, wake it by visiting its URL.
- To update the deployed app, merge changes into `main` and let Community Cloud redeploy.
