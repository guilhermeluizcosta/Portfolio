from locale_loader import load_server_messages


def test_load_server_messages_returns_both_locales():
    """Server messages must be available for English and Portuguese."""
    messages = load_server_messages()

    assert "en" in messages
    assert "pt-BR" in messages
    assert messages["en"]["email_success"] == "Message sent successfully!"
    assert messages["pt-BR"]["email_success"] == "Mensagem enviada com sucesso!"