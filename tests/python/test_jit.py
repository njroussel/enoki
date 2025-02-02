import enoki as ek
import pytest
import importlib


@pytest.fixture(scope="module", params=['enoki.cuda.ad', 'enoki.llvm.ad'])
def m(request):
    if 'cuda' in request.param:
        if not ek.has_backend(ek.JitBackend.CUDA):
            pytest.skip('CUDA mode is unsupported')
    else:
        if not ek.has_backend(ek.JitBackend.LLVM):
            pytest.skip('LLVM mode is unsupported')
    yield importlib.import_module(request.param)


def test01_kernel_history(m):
    for i in range(4):
        ek.eval(ek.arange(m.Float, i + 4))

    # Kernel history should be disabled by default
    assert len(ek.kernel_history()) == 0

    assert not ek.flag(ek.JitFlag.KernelHistory)

    with ek.scoped_set_flag(ek.JitFlag.KernelHistory, True):
        assert ek.flag(ek.JitFlag.KernelHistory)
        for i in range(4):
            ek.eval(ek.arange(m.Float, i + 4))

        history = ek.kernel_history()
        assert len(history) == 4
        for i in range(4):
            assert history[i]['size'] == i + 4

    assert not ek.flag(ek.JitFlag.KernelHistory)

    # Kernel history should be erased after queried
    assert len(ek.kernel_history()) == 0



# TODO:
# - Check number of kernel launched when scheduling variables to make sure it create a single kernel
# - Check that number of output only contains the ones required (optimization)
# - ...
