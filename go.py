from urllib.parse import urljoin
from typing import Optional, Any
import time
import os

from prometheus_client import start_http_server, Summary, Gauge
import requests


class TFLBikePointRequest:
    ENDPOINT = "https://api.tfl.gov.uk/BikePoint/"

    def __init__(self, app_key: str, id: str) -> None:
        self.params = {"app_key": app_key}
        self.id = id
        self.response: Optional[dict[str, Any]] = None

    def get(self) -> None:
        _req = requests.get(
            urljoin(self.ENDPOINT, self.id),
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
    from dotenv import load_dotenv

    load_dotenv()

    APP_KEY = os.environ.get("APP_KEY")
    ID = "BikePoints_73"
    BUFFER = 10

    req = TFLBikePointRequest(app_key=APP_KEY,
                              id=ID)
    start_http_server(8000)
    while True:
        do_tfl_get_request(req)
        time.sleep(BUFFER)
