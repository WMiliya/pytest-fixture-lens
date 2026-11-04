def test_checkout_uses_database(client):
    assert client["db"]["connected"] is True


def test_checkout_reads_settings(client):
    assert client["db"]["settings"]["retries"] == 3


def test_settings_are_shared(settings):
    assert settings["currency"] == "USD"
