from json.decoder import JSONDecodeError
import requests
from requests.exceptions import HTTPError
import json
import os


class Flags(object):
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            self.set(k, v)

    def set(self, key, value):
        setattr(self, key, value)

    def _as_json(self):
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }


class Config(object):
    def __init__(
        self, endpoint=None, timeout=None,
        username=None, password=None,
    ) -> None:
        self.endpoint = (
            endpoint or os.getenv("RCLONERC_ENDPOINT") or "http://localhost:5572"
        )
        self.timeout = timeout or os.getenv("RCLONERC_TIMEOUT") or 3
        self.username = username or os.getenv("RCLONERC_USERNAME") or ""
        self.password = password or os.getenv("RCLONERC_PASSWORD") or ""


class Client(object):
    '''
    RClone RC Client
    '''
    def __init__(
        self, config: Config = None,
        global_flags: Flags = None,
        filters: Flags = None,
        group: str = None,
    ) -> None:
        self.config = config or Config()
        self.global_flags = global_flags or Flags()
        self.filters = filters or Flags()
        self.group = group or ""

    def _send_request(self, op: str, params: dict = {}, payload: dict = {}):
        '''
        HTTP request wrapper for rclonerc http interface
        '''
        final_global_flags = {
            **self.global_flags._as_json(),
            **payload.get("_config", {}),
        }
        if final_global_flags:
            payload["_config"] = final_global_flags

        final_filters = {
            **self.filters._as_json(),
            **payload.get("_config", {}),
        }
        if final_filters:
            payload["_filter"] = final_filters

        final_group = self.group or payload.get("_group", "")
        if final_group:
            payload['_group'] = final_group

        resp = requests.post(
            url=f"{self.config.endpoint}/{op}",
            params=params,
            json=payload,
            timeout=self.config.timeout,
            auth=(self.config.username, self.config.password)
        )
        try:
            body = resp.json()
        except JSONDecodeError:
            raise HTTPError(
                "Body is not valid JSON: "
                f"{resp.text}, status={resp.status_code}"
            )
        if "error" in body:
            raise HTTPError(
                f"{body['error']} on {body['path']}, "
                f"status={body['status']}, "
                f"input={json.dumps(body['input'])}"
            )
        return body

    def op(self, op, payload={}):
        return self._send_request(op, payload=payload)

    def default_global_flags(self) -> dict:
        return self.op("options/get")['main']

    def default_filters(self) -> dict:
        return self.op("options/get")['filter']
