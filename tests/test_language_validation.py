from mapvoice_llm.language_profiles import LanguageProfile
from mapvoice_llm.language_validation import native_script_fraction


def test_tamil_script_fraction():
    profile = LanguageProfile(
        language_code="ta",
        language="Tamil",
        script_name="Tamil",
        unicode_ranges=[["0B80", "0BFF"]],
        tts_language_code="ta-IN",
    )

    assert native_script_fraction(
        "தமிழ்",
        profile,
    ) == 1.0

    assert native_script_fraction(
        "Telugu",
        profile,
    ) == 0.0
