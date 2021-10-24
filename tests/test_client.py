import pytest

from rclonerc.client import Config, Client, HTTPError


@pytest.fixture
def c():
    return Client(
        Config(timeout=1, username="devuser", password="devpassword")
    )


def test_noop(c: Client):
    resp = c.op("rc/noop", {"k": "v"})
    assert resp["k"] == "v"


def test_noauth(c: Client):
    c.config = Config()
    with pytest.raises(HTTPError) as e:
        c.op("rc/noop")
    assert "Unauthorized" in str(e.value)
