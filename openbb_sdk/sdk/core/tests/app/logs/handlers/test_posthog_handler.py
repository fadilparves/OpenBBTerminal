from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.logs.handlers.posthog_handler import (
    PosthogHandler,
)
import logging


class MockLoggingSettings:
    def __init__(
        self,
        app_name,
        user_logs_directory,
        session_id,
        frequency,
        appid,
        commit_hash,
        platform,
        python_version,
        terminal_version,
        branch,
        userid,
    ):
        self.app_name = app_name
        self.user_logs_directory = Path(user_logs_directory)
        self.session_id = session_id
        self.frequency = frequency
        self.app_id = appid
        self.commit_hash = commit_hash
        self.platform = platform
        self.python_version = python_version
        self.terminal_version = terminal_version
        self.branch = branch
        self.user_id = userid


logging_settings = MagicMock(spec=MockLoggingSettings)
logging_settings.app_name = "TestApp"
logging_settings.user_logs_directory = MagicMock()
logging_settings.user_logs_directory.absolute.return_value = Path(
    "/mocked/logs/directory"
)
logging_settings.session_id = "session123"
logging_settings.frequency = "H"
logging_settings.app_id = "test123"
logging_settings.commit_hash = "commit123"
logging_settings.platform = "Windows"
logging_settings.python_version = "3.9"
logging_settings.terminal_version = "1.2.3"
logging_settings.branch = "main"
logging_settings.user_id = "user123"


@pytest.fixture
def handler():
    return PosthogHandler(logging_settings)


def test_emit_calls_send(mocker, handler):
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=None,
        exc_info=None,
    )

    # Mock the send method
    handler.send = mocker.MagicMock()

    # Act
    handler.emit(record)

    # Assert
    handler.send.assert_called_once_with(record=record)


def test_emit_calls_handleError_when_send_raises_exception(mocker, handler):
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=42,
        msg="Test error message",
        args=None,
        exc_info=None,
    )

    # Mock the send method to raise an exception
    handler.send = mocker.MagicMock(side_effect=Exception)

    # Mock the handleError method
    handler.handleError = mocker.MagicMock()

    # Act
    handler.emit(record)

    # Assert
    handler.send.assert_called_once_with(record=record)
    handler.handleError.assert_called_once_with(record)


def test_emit_calls_handleError_when_send_raises_exception_of_specific_type(
    mocker, handler
):
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=42,
        msg="Test error message",
        args=None,
        exc_info=None,
    )

    # Mock the send method to raise an exception of a specific type
    handler.send = mocker.MagicMock(side_effect=ValueError)

    # Mock the handleError method
    handler.handleError = mocker.MagicMock()

    # Act
    handler.emit(record)

    # Assert
    handler.send.assert_called_once_with(record=record)
    handler.handleError.assert_called_once_with(record)


def test_emit_calls_handleError_when_send_raises_exception_of_another_type(
    mocker, handler
):
    # Arrange
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=42,
        msg="Test error message",
        args=None,
        exc_info=None,
    )

    # Mock the send method to raise an exception of another type
    handler.send = mocker.MagicMock(side_effect=TypeError)

    # Mock the handleError method
    handler.handleError = mocker.MagicMock()

    # Act
    handler.emit(record)

    # Assert
    handler.send.assert_called_once_with(record=record)
    handler.handleError.assert_called_once_with(record)


@pytest.mark.parametrize(
    "log_info, expected_dict",
    [
        (
            'STARTUP: {"status": "success"}',
            {"STARTUP": {"status": "success"}},
        ),
        (
            '{"INPUT": {"something_something":"something_something"}}',
            {
                "SDK": {"INPUT": {"something_something": "something_something"}},
            },
        ),
        (
            'CMD: {"path": "/stocks/", "known_cmd": "load", "other_args": "aapl", "input": "load aapl"}',
            {
                "CMD": {
                    "path": "/stocks/",
                    "known_cmd": "load",
                    "other_args": "aapl",
                    "input": "load aapl",
                }
            },
        ),
    ],
)
def test_log_to_dict(handler, log_info, expected_dict):
    # Act
    result = handler.log_to_dict(log_info)

    # Assert
    assert result == expected_dict


@pytest.mark.parametrize(
    "record, expected_extra",
    [
        (
            logging.LogRecord(
                "name", logging.INFO, "pathname", 42, "message", (), None, None
            ),
            {
                "appName": "TestApp",
                "appId": "test123",
                "sessionId": "session123",
                "commitHash": "commit123",
                "platform": "Windows",
                "pythonVersion": "3.9",
                "terminalVersion": "1.2.3",
                "branch": "main",
                "userId": "user123",
            },
        ),
    ],
)
def test_extract_log_extra(handler, record, expected_extra):
    # Act
    result = handler.extract_log_extra(record)

    # Assert
    assert result == expected_extra
