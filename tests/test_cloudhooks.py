"""Test cloud cloudhooks."""
from unittest.mock import Mock

import pytest

from hass_nabucasa import cloudhooks

from .common import mock_coro


@pytest.fixture
def mock_cloudhooks(cloud_mock):
    """Mock cloudhooks class."""
    cloud_mock.run_executor = Mock(return_value=mock_coro())
    cloud_mock.iot = Mock(async_send_message=Mock(return_value=mock_coro()))
    cloud_mock.cloudhook_create_url = "https://webhook-create.url"
    return cloudhooks.Cloudhooks(cloud_mock)


async def test_enable(mock_cloudhooks, aioclient_mock):
    """Test enabling cloudhooks."""
    aioclient_mock.post(
        "https://webhook-create.url",
        json={
            "cloudhook_id": "mock-cloud-id",
            "url": "https://hooks.nabu.casa/ZXCZCXZ",
        },
    )

    hook = {
        "webhook_id": "mock-webhook-id",
        "cloudhook_id": "mock-cloud-id",
        "cloudhook_url": "https://hooks.nabu.casa/ZXCZCXZ",
    }

    assert hook == await mock_cloudhooks.async_create("mock-webhook-id")

    assert mock_cloudhooks.cloud.prefs.cloudhooks == {"mock-webhook-id": hook}

    publish_calls = mock_cloudhooks.cloud.iot.async_send_message.mock_calls
    assert len(publish_calls) == 1
    assert publish_calls[0][1][0] == "webhook-register"
    assert publish_calls[0][1][1] == {"cloudhook_ids": ["mock-cloud-id"]}


async def test_disable(mock_cloudhooks):
    """Test disabling cloudhooks."""
    mock_cloudhooks.cloud.prefs._prefs["cloudhooks"] = {
        "mock-webhook-id": {
            "webhook_id": "mock-webhook-id",
            "cloudhook_id": "mock-cloud-id",
            "cloudhook_url": "https://hooks.nabu.casa/ZXCZCXZ",
        }
    }

    await mock_cloudhooks.async_delete("mock-webhook-id")

    assert mock_cloudhooks.cloud.prefs.cloudhooks == {}

    publish_calls = mock_cloudhooks.cloud.iot.async_send_message.mock_calls
    assert len(publish_calls) == 1
    assert publish_calls[0][1][0] == "webhook-register"
    assert publish_calls[0][1][1] == {"cloudhook_ids": []}
