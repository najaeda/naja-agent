# Exemples vérifiés et testés

## Règle fondamentale
Tout snippet dans ce skill a été exécuté sur un vrai design et produit
le résultat attendu. Ne pas modifier la structure sans re-tester.

## Pattern : variable partagée entre __main__ et fonction
Certaines fonctions NajaEDA utilisent une variable initialisée dans
__main__ et accessible depuis la fonction via le scope global.
Ne PAS initialiser ces variables dans la fonction.

```python
# CORRECT
def apply_dle(top, keep_attributes=None):
    # 'instances' est défini dans __main__, pas ici

if __name__ == '__main__':
    instances = set()   # ← ici, accessible depuis apply_dle
    apply_dle(top)

# INCORRECT
def apply_dle(top, keep_attributes=None):
    instances = set()   # ← cache la globale, résultat vide
```

## Pattern : charger liberty OU primitives selon le design
```python
lib_files = [f for f in os.listdir(lib_dir) if f.endswith('.lib')]
if lib_files:
    netlist.load_liberty(lib_files)
else:
    netlist.load_primitives('xilinx')   # FPGA sans liberty
```

## Pattern : chemin dynamique depuis __file__
```python
# Ne jamais hardcoder les chemins
benchmarks = path.join(path.dirname(path.abspath(__file__)), 'benchmarks')
```

## Pattern : upper/lower explicite pour le routage des termes
```python
# Pour un terme d'instance enfant, utiliser l'API upper côté parent.
child = top.create_child_instance("INV_X1", "u_inv")
in_term = child.get_term("A")
out_term = child.get_term("Y")

src = top.get_net("src_net")
dst = top.create_net("dst_net")

in_term.connect_upper_net(src)
out_term.connect_upper_net(dst)

in_term.disconnect_upper_net()
in_term.connect_upper_net(top.get_net("alt_src_net"))

# Lower ne s'emploie que pour le top ou lorsque la doc le demande explicitement.
top_term = top.get_term("TOP_IN")
top_term.connect_lower_net(top.get_net("top_net"))
top_term.disconnect_lower_net()
```

## Pattern : insertion structurelle minimale
```python
child = top.create_child_instance("BUF_X1", "u_buf")
src_net = top.get_net("path_in")
mid_net = top.create_net("path_mid")

child.get_term("A").connect_upper_net(src_net)
child.get_term("Y").connect_upper_net(mid_net)
```

## Pattern : reconnect upper after disconnect
```python
term = child.get_term("A")
term.disconnect_upper_net()
term.connect_upper_net(top.get_net("alt_src_net"))
```

## Pattern : insert in path
```python
in_net = top.get_net("logic_path_in")
out_net = top.create_net("logic_path_out")

stage = top.create_child_instance("INV_X1", "u_stage")
stage.get_term("A").connect_upper_net(in_net)
stage.get_term("Y").connect_upper_net(out_net)
```

## Pattern : choisir un net exploitable avant modification
```python
named_nets = [n for n in top.get_nets() if n.get_name()]

for net in named_nets:
    terms = list(net.get_terms())
    if any(t.is_output() and t.get_instance().is_top() for t in terms):
        print(f"primary-output-visible: {net.get_name()}")
    elif any(t.get_instance().is_sequential() for t in terms):
        print(f"sequential-visible: {net.get_name()}")
```

## Common pitfalls
- `list(top.get_nets())[0]` n'est pas un bon point de départ: il peut s'agir d'un net anonyme ou interne.
- `disconnect()` seul n'est pas la bonne API: utiliser `disconnect_upper_net()` ou `disconnect_lower_net()`.
- Une connexion avec la mauvaise face du design peut lever `RuntimeError`.
- Une modification sur un net sans fanout visible peut rester invisible pour Kepler ou une vérification formelle.
- Pour un terme d'enfant, la règle par défaut est l'API upper; lower n'est réservé qu'au top ou aux cas documentés.

## Types de retour réels (vérifiés, différents de la doc)
| Fonction | Doc dit | Réalité |
|---|---|---|
| `get_leaf_drivers()` | instances | `Term` → appeler `.get_instance()` |
| `get_leaf_readers()` | instances | `Term` → appeler `.get_instance()` |
| `id(instance)` | stable | INSTABLE — utiliser `==` et `hash()` |
| `id(equipotential)` | stable | INSTABLE — ne pas utiliser comme clé |

## Identifiants stables
```python
# CORRECT — __hash__ et __eq__ basés sur pathIDs C++
visited = set()
if term in visited: ...      # fonctionne
if instance in instances: ...  # fonctionne

# INCORRECT
if id(term) in visited: ...    # id() change à chaque appel
```

## Nets anonymes vs nets nommés
- Un net avec un nom vide ou généré automatiquement peut être interne, peu observable, ou non pertinent pour la validation.
- Pour qu'une modification soit détectable par Kepler ou par une vérification formelle, privilégier un net nommé qui a un fanout vers une sortie primaire ou un élément séquentiel.
- Si un changement reste invisible après transformation, vérifier d'abord que le net cible est vraiment observable avant de poursuivre.

## Kepler observability
- Kepler usually needs the change to reach a primary output or a DFF input to be visible
- if `n.get_name() == ''`, skip that net unless the workflow explicitly wants internal wiring
- filter first: `[n for n in top.get_nets() if n.get_name()]`