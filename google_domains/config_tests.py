"""
    Tests for config
"""
import os
from mock import patch  # create_autospec
from box import Box
import pytest
import google_domains.config as test


PACKAGE = "google_domains."


@patch(PACKAGE + "config.read_configfile")
def test_initialize_from_files(read_configfile):
    """ Tests initialize_from_files
    """
    # File has something
    read_configfile.return_value = {"domain": "foobar"}
    response = test.initialize_from_files()
    assert response["domain"] == "foobar"

    # File has nothing
    read_configfile.return_value = {}
    response = test.initialize_from_files()
    assert not response


def test_initialize_from_env():
    """ Tests initialize_from_env
    """
    env = "GOOGLE_DOMAINS_DOMAIN"

    # set the env var to something
    os.environ[env] = "foobar"
    response = test.initialize_from_env()
    assert response["domain"] == "foobar"

    # set the env var to nothing
    os.environ[env] = ""
    response = test.initialize_from_env()
    assert response.get("domain") is None

    del os.environ[env]
    response = test.initialize_from_env()
    assert response.get("domain") is None


def test_initialize_from_cmdline():
    """ Tests initialize_from_cmdline
    """

    # DEFAULT ARGS
    response = test.initialize_from_cmdline([])
    assert response.get("verbose") is None
    assert response.get("browser") == "firefox"
    assert response.get("operation") == "ls"
    assert response.get("hostname") == ""
    assert response.get("target") == ""

    # VERBOSE LS
    response = test.initialize_from_cmdline("-v ls".split())
    assert response.get("verbose") is True
    assert response.get("operation") == "ls"

    # QUIET ADD
    response = test.initialize_from_cmdline("-q add".split())
    assert response.get("verbose") is False
    assert response.get("operation") == "add"

    # SET DOMAIN
    response = test.initialize_from_cmdline("--domain foo.bar del".split())
    assert response.get("verbose") is None
    assert response.get("domain") == "foo.bar"
    assert response.get("operation") == "del"

    # CHROME
    response = test.initialize_from_cmdline("--browser chrome".split())
    assert response.get("verbose") is None
    assert response.get("browser") == "chrome"
    assert response.get("operation") == "ls"

    # FIREFOX
    response = test.initialize_from_cmdline("--browser firefox".split())
    assert response.get("verbose") is None
    assert response.get("browser") == "firefox"
    assert response.get("operation") == "ls"

    # INVALID BROWSER
    with pytest.raises(SystemExit) as e:
        response = test.initialize_from_cmdline("--browser foobar".split())
        assert e.type == SystemExit

    # INVALID OPERATION
    with pytest.raises(SystemExit) as e:
        response = test.initialize_from_cmdline("foobar".split())
        assert e.type == SystemExit


def test_validate_args():
    """ Tests validate_args
    """

    validation_tests = [
        # No hostname for add
        [{"operation": "add"}, ["hostname", "The add operation needs a"]],
        # Has hostname, but no password for add
        [{"operation": "add", "hostname": "foobar"}, ["target"]],
        # No hostname for del
        [{"operation": "del"}, ["hostname"]],
        # No username
        [{"operation": "ls"}, ["username", "Please"]],
        # Has username, but no password
        [{"operation": "ls", "username": "foo"}, ["password"]],
        # Has username and password, but no domain
        [{"operation": "ls", "username": "foo", "password": "bar"}, ["domain"]],
    ]

    for validation_test in validation_tests:
        args = validation_test[0]
        strings = validation_test[1]

        for string in strings:
            assert string in test.validate_args(Box(args))
