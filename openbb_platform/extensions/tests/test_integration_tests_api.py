"""Test the integration tests."""
import pytest
from extensions.tests.utils.integration_tests_testers import (
    check_missing_integration_test_params,
    check_missing_integration_test_providers,
    get_integration_tests,
    get_module_functions,
)


def run_test(test_type: str, check_function) -> None:
    """Run tests helper function."""
    integration_tests = get_integration_tests(test_type=test_type)
    functions = get_module_functions(integration_tests)
    missing_items = check_function(functions)

    assert not missing_items, "\n".join(missing_items)


@pytest.mark.skip(reason="Needs uvicorn to be launched but shouldn't be the case.")
def test_api_interface_integration_test_providers() -> None:
    """Test if there are any missing providers for integration tests."""
    run_test("integration", check_missing_integration_test_providers)


@pytest.mark.skip(reason="Needs uvicorn to be launched but shouldn't be the case.")
def test_api_interface_integration_test_params() -> None:
    """Test if there are any missing params for integration tests."""
    run_test("integration", check_missing_integration_test_params)
