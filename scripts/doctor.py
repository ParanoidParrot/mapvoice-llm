from __future__ import annotations
import sys
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/'src'))
from mapvoice_llm.runtime_compat import environment_snapshot, python_runtime_check

def main():
    runtime=python_runtime_check(); snapshot=environment_snapshot()
    print('MapVoice-LLM environment doctor')
    print('='*40)
    print(f"Python executable : {snapshot['python_executable']}")
    print(f"Python version    : {snapshot['python']}")
    print(f"Platform          : {snapshot['platform']}")
    print(); print(f'Runtime status    : {runtime.level.upper()}'); print(runtime.message); print()
    for name,version in snapshot['packages'].items(): print(f"{name:14}: {version or 'not installed'}")
    try:
        import torch
        print(); print(f'CUDA available    : {torch.cuda.is_available()}')
        print('MPS available     : '+str(hasattr(torch.backends,'mps') and torch.backends.mps.is_available()))
    except Exception: pass
    if not runtime.ok: raise SystemExit(1)
if __name__=='__main__': main()
