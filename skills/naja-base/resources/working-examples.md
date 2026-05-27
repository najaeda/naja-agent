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