from mapvoice_llm.audio_store import AudioStore


def test_audio_store_is_deterministic(tmp_path):
    store = AudioStore(tmp_path)
    first = store.save(
        kind="raw",
        text="Turn left",
        audio_bytes=b"abc",
    )
    second = store.save(
        kind="raw",
        text="Turn left",
        audio_bytes=b"abc",
    )

    assert first == second
    assert first.read_bytes() == b"abc"
    assert store.url_for(first).startswith("/audio/")
