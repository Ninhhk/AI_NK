import compileall
import sys
import warnings


warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore")

ok = (
    compileall.compile_dir("backend", quiet=1)
    and compileall.compile_dir("frontend", quiet=1)
    and compileall.compile_dir("utils", quiet=1)
)
sys.stderr.write(f"compileall ok: {ok}\n")

import backend.api.main as m
sys.stderr.write(f"import backend.api.main ok; app type = {type(m.app)}\n")
sys.stderr.write("SMOKE PASS\n")

sys.exit(0 if ok else 1)
