# Template: Complete Structure of a Naja Script

All templates here use direct calls to najaeda.netlist.
**Module:** `import najaeda.netlist as netlist`

## Rules Embedded in Every Template

- Import exactly: import najaeda.netlist as netlist
- Do not import `naja_utils` (internal only)
- Load Liberty files before Verilog:
    netlist.load_liberty([str(f) for f in Path(design_dir).glob("*.lib")])
- Load Verilog with:
  netlist.load_verilog(path, config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True))
- Methods returning generators must be wrapped with list():
  get_output_bit_terms(), get_input_bit_terms(), get_leaf_children()
- Use native DLE: netlist.apply_dle()
- Export with top.dump_verilog("output.v") only
- Output path must end with .v and parent directory must exist

---

## Minimal Template: Load, Analyze, Export

```python
#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

import najaeda.netlist as netlist

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: script.py <input_file> [output_file]")
        return 1

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output.v")

    if not input_file.exists() or not input_file.is_file():
        logger.error(f"Missing input file: {input_file}")
        return 1

    if output_file.suffix != ".v":
        logger.error(f"Output file must end with .v: {output_file}")
        return 1

    if not output_file.parent.exists():
        logger.error(f"Output directory does not exist: {output_file.parent}")
        return 1

    design_dir = input_file.resolve().parent
    netlist.load_liberty([str(f) for f in Path(design_dir).glob("*.lib")])

    top = netlist.load_verilog(
        str(input_file),
        config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True),
    )
    if top is None:
        logger.error("Failed to load design")
        return 1

    leaves = list(top.get_leaf_children())
    logger.info(f"Top module: {top.get_model_name()}")
    logger.info(f"Leaf cells: {len(leaves)}")

    top.dump_verilog(str(output_file))
    logger.info(f"Wrote {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Template: Query Connectivity

```python
#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

import najaeda.netlist as netlist

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: script.py <input_file>")
        return 1

    input_file = Path(sys.argv[1])
    design_dir = input_file.resolve().parent

    netlist.load_liberty([str(f) for f in Path(design_dir).glob("*.lib")])
    top = netlist.load_verilog(
        str(input_file),
        config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True),
    )
    if top is None:
        logger.error("Failed to load design")
        return 1

    leaves = list(top.get_leaf_children())
    for leaf in leaves:
        inputs = list(leaf.get_input_bit_terms())
        outputs = list(leaf.get_output_bit_terms())
        print(f"{leaf.get_model_name()}: {len(inputs)} in, {len(outputs)} out")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Template: Multi-step Transform (Native DLE)

```python
#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

import najaeda.netlist as netlist

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: script.py <input_file> <output_file>")
        return 1

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if output_file.suffix != ".v":
        logger.error("Output file must end with .v")
        return 1
    if not output_file.parent.exists():
        logger.error(f"Output directory does not exist: {output_file.parent}")
        return 1

    design_dir = input_file.resolve().parent
    netlist.load_liberty([str(f) for f in Path(design_dir).glob("*.lib")])
    top = netlist.load_verilog(
        str(input_file),
        config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True),
    )
    if top is None:
        logger.error("Failed to load design")
        return 1

    netlist.apply_dle()
    netlist.apply_constant_propagation()

    top.dump_verilog(str(output_file))
    logger.info(f"Wrote {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

For the canonical list of forbidden or deprecated API calls, see [resources/api-rules.md](resources/api-rules.md).
