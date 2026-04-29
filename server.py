#!/usr/bin/env python3
import importlib
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import List
import json

from mcp.server.fastmcp import FastMCP

from najaeda import netlist

app = FastMCP("naja-analyze")

# Keep stdout reserved for MCP JSON-RPC frames.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="[naja] [%(levelname)s] %(message)s",
    force=True,
)


def _log_info(message: str) -> None:
    logging.info(message)


_log_info("serveur lancé")

_loaded_liberty_files: List[str] = []


def _ensure_list_of_paths(files: str | List[str]) -> List[str]:
    if isinstance(files, str):
        return [files]
    return list(files)


def _reload_design_from_verilog(verilog_path: str) -> None:
    netlist.reset()
    if _loaded_liberty_files:
        netlist.load_liberty(_loaded_liberty_files)
    config = netlist.VerilogConfig(
        keep_assigns=True,
        allow_unknown_designs=True,
    )
    netlist.load_verilog(verilog_path, config=config)


def _get_primitive_library_count() -> int:
    try:
        naja = importlib.import_module("naja")

        universe = naja.NLUniverse.get()
        if universe is None:
            return 0
        top_design = universe.getTopDesign()
        if top_design is None:
            return 0
        primitive_libraries = top_design.getDB().getPrimitiveLibraries()
        if hasattr(primitive_libraries, "size"):
            return int(primitive_libraries.size())
        return len(list(primitive_libraries))
    except Exception:
        return 0


def _run_constant_propagation_isolated() -> str:
    top = netlist.get_top()
    if top is None:
        raise RuntimeError("Aucun design chargé. Utilise d'abord load_verilog.")

    primitive_lib_count = _get_primitive_library_count()
    if primitive_lib_count == 0:
        raise RuntimeError(
            "Propagation constante indisponible: aucune librairie de primitives chargée. "
            "Charge d'abord un .lib via load_liberty()."
        )
    if primitive_lib_count != 1:
        raise RuntimeError(
            "Propagation constante indisponible: exactement une librairie de primitives est requise "
            f"(trouvées: {primitive_lib_count})."
        )

    with tempfile.TemporaryDirectory(prefix="naja_mcp_cp_") as tmp_dir:
        input_v = os.path.join(tmp_dir, "input.v")
        output_v = os.path.join(tmp_dir, "output.v")
        script_path = os.path.join(tmp_dir, "run_cp.py")

        top.dump_verilog(input_v)

        script = "\n".join([
            "from najaeda import netlist",
            f"input_v = {input_v!r}",
            f"output_v = {output_v!r}",
            f"liberty_files = {_loaded_liberty_files!r}",
            "if liberty_files:",
            "    netlist.load_liberty(liberty_files)",
            "cfg = netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True)",
            "netlist.load_verilog(input_v, config=cfg)",
            "netlist.apply_constant_propagation()",
            "netlist.get_top().dump_verilog(output_v)",
        ])
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            details = stderr or stdout or f"code retour={result.returncode}"
            if result.returncode < 0:
                signal_num = -result.returncode
                details = f"processus fils tué par signal {signal_num} ({details})"
            raise RuntimeError(f"Propagation constante échouée en mode isolé: {details}")

        if not os.path.exists(output_v):
            raise RuntimeError("Le sous-processus n'a pas produit de netlist de sortie")

        _reload_design_from_verilog(output_v)
        return "Constantes propagées (mode isolé)"


@app.tool()
async def load_liberty(files: str | List[str]) -> str:
    _log_info(f"chargement des fichiers liberty: {files}")
    """Charge liberty files (.lib)"""
    file_list = _ensure_list_of_paths(files)
    netlist.load_liberty(file_list)
    _loaded_liberty_files[:] = file_list
    return f"Liberty {files} chargée"

@app.tool()
async def load_verilog(verilog_path: str | List[str]) -> str:
    _log_info(f"chargement du verilog: {verilog_path}")
    """Charge Verilog netlist"""
    netlist.reset()
    if _loaded_liberty_files:
        netlist.load_liberty(_loaded_liberty_files)
    config = netlist.VerilogConfig(
        keep_assigns=True,
        allow_unknown_designs=True,
    )
    top = netlist.load_verilog(verilog_path, config=config)
    return f"{verilog_path} chargée, top: {top.get_name()}"


@app.tool()
async def list_verilog_tests() -> str:
    """Liste les fichiers Verilog de test disponibles dans mcp-servers."""
    base_dir = Path(__file__).resolve().parent
    tests = sorted(
        str(path.name)
        for path in base_dir.glob("*.v")
    )
    return json.dumps({"files": tests}, indent=2)

@app.tool()
async def apply_dle() -> str:
    _log_info("application du DLE")
    """Don't Logic Equivalent (optimisation)"""
    netlist.apply_dle()
    return "DLE appliqué"

@app.tool()
async def apply_constant_propagation() -> str:
    _log_info("application de la propagation des constantes")
    """Propagation constantes"""
    return _run_constant_propagation_isolated()

@app.tool()
async def get_max_fanout() -> str:
    _log_info("récupération du fanout max")
    """Fanout max (liste sources)"""
    result = netlist.get_max_fanout()
    max_val = result[0]
    fanouts = []
    if len(result) > 1:
        for entry in result[1]:
            driver = str(entry[0])
            readers = [str(r) for r in entry[1]]
            fanouts.append({"driver": driver, "readers": readers})
    return json.dumps({"max_fanout": max_val, "details": fanouts})

@app.tool()
async def get_max_logic_level() -> str:
    _log_info("récupération du niveau logique max")
    """Niveaux logiques max"""
    result = netlist.get_max_logic_level()
    max_val = result[0]
    paths = []
    if len(result) > 1:
        for path in result[1]:
            paths.append([str(t) for t in path])
    return json.dumps({"max_logic_level": max_val, "paths": paths})

@app.tool()
async def get_top_info() -> str:
    _log_info("récupération des informations sur le top design")
    """Informations sur le top design (ports, nets, instances)"""
    top = netlist.get_top()
    info = {
        "name": top.get_name(),
        "nb_terms": top.count_terms(),
        "nb_nets": top.count_nets(),
        "nb_instances": top.count_child_instances(),
        "terms": [],
        "nets": [],
        "instances": [],
    }
    for term in top.get_terms():
        info["terms"].append({
            "name": term.get_name(),
            "direction": str(term.get_direction()),
            "width": term.get_width(),
        })
    for net in top.get_nets():
        info["nets"].append({
            "name": net.get_name(),
            "width": net.get_width(),
            "is_bus": net.is_bus(),
        })
    for inst in top.get_child_instances():
        info["instances"].append({
            "name": inst.get_name(),
            "model": inst.get_model_name(),
            "is_leaf": inst.is_leaf(),
            "is_blackbox": inst.is_blackbox(),
        })
    _log_info(f"informations sur le top design: {json.dumps(info, indent=2)}")
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    app.run()
