from urllib.parse import urljoin
from typing import Optional, Any
import time
import os

from prometheus_client import start_http_server, Summary, Gauge
import requests


class TFLBikePointRequest:
    ENDPOINT = "https://api.tfl.gov.uk/BikePoint/"

    def __init__(self, api_key: str, bikepoint_id: str) -> None:
        self.params = {"app_key": api_key}
        self.bikepoint_id = bikepoint_id
        self.response: Optional[dict[str, Any]] = None

    def get(self) -> None:
        _req = requests.get(
            urljoin(self.ENDPOINT, self.bikepoint_id),
            params=self.params
        )
        self.response = _req.json()

    @property
    def bikes(self) -> Optional[int]:
        return self._add_prop_by_key("NbBikes")

    @property
    def total_docks(self) -> Optional[int]:
        return self._add_prop_by_key("NbDocks")

    @property
    def empty_docks(self) -> Optional[int]:
        return self._add_prop_by_key("NbEmptyDocks")

    @property
    def broken_docks(self) -> Optional[int]:
        if all([self.total_docks, self.empty_docks, self.bikes]):
            return self.total_docks - self.empty_docks - self.bikes
        return None

    def _add_prop_by_key(self, key: str) -> Optional[int]:
        assert self.response, "Make a request first"
        add_props = self.response["additionalProperties"]
        select = [prop for prop in add_props if prop["key"] == key]
        if select:
            return int(select[0]["value"])
        return None


REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")
GAUGES = {
    "bikes": Gauge("bikes", "Number of bikes"),
    "total_docks": Gauge("total_docks", "Total number of docks"),
    "empty_docks": Gauge("empty_docks", "Number of empty docks"),
    "broken_docks": Gauge("broken_docks", "Number of broken docks")
}


@REQUEST_TIME.time()
def do_tfl_get_request(req: TFLBikePointRequest) -> None:
    req.get()
    for key, gauge in GAUGES.items():
        dock_stat = getattr(req, key)
        if dock_stat:
            gauge.set(dock_stat)


if __name__ == "__main__":
    api_key = os.environ.get("API_KEY")
    bikepoint_id = os.environ.get("BIKEPOINT_ID")
    server_port = int(os.environ.get("SERVER_PORT"))
    request_buffer = int(os.environ.get("REQUEST_BUFFER"))

    req = TFLBikePointRequest(api_key=api_key,
                              bikepoint_id=bikepoint_id)
    start_http_server(server_port)

    while True:
        do_tfl_get_request(req)
        time.sleep(request_buffer)
