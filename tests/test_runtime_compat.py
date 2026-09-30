from mapvoice_llm.runtime_compat import environment_snapshot, package_version

def test_environment_snapshot_has_python():
    snapshot=environment_snapshot()
    assert snapshot['python']
    assert snapshot['python_executable']

def test_missing_package_returns_none():
    assert package_version('definitely_not_a_real_package_xyz') is None
