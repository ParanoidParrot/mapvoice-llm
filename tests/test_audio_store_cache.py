from mapvoice_llm.audio_store import AudioStore


def test_audio_cache_is_language_aware(tmp_path):
    store = AudioStore(tmp_path)

    en = store.save(
        kind="raw",
        text="hello",
        audio_bytes=b"en",
        cache_key="sarvam|v3|shubh|en-IN",
    )
    kn = store.save(
        kind="raw",
        text="hello",
        audio_bytes=b"kn",
        cache_key="sarvam|v3|shubh|kn-IN",
    )

    assert en != kn
    assert en.read_bytes() == b"en"
    assert kn.read_bytes() == b"kn"
