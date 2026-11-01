"""Explicit local-only serial and TCP radio gateways."""
from meshlab.monitor import Monitor

class RadioGateway:
    def __init__(self, monitor: Monitor):
        self.monitor = monitor
        self.interface = None
        self.callback = None

    def connect(self, target: str, transport: str = "serial"):
        if self.interface is not None:
            raise RuntimeError("Already connected")
        if not target or not target.strip():
            raise ValueError("Select a port or private IP address")
        from meshlab.live import connect_serial, connect_tcp
        if transport == "serial":
            connector = connect_serial
        elif transport == "tcp":
            connector = connect_tcp
        else:
            raise ValueError("Unsupported transport")
        interface, callback = connector(target, self.monitor.ingest)
        self.interface, self.callback = interface, callback

    def disconnect(self):
        if self.interface is None:
            return
        from meshlab.live import disconnect_serial
        interface, callback = self.interface, self.callback
        self.interface = self.callback = None
        disconnect_serial(interface, callback)

    @property
    def connected(self):
        return self.interface is not None

class SerialGateway(RadioGateway):
    def connect(self, port: str):
        return super().connect(port, "serial")
