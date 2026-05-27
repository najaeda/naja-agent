# Common Steps: Patterns for Naja Scripts

All patterns use only verified functions from najaeda.netlist.

## Règle avant d'écrire tout script

1. Copier le pattern le plus proche de [working-examples.md](working-examples.md)
2. Ne modifier QUE ce qui est nécessaire pour le cas demandé
3. Ne jamais inventer une API — si elle n'est pas dans [api-functions.md](api-functions.md)
    ou [working-examples.md](working-examples.md), elle n'existe probablement pas
4. Les types de retour réels sont dans [working-examples.md](working-examples.md),
    pas dans la doc officielle

**Module:** `import najaeda.netlist as netlist`

---

## Pattern BFS NajaEDA — validé sur vexriscv et black_parrot

```python
# Dans __main__ :
instances = set()   # GLOBAL — accessible depuis la fonction

# Dans la fonction :
visited = set()     # TOUJOURS set(), jamais list()
queue   = deque()

for term in top.get_output_bit_terms():
    if term not in visited:          # dédoublonner AVANT
        visited.add(term)
        queue.append(term)

while queue:
    term = queue.popleft()
    equip = term.get_equipotential()
    if equip is None:
        continue
    for driver_term in equip.get_leaf_drivers():   # retourne Term, pas Instance
        inst = driver_term.get_instance()           # .get_instance() obligatoire
        if inst not in instances:
            instances.add(inst)
            for in_term in inst.get_input_bit_terms():
                if in_term not in visited:           # dédoublonner AVANT
                    visited.add(in_term)
                    queue.append(in_term)
```

Règles :
- `set()` partout — jamais `list()` pour les collections visitées
- `get_leaf_drivers()` -> `Term` -> `.get_instance()` -> `Instance`
- Dédoublonner AVANT d'ajouter dans la queue, pas après
- `instances` défini dans `__main__`, pas dans la fonction

---

## Pattern 1: Load libs, then Verilog

```python
from pathlib import Path
import najaeda.netlist as netlist

input_path = Path("circuit.v")
design_dir = input_path.resolve().parent

try:
    netlist.load_primitives('xilinx')
except Exception as exc:
    logger.error(f"Failed to load Xilinx primitives: {exc}")
    return 1

netlist.load_liberty([str(f) for f in Path(design_dir).glob("*.lib")])
top = netlist.load_verilog(
    str(input_path),
    config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True),
)
if top is None:
    raise SystemExit(1)
```

---

## Pattern 2: Query connectivity safely (generator APIs)

```python
leaves = list(top.get_leaf_children())
for leaf in leaves:
    in_terms = list(leaf.get_input_bit_terms())
    out_terms = list(leaf.get_output_bit_terms())
    print(f"{leaf.get_model_name()}: {len(in_terms)} inputs, {len(out_terms)} outputs")
```

---

## Pattern 3: Modify and reconnect

```python
leaves = list(top.get_leaf_children())
if not leaves:
    raise SystemExit("No leaf cells")

candidate = leaves[0]
in_terms = list(candidate.get_input_bit_terms())

if in_terms:
    new_net = top.create_net("new_signal")
    in_terms[0].disconnect_lower_net()  # disconnect first
    in_terms[0].connect_lower_net(new_net)  # then reconnect
```

---

## Pattern 4: Apply native transforms

```python
netlist.apply_dle()
netlist.apply_constant_propagation()
```

---

## Pattern 5: Export correctly

```python
from pathlib import Path

output_path = Path("output.v")
if output_path.suffix != ".v":
    raise SystemExit("Output path must end with .v")
if not output_path.parent.exists():
    raise SystemExit(f"Output directory does not exist: {output_path.parent}")

top.dump_verilog(str(output_path))
```

---

## Required Checks Before Running

- Input file exists and is readable
- For Xilinx FPGA netlists, load primitives first with `netlist.load_primitives('xilinx')`
- Liberty loading happens before Verilog loading
- top is not None after load_verilog
- list() wrapping for get_output_bit_terms/get_input_bit_terms/get_leaf_children
- Output path ends with .v
- Output directory already exists

---

For the canonical list of forbidden or deprecated API calls, see [resources/api-rules.md](resources/api-rules.md).
