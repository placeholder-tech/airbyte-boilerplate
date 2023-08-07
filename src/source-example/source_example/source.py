import logging
from typing import Mapping, Any, Tuple, Optional, List, MutableMapping, Iterable

import pendulum
import requests as requests
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator


class BaseStream(HttpStream, IncrementalMixin):
    def __init__(self, authenticator: BasicHttpAuthenticator, base_url: str, **kwargs):
        HttpStream.__init__(self, authenticator=authenticator)
        self._base_url = base_url
        self._authenticator = authenticator


class ExampleStream(BaseStream):
    state_checkpoint_interval = 100
    cursor_value = pendulum.parse("2023-01-01")
    cursor_field = "updated_at"
    primary_key = "uid"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 0
        self.page_size = 25

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {
            self.cursor_field: self.cursor_value.isoformat(),
        }

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self.cursor_value = pendulum.parse(value[self.cursor_field])

    @property
    def url_base(self):
        return self._base_url + "/"

    def path(self, **kwargs) -> str:
        return f"orders"

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if len(data) == self.page_size:
            self.page += 1

            return {"page": self.page}

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        headers = dict(
            Accept="application/json", **self._authenticator.get_auth_header()
        )
        return headers

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        params["since"] = self.cursor_value.isoformat().split("T")[0]
        params["page"] = 0
        if next_page_token:
            params["page"] = next_page_token["page"]
        return params

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        result = response.json()

        for rec in result:
            yield rec

        if len(result) < self.page_size:
            return None

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        latest_record_cursor = latest_record.get(self.cursor_field)
        latest_record_value = pendulum.parse(latest_record_cursor)

        if self.cursor_value.diff(latest_record_value).in_days() > 1:
            self.cursor_value = latest_record_value

        return {
            self.cursor_field: self.cursor_value,
        }


class ExampleSource(AbstractSource):
    def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, Optional[Any]]:
        auth = BasicHttpAuthenticator(config["username"], config["password"])
        base_url = config["api_base_url"]
        headers = dict(Accept="application/json", **auth.get_auth_header())
        session = requests.get(base_url + "/test", headers=headers)
        session.raise_for_status()
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = BasicHttpAuthenticator(config["username"], config["password"])
        base_url = config["api_base_url"]
        return [ExampleStream(authenticator=auth, base_url=base_url)]
