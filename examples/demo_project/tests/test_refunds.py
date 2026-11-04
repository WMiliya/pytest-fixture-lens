def test_refund_uses_database(client):
    assert client["db"]["connected"] is True


def test_refund_reads_settings(client):
    assert client["db"]["settings"]["currency"] == "USD"


def test_database_module_scope(database):
    assert database["connected"] is True
