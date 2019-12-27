import pytest

import vyper
from vyper import (
    opcodes,
)


@pytest.fixture(params=list(opcodes.EVM_VERSIONS))
def evm_version(request):
    default = opcodes.active_evm_version
    opcodes.active_evm_version = opcodes.EVM_VERSIONS[request.param]
    yield request.param
    opcodes.active_evm_version = default


def test_opcodes():
    code = """
@public
def a() -> bool:
    return True
    """

    out = vyper.compile_code(code, ['opcodes_runtime', 'opcodes'])

    assert len(out['opcodes']) > len(out['opcodes_runtime'])
    assert out['opcodes_runtime'] in out['opcodes']


def test_version_check_no_begin_or_end():
    with pytest.raises(AssertionError):
        opcodes.version_check()


def test_version_check(evm_version):
    assert opcodes.version_check(begin=evm_version)
    assert opcodes.version_check(end=evm_version)
    assert opcodes.version_check(begin=evm_version, end=evm_version)
    if evm_version != "byzantium":
        assert not opcodes.version_check(end="byzantium")
    if evm_version != "istanbul":
        assert not opcodes.version_check(begin="istanbul")


def test_get_opcodes(evm_version):
    op = opcodes.get_opcodes()
    if evm_version == "istanbul":
        assert "CHAINID" in op
        assert op['SLOAD'][-1] == 800
    else:
        assert "CHAINID" not in op
        assert op['SLOAD'][-1] == 200
    if evm_version == "byzantium":
        assert "CREATE2" not in op
    else:
        assert op["CREATE2"][-1] == 32000
