#!/usr/bin/env python3
"""
naja_utils.py: Common Functions Library for Naja Scripts

Provides reusable utilities for documented Naja API functions.
Reference: https://najaeda.readthedocs.io/en/latest
API Catalog: ../resources/api-functions.md

All functions are self-contained and can be imported independently.
NOTE: This is an INTERNAL utility module. Do NOT import into generated scripts.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Try to import najaeda.netlist (correct module path)
try:
    import najaeda.netlist as netlist
    NAJA_AVAILABLE = True
except ImportError:
    NAJA_AVAILABLE = False
    logging.warning("Naja library not found - some functions will be limited")

logger = logging.getLogger(__name__)


# ============================================================================
# LOADING & VALIDATION
# ============================================================================

# ============================================================================
# LOADING & VALIDATION
# ============================================================================

def safe_load_liberty(filepaths: List[str]) -> bool:
    """
    Safely load Liberty library file(s).
    
    Args:
        filepaths: List of Liberty file paths (strings or Path objects)
    
    Returns:
        True if successful, False otherwise
    
    Example:
        if not safe_load_liberty(["cell.lib", "io.lib"]):
            exit(1)
    """
    if not NAJA_AVAILABLE:
        logger.error("Naja library not available")
        return False
    
    try:
        file_list = [str(f) for f in filepaths]
        logger.info(f"Loading {len(file_list)} Liberty file(s)")
        netlist.load_liberty(file_list)
        logger.info("Liberty files loaded successfully")
        return True
    except FileNotFoundError as e:
        logger.error(f"Liberty file not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to load Liberty files: {e}")
        return False


def safe_load_verilog(filepath: str, keep_assigns: bool = True) -> Optional[Any]:
    """
    Safely load Verilog design with error handling.
    
    Args:
        filepath: Path to Verilog file
        keep_assigns: Keep assign statements as instances (default True)
    
    Returns:
        Top-level Instance object or None if failed
    
    Example:
        # Load Liberty first!
        safe_load_liberty(["design.lib"])
        top = safe_load_verilog("circuit.v")
        if top is None:
            exit(1)
    """
    filepath = Path(filepath)
    
    # Check file exists
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        return None
    
    if not filepath.is_file():
        logger.error(f"Not a file: {filepath}")
        return None
    
    if filepath.stat().st_size == 0:
        logger.error(f"File is empty: {filepath}")
        return None
    
    if not NAJA_AVAILABLE:
        logger.error("Naja library not available")
        return None
    
    try:
        logger.info(f"Loading Verilog design from {filepath}")
        config = netlist.VerilogConfig(
            keep_assigns=keep_assigns,
            allow_unknown_designs=True
        )
        top = netlist.load_verilog(str(filepath), config=config)
        
        if top is None:
            logger.error("Failed to load Verilog: top instance is None")
            return None
        
        logger.info(f"Design loaded successfully (top: {top.get_model_name()})")
        return top
    except FileNotFoundError as e:
        logger.error(f"File not found during load: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load Verilog design: {e}")
        return None


# ============================================================================
# EXPORT & PERSISTENCE
# ============================================================================

def safe_export_verilog(top: Any, filepath: str) -> bool:
    """
    Safely export design to Verilog file.
    
    Args:
        top: Top-level Instance object
        filepath: Output file path (must end with .v)
    
    Returns:
        True if successful, False otherwise
    
    Example:
        if not safe_export_verilog(top, "output.v"):
            exit(1)
    """
    filepath = Path(filepath)
    
    # Validate output path
    if filepath.suffix != ".v":
        logger.error(f"Output file must end with .v, got: {filepath}")
        return False
    
    output_dir = filepath.parent
    if not output_dir.exists():
        logger.error(f"Output directory does not exist: {output_dir}")
        return False
    
    if top is None:
        logger.error("Top instance is None")
        return False
    
    try:
        logger.info(f"Exporting design to {filepath}")
        top.dump_verilog(str(filepath))

        if not filepath.exists():
            logger.error(f"Export file not created: {filepath}")
            return False

        file_size = filepath.stat().st_size
        if file_size == 0:
            logger.error(f"Export file is empty: {filepath}")
            return False
        
        logger.info(f"Export successful ({file_size} bytes)")
        return True
    except PermissionError as e:
        logger.error(f"Permission denied writing to {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return False


def safe_export_naja_if(top: Any, filepath: str) -> bool:
    """
    Safely export design in Naja IF format.
    
    Args:
        top: Top-level Instance object
        filepath: Output file path (Naja IF format)
    
    Returns:
        True if successful, False otherwise
    
    Example:
        if not safe_export_naja_if(top, "design.naja"):
            exit(1)
    """
    if top is None:
        logger.error("Top instance is None")
        return False
    
    filepath = Path(filepath)
    output_dir = filepath.parent
    if not output_dir.exists():
        logger.error(f"Output directory does not exist: {output_dir}")
        return False
    
    if not NAJA_AVAILABLE:
        logger.error("Naja library not available")
        return False
    
    try:
        logger.info(f"Exporting design to {filepath} (Naja IF)")
        netlist.dump_naja_if(str(filepath))

        if not filepath.exists():
            logger.error(f"Export file not created: {filepath}")
            return False
        
        logger.info(f"Naja IF export successful")
        return True
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return False


# ============================================================================
# ANALYSIS & QUERY
# ============================================================================

def get_leaf_cells(instance: Any) -> List[Any]:
    """
    Get all leaf (non-hierarchical) child cells.
    
    Args:
        instance: Instance object (typically top-level)
    
    Returns:
        List of leaf cell instances
    
    Example:
        leaves = get_leaf_cells(top)
        for leaf in leaves:
            print(f"{leaf.get_name()}: {leaf.get_model_name()}")
    """
    if instance is None:
        logger.error("Instance is None")
        return []
    
    try:
        leaves = list(instance.get_leaf_children())
        logger.debug(f"Found {len(leaves)} leaf cells")
        return leaves
    except Exception as e:
        logger.error(f"Failed to get leaf cells: {e}")
        return []


def analyze_instance(instance: Any) -> Dict[str, Any]:
    """
    Get comprehensive analysis of an instance.
    
    Args:
        instance: Instance object
    
    Returns:
        Dictionary with instance information
    
    Example:
        info = analyze_instance(leaf_cell)
        print(f"Model: {info['model']}")
        print(f"Inputs: {info['input_count']}")
    """
    if instance is None:
        logger.error("Instance is None")
        return {}
    
    try:
        model = instance.get_model_name()
        input_bit_terms = list(instance.get_input_bit_terms())
        output_bit_terms = list(instance.get_output_bit_terms())
        input_terms = list(instance.get_input_terms())
        output_terms = list(instance.get_output_terms())
        attrs = list(instance.get_attributes())
        
        return {
            'name': instance.get_name(),
            'model': model,
            'is_leaf': instance.is_leaf(),
            'is_primitive': instance.is_primitive(),
            'input_bit_count': len(input_bit_terms),
            'output_bit_count': len(output_bit_terms),
            'input_term_count': len(input_terms),
            'output_term_count': len(output_terms),
            'attribute_count': len(attrs),
            'input_bit_terms': input_bit_terms,
            'output_bit_terms': output_bit_terms,
            'input_terms': input_terms,
            'output_terms': output_terms,
            'attributes': attrs
        }
    except Exception as e:
        logger.error(f"Failed to analyze instance: {e}")
        return {}


def print_design_structure(top: Any) -> None:
    """
    Print design hierarchy and structure.
    
    Args:
        top: Top-level Instance object
    
    Example:
        print_design_structure(top)
    """
    if top is None:
        logger.error("Top instance is None")
        return
    
    try:
        top_name = top.get_model_name()
        leaves = list(top.get_leaf_children())
        
        print("\n" + "="*60)
        print(f"DESIGN STRUCTURE: {top_name}")
        print("="*60)
        print(f"Leaf cells: {len(leaves)}")
        
        for i, leaf in enumerate(leaves[:20], 1):  # Show first 20
            model = leaf.get_model_name()
            try:
                inputs = len(list(leaf.get_input_bit_terms()))
                outputs = len(list(leaf.get_output_bit_terms()))
                print(f"  {i}. {leaf.get_name()}: {model} ({inputs} in, {outputs} out)")
            except:
                print(f"  {i}. {leaf.get_name()}: {model}")
        
        if len(leaves) > 20:
            print(f"  ... and {len(leaves) - 20} more cells")
        
        print("="*60 + "\n")
    except Exception as e:
        logger.error(f"Failed to print design structure: {e}")


def find_instance_by_path(path: str) -> Optional[Any]:
    """
    Find an instance by hierarchical path.
    
    Args:
        path: Hierarchical path (e.g., "top/cpu/alu" or as list ["top", "cpu"])
    
    Returns:
        Instance object or None if not found
    
    Example:
        inst = find_instance_by_path("top/cpu")
    """
    if not NAJA_AVAILABLE:
        logger.error("Naja library not available")
        return None
    
    try:
        inst = netlist.get_instance_by_path(path)
        if inst is None:
            logger.warning(f"Instance not found at path: {path}")
        else:
            logger.debug(f"Found instance: {inst.get_model_name()}")
        return inst
    except Exception as e:
        logger.error(f"Failed to find instance at {path}: {e}")
        return None


def connect_term_to_net(term: Any, net: Any, is_upper: bool = False) -> bool:
    """
    Safely connect a terminal to a net.
    
    Args:
        term: Terminal object
        net: Net object
        is_upper: If False (default), connect lower_net; if True, connect upper_net
    
    Returns:
        True if successful, False otherwise
    
    Example:
        success = connect_term_to_net(term, net, is_upper=False)
    """
    if term is None or net is None:
        logger.error("Terminal or net is None")
        return False
    
    try:
        if is_upper:
            term.connect_upper_net(net)
        else:
            term.connect_lower_net(net)
        logger.debug(f"Connected terminal to net")
        return True
    except Exception as e:
        logger.error(f"Failed to connect terminal: {e}")
        return False


# ============================================================================
# SETUP & CONFIGURATION
# ============================================================================

def configure_logging(log_level=logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Configure logging for Naja scripts.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
    
    Example:
        configure_logging(log_level=logging.DEBUG, log_file="script.log")
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.warning(f"Could not open log file {log_file}: {e}")


# ============================================================================
# UTILITIES
# ============================================================================

def get_instances(design: Any) -> List[Any]:
    """
    Get all instances in design.
    
    Args:
        design: Design object
    
    Returns:
        List of instances
    
    Example:
        for instance in get_instances(design):
            print(instance)
    """
    if not NAJA_AVAILABLE:
        return []
    
    try:
        top = design.get_top()
        if top is None:
            return []

        return top.get_leaf_children()
    except Exception as e:
        logger.error(f"Failed to get instances: {e}")
        return []


def print_statistics(design: Any, additional_info: str = "") -> None:
    """
    Print design statistics.
    
    Args:
        design: Design object
        additional_info: Additional information to display
    
    Example:
        print_statistics(design, f"Deleted 5 elements")
    """
    if not NAJA_AVAILABLE:
        logger.warning("Cannot print statistics - Naja not available")
        return
    
    try:
        top = design.get_top()
        leaves = top.get_leaf_children() if top is not None else []
        input_terms = 0
        output_terms = 0

        for leaf in leaves:
            input_terms += len(leaf.get_input_bit_terms())
            output_terms += len(leaf.get_output_bit_terms())

        print("\n" + "="*60)
        print("DESIGN STATISTICS")
        print("="*60)
        print(f"  top_module: {top.get_model_name() if top is not None else 'n/a'}")
        print(f"  leaf_cells: {len(leaves)}")
        print(f"  input_terms: {input_terms}")
        print(f"  output_terms: {output_terms}")
        if additional_info:
            print(f"  {additional_info}")
        print("="*60 + "\n")
    except Exception as e:
        logger.warning(f"Failed to compute statistics: {e}")


def generate_report(hierarchy: str, stats: Dict[str, Any], paths: List[Any]) -> str:
    """
    Generate analysis report.
    
    Args:
        hierarchy: Hierarchy report text
        stats: Statistics dictionary
        paths: List of critical paths
    
    Returns:
        Report as string
    
    Example:
        report = generate_report(hierarchy, stats, paths)
    """
    lines = [
        "="*60,
        "DESIGN ANALYSIS REPORT",
        "="*60,
        "",
        "HIERARCHY:",
        "-" * 60,
        hierarchy,
        "",
        "STATISTICS:",
        "-" * 60,
    ]
    
    for key, value in stats.items():
        lines.append(f"  {key}: {value}")
    
    lines.extend([
        "",
        "CRITICAL PATHS:",
        "-" * 60,
    ])
    
    if paths:
        for i, path in enumerate(paths[:10], 1):  # Top 10
            lines.append(f"  {i}. {path}")
    else:
        lines.append("  No paths found")
    
    lines.append("="*60)
    
    return "\n".join(lines)


# ============================================================================
# TRANSFORM UTILITIES
# ============================================================================

def apply_transform_safe(transform_name: str, *args, **kwargs) -> tuple:
    """
    Apply a native transformation with error handling.
    
    Args:
        transform_name: Name of transformation ('dle', 'const_prop')
        *args: Arguments to pass
        **kwargs: Keyword arguments
    
    Returns:
        (success: bool, result: Any, error: Optional[str])
    
    Example:
        success, result, error = apply_transform_safe('dle')
        if not success:
            print(f"Transform failed: {error}")
    
    Supported transforms:
        - 'dle': Dead Logic Elimination (netlist.apply_dle)
        - 'const_prop': Constant Propagation (netlist.apply_constant_propagation)
    """
    if not NAJA_AVAILABLE:
        return (False, None, "Naja library not available")
    
    try:
        logger.info(f"Applying transform: {transform_name}")
        
        if transform_name == 'dle':
            result = netlist.apply_dle()
        elif transform_name == 'const_prop':
            result = netlist.apply_constant_propagation()
        else:
            return (False, None, f"Unknown transform: {transform_name}")
        
        logger.info(f"Transform successful")
        return (True, result, None)
    except RuntimeError as e:
        error_msg = f"Runtime error (may be SEGV): {e}"
        logger.error(error_msg)
        return (False, None, error_msg)
    except Exception as e:
        error_msg = f"Transform failed: {e}"
        logger.error(error_msg)
        return (False, None, error_msg)


