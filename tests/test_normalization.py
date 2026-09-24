from mapvoice_llm.normalization import normalize_navigation_text


def test_distance_and_road_expansion():
    text = "Turn left onto Kanakapura Rd after 500m"
    assert (
        normalize_navigation_text(text)
        == "Turn left onto Kanakapura Road after five hundred meters"
    )


def test_nh_expansion():
    text = "Continue on NH 44"
    assert normalize_navigation_text(text) == "Continue on National Highway 44"
