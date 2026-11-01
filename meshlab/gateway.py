"""Explicit, local-only serial radio gateway for read-only monitoring."""
from meshlab.monitor import Monitor

class SerialGateway:
    def __init__(self, monitor: Monitor):
        self.monitor = monitor
        self.interface = None
        self.callback = None

    def connect(self, port: str):
        if self.interface is not None:
            raise RuntimeError("Already connected")
        if not port or not port.strip():
            raise ValueError("Select a serial port")
        from meshlab.live import connect_serial
        interface, callback = connect_serial(port, self.monitor.ingest)
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
