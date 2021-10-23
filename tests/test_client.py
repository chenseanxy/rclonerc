from rclonerc import Client


def test_get_client():
    c = Client()
    assert c
