from urllib.parse import urljoin
from typing import Optional, Any
import time
import os

from prometheus_client import start_http_server, Summary, Gauge
import requests


class TFLBikePointRequest:
    ENDPOINT = "https://api.tfl.gov.uk/BikePoint/"

    def __init__(self, api_key: str, bikepoint_id: str) -> None:
        self.stats = ["available", "total", "empty", "broken"]
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
    def available(self) -> Optional[int]:
        return self._add_prop_by_key("NbBikes")

    @property
    def total(self) -> Optional[int]:
        return self._add_prop_by_key("NbDocks")

    @property
    def empty(self) -> Optional[int]:
        return self._add_prop_by_key("NbEmptyDocks")

    @property
    def broken(self) -> Optional[int]:
        if all([self.total, self.empty, self.available]):
            return self.total - self.empty - self.available
        return None

    def _add_prop_by_key(self, key: str) -> Optional[int]:
        assert self.response, "Make a request first"
        add_props = self.response["additionalProperties"]
        select = [prop for prop in add_props if prop["key"] == key]
        if select:
            return int(select[0]["value"])
        return None


REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")
DOCK_STATS = Gauge("tfl_dock_stat", "Bikepoint dock statistic", ["stat"])


@REQUEST_TIME.time()
def do_tfl_get_request(req: TFLBikePointRequest) -> None:
    req.get()
    for stat in req.stats:
        dock_stat = getattr(req, stat)
        if dock_stat:
            DOCK_STATS.labels(stat=stat).set(dock_stat)


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
