# Copyright (c) 2025 GenOrca. All Rights Reserved.

import unreal
import json
import traceback
from collections import deque


def _load_asset(asset_path, expected_class=None):
    """Load an asset and optionally verify its class. Returns (asset, error_json_str)."""
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if asset is None:
        return None, json.dumps({
            "success": False,
            "message": f"Asset not found or failed to load: {asset_path}"
        })
    if expected_class is not None and not isinstance(asset, expected_class):
        return None, json.dumps({
            "success": False,
            "message": f"Asset at '{asset_path}' is {type(asset).__name__}, expected {expected_class.__name__}."
        })
    return asset, None


# ─── Read Actions ─────────────────────────────────────────────────────────────

def ue_get_selected_bp_nodes() -> str:
    """Returns information about currently selected blueprint nodes in the editor."""
    try:
        nodes = unreal.MCPythonHelper.get_selected_blueprint_nodes()
        node_infos = []
        for node in nodes:
            node_info = {
                "name": node.get_name() if hasattr(node, 'get_name') else str(node),
                "class": node.get_class().get_name() if hasattr(node, 'get_class') else str(type(node)),
                "object_path": node.get_path_name() if hasattr(node, 'get_path_name') else None
            }
            node_infos.append(node_info)
        return json.dumps({
            "success": True,
            "selected_nodes_count": len(node_infos),
            "selected_nodes": node_infos
        })
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_get_selected_bp_node_infos() -> str:
    """Returns compact blueprint node info optimized for LLM token efficiency."""
    try:
        node_infos = unreal.MCPythonHelper.get_selected_blueprint_node_infos()

        name_to_id = {}
        for i, n in enumerate(node_infos):
            name_to_id[n.node_name] = i

        def link_to_dict(link):
            d = {}
            if link.node_name in name_to_id:
                d["node"] = name_to_id[link.node_name]
            else:
                d["node"] = link.node_title
            if link.pin_name:
                d["pin"] = link.pin_name
            return d

        def pin_to_dict(pin):
            name = pin.friendly_name if pin.friendly_name else pin.pin_name
            d = {"name": name, "dir": pin.direction}
            ptype = pin.pin_type
            if pin.pin_sub_type:
                ptype += ":" + pin.pin_sub_type
            d["type"] = ptype
            if pin.default_value:
                d["default"] = pin.default_value
            linked = list(pin.linked_to)
            if linked:
                d["linked"] = [link_to_dict(l) for l in linked]
            return d

        def node_to_dict(node, idx):
            d = {"id": idx, "title": node.node_title}
            if node.node_comment:
                d["comment"] = node.node_comment
            d["pins"] = [pin_to_dict(p) for p in node.pins]
            return d

        nodes = [node_to_dict(n, i) for i, n in enumerate(node_infos)]
        return json.dumps({
            "success": True,
            "nodes": nodes
        })
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_get_blueprint_graph_info(asset_path: str = None, graph_name: str = "EventGraph") -> str:
    """Returns the full graph info for a Blueprint graph."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.get_blueprint_graph_info(bp, graph_name)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_list_callable_functions(asset_path: str = None, filter: str = "") -> str:
    """Lists callable functions available in a Blueprint context."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.list_callable_functions(bp, filter)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_list_blueprint_variables(asset_path: str = None) -> str:
    """Lists all variables defined in a Blueprint."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.list_blueprint_variables(bp)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


# ─── Write Actions ────────────────────────────────────────────────────────────

def ue_add_blueprint_node(asset_path: str = None, graph_name: str = "EventGraph",
                          node_json: dict = None) -> str:
    """Adds a single node to a Blueprint graph."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if node_json is None:
        return json.dumps({"success": False, "message": "Required parameter 'node_json' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        node_json_str = json.dumps(node_json)
        result_json = unreal.MCPythonHelper.add_blueprint_node(bp, graph_name, node_json_str)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_connect_blueprint_pins(asset_path: str = None, graph_name: str = "EventGraph",
                              source_node: str = None, source_pin: str = None,
                              target_node: str = None, target_pin: str = None) -> str:
    """Connects two pins in a Blueprint graph."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    for name, val in [("source_node", source_node), ("source_pin", source_pin),
                      ("target_node", target_node), ("target_pin", target_pin)]:
        if val is None:
            return json.dumps({"success": False, "message": f"Required parameter '{name}' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.connect_blueprint_pins(
            bp, graph_name, source_node, source_pin, target_node, target_pin)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_remove_blueprint_node(asset_path: str = None, graph_name: str = "EventGraph",
                             node_name: str = None) -> str:
    """Removes a node from a Blueprint graph."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if node_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'node_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.remove_blueprint_node(bp, graph_name, node_name)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_build_blueprint_graph(asset_path: str = None, graph_name: str = "EventGraph",
                             graph_structure: dict = None) -> str:
    """Builds a Blueprint graph from JSON adjacency list."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if graph_structure is None:
        return json.dumps({"success": False, "message": "Required parameter 'graph_structure' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        graph_json_str = json.dumps(graph_structure)
        result_json = unreal.MCPythonHelper.build_blueprint_graph(bp, graph_name, graph_json_str)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_compile_blueprint(asset_path: str = None) -> str:
    """Compiles a Blueprint and returns the result."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.compile_blueprint(bp)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


# ─── Component Management ──────────────────────────────────────────────────────

def ue_list_blueprint_components(asset_path: str = None) -> str:
    """Lists all SCS components on a Blueprint."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        return unreal.MCPythonHelper.list_blueprint_components(bp)
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_add_component_to_blueprint(asset_path: str = None,
                                   component_class_path: str = None,
                                   component_name: str = None,
                                   location_x: float = 0.0, location_y: float = 0.0, location_z: float = 0.0,
                                   rotation_pitch: float = 0.0, rotation_yaw: float = 0.0, rotation_roll: float = 0.0,
                                   parent_component_name: str = "") -> str:
    """Adds a component to a Blueprint's SCS."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if component_class_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'component_class_path' is missing."})
    if component_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'component_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result = unreal.MCPythonHelper.add_component_to_blueprint(
            bp, component_class_path, component_name,
            location_x, location_y, location_z,
            rotation_pitch, rotation_yaw, rotation_roll,
            parent_component_name or ""
        )
        unreal.EditorAssetLibrary.save_asset(bp.get_path_name(), only_if_is_dirty=False)
        return result
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_remove_component_from_blueprint(asset_path: str = None, component_name: str = None) -> str:
    """Removes a component by variable name from a Blueprint's SCS."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if component_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'component_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result = unreal.MCPythonHelper.remove_component_from_blueprint(bp, component_name)
        unreal.EditorAssetLibrary.save_asset(bp.get_path_name(), only_if_is_dirty=False)
        return result
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_set_component_property(asset_path: str = None, component_name: str = None,
                               property_name: str = None, value: str = None) -> str:
    """Sets a property on a component template in a Blueprint's SCS."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if component_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'component_name' is missing."})
    if property_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'property_name' is missing."})
    if value is None:
        return json.dumps({"success": False, "message": "Required parameter 'value' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result = unreal.MCPythonHelper.set_component_property(bp, component_name, property_name, value)
        unreal.EditorAssetLibrary.save_asset(bp.get_path_name(), only_if_is_dirty=False)
        return result
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


# ─── Graph Auto-Layout ─────────────────────────────────────────────────────────

def ue_set_blueprint_node_position(asset_path: str = None, graph_name: str = "EventGraph",
                                    node_name: str = None, pos_x: float = 0.0, pos_y: float = 0.0) -> str:
    """Sets the canvas position of a node in a Blueprint graph."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if node_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'node_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        return unreal.MCPythonHelper.set_blueprint_node_position(bp, graph_name, node_name, pos_x, pos_y)
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_auto_layout_graph(asset_path: str = None, graph_name: str = "EventGraph",
                          x_step: float = 380.0, y_step: float = 200.0) -> str:
    """Auto-lays out all nodes in a Blueprint graph using unified exec+data DAG
    topological sort. Pure/data nodes (math, conversions, VariableGet) are placed
    at correct column depth based on data-flow distance from the exec spine."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err

        graph_info_str = unreal.MCPythonHelper.get_blueprint_graph_info(bp, graph_name)
        graph_info = json.loads(graph_info_str)
        if not graph_info.get("success"):
            return graph_info_str

        nodes = graph_info.get("nodes", [])
        if not nodes:
            return json.dumps({"success": True, "message": "No nodes to lay out.", "positioned": 0})

        node_names = [n["node_name"] for n in nodes]
        name_set = set(node_names)

        # Classify nodes: EXEC (has exec pins) vs PURE (data-only)
        ENTRY_CLASSES = {"K2Node_Event", "K2Node_CustomEvent", "K2Node_InputKey",
                         "K2Node_InputAction", "K2Node_FunctionEntry"}

        is_exec = {}
        is_entry = {}
        for node in nodes:
            n = node["node_name"]
            has_exec = False
            for pin in node.get("pins", []):
                if pin.get("type") == "exec":
                    has_exec = True
                    break
            is_exec[n] = has_exec
            node_class = node.get("node_class", "")
            is_entry[n] = any(et in node_class for et in ENTRY_CLASSES)

        # Phase 2: Build unified dependency graph from ALL output pins
        in_degree = {n: 0 for n in node_names}
        successors = {n: [] for n in node_names}

        for node in nodes:
            node_name = node["node_name"]
            for pin in node.get("pins", []):
                if pin.get("direction") != "Output":
                    continue
                for link in pin.get("linked_to", []):
                    target = link.get("node_name", "")
                    if target in name_set and target != node_name:
                        if target not in successors[node_name]:
                            successors[node_name].append(target)
                            in_degree[target] += 1

        # Phase 3: Topological sort — column assignment
        column = {}
        queue = deque()
        queued_or_processed = set()

        # Entry nodes are always column 0
        for n in node_names:
            if is_entry[n]:
                column[n] = 0
                queue.append(n)
                queued_or_processed.add(n)

        # Also seed with nodes that have no incoming connections
        for n in node_names:
            if in_degree[n] == 0 and n not in queued_or_processed:
                column[n] = 0
                queue.append(n)
                queued_or_processed.add(n)

        while queue:
            n = queue.popleft()
            for s in successors[n]:
                new_col = column[n] + 1
                if column.get(s, -1) < new_col:
                    column[s] = new_col
                in_degree[s] -= 1
                if in_degree[s] <= 0 and s not in queued_or_processed:
                    queue.append(s)
                    queued_or_processed.add(s)

        # Any nodes still unplaced (disconnected) go in column 0
        for n in node_names:
            if n not in column:
                column[n] = 0

        # Phase 4: Compute "exec affinity" for subgraph grouping
        # For each node, find which exec spine node its data ultimately flows into.
        # We trace forward through data connections until hitting an exec node.
        def find_affinity(start_name, max_depth=20):
            """Find the nearest downstream exec node by following output links."""
            visited = set()
            q = deque([(start_name, 0)])
            while q:
                name, depth = q.popleft()
                if depth > max_depth:
                    break
                if is_exec.get(name) and name != start_name:
                    return name
                for s in successors.get(name, []):
                    if s not in visited:
                        visited.add(s)
                        q.append((s, depth + 1))
            return None

        node_affinity = {}
        for n in node_names:
            aff = find_affinity(n)
            node_affinity[n] = aff or ""

        # Phase 5: Row assignment within each column, grouped by affinity
        # Collect nodes per column
        col_nodes = {}
        for n in node_names:
            c = column[n]
            col_nodes.setdefault(c, []).append(n)

        positions = {}
        for c in sorted(col_nodes.keys()):
            col_list = col_nodes[c]
            # Sort: entry nodes first, then by affinity, then by name
            col_list.sort(key=lambda n: (
                not is_entry.get(n, False),      # entries first
                node_affinity.get(n, ""),         # group by affinity
                n                                  # then by name
            ))

            row = 0
            prev_affinity = None
            group_gap = y_step * 0.5  # extra gap between different affinity groups

            for n in col_list:
                aff = node_affinity.get(n, "")
                if prev_affinity is not None and aff != prev_affinity and prev_affinity != "" and aff != "":
                    row += 1  # add extra row gap between different subgraphs
                prev_affinity = aff

                positions[n] = (c * x_step, row * y_step)
                row += 1

        # Phase 6: Apply positions
        errors = []
        positioned = 0
        for n, (px, py) in positions.items():
            result_str = unreal.MCPythonHelper.set_blueprint_node_position(bp, graph_name, n, px, py)
            result = json.loads(result_str)
            if result.get("success"):
                positioned += 1
            else:
                errors.append(f"{n}: {result.get('message', '?')}")

        return json.dumps({
            "success": True,
            "positioned": positioned,
            "total": len(node_names),
            "columns": len(col_nodes),
            "max_column": max(column.values()) if column else 0,
            "errors": errors,
            "message": f"Auto-layout complete: {positioned}/{len(node_names)} nodes in {len(col_nodes)} columns.",
        })
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


# ─── Variable Lifecycle ────────────────────────────────────────────────────────

def ue_add_blueprint_variable(asset_path: str = None, var_name: str = None,
                               var_type: str = "bool",
                               var_sub_type: str = "",
                               is_array: bool = False,
                               default_value: str = "") -> str:
    """Adds a new variable to a Blueprint. Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if var_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'var_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.add_blueprint_variable(
            bp, var_name, var_type, var_sub_type, is_array, default_value)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_remove_blueprint_variable(asset_path: str = None, var_name: str = None) -> str:
    """Removes a variable from a Blueprint by name. Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if var_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'var_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.remove_blueprint_variable(bp, var_name)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_set_blueprint_variable_property(asset_path: str = None, var_name: str = None,
                                        property: str = None, value: str = None) -> str:
    """Sets a property on a Blueprint variable. Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if var_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'var_name' is missing."})
    if property is None:
        return json.dumps({"success": False, "message": "Required parameter 'property' is missing."})
    if value is None:
        return json.dumps({"success": False, "message": "Required parameter 'value' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.set_blueprint_variable_property(bp, var_name, property, value)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


# ─── Expose Existing C++ Functions ──────────────────────────────────────────────

def ue_set_blueprint_cdo_property(asset_path: str = None, property_name: str = None,
                                   value: str = None) -> str:
    """Sets a CDO property on a Blueprint, including inherited C++ UPROPERTYs.
    Uses TFieldIterator with IncludeSuper to bypass Python set_editor_property limitations.
    Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if property_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'property_name' is missing."})
    if value is None:
        return json.dumps({"success": False, "message": "Required parameter 'value' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.set_blueprint_cdo_property(bp, property_name, value)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_set_blueprint_node_pin_default(asset_path: str = None, graph_name: str = "EventGraph",
                                       node_name: str = None, pin_name: str = None,
                                       value: str = None) -> str:
    """Sets the default value of a pin on a Blueprint graph node.
    For object-type pins, Value should be an asset path.
    For numeric/bool pins, Value is the literal string.
    Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if node_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'node_name' is missing."})
    if pin_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'pin_name' is missing."})
    if value is None:
        return json.dumps({"success": False, "message": "Required parameter 'value' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.set_blueprint_node_pin_default(
            bp, graph_name, node_name, pin_name, value)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


# ─── Function Graph Management ──────────────────────────────────────────────────

def ue_list_function_graphs(asset_path: str = None) -> str:
    """Lists all function graphs in a Blueprint. Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.list_function_graphs(bp)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_add_function_graph(asset_path: str = None, func_name: str = None) -> str:
    """Creates a new function graph in a Blueprint. Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if func_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'func_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.add_function_graph(bp, func_name)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_create_blueprint(asset_path: str = None, parent_class_path: str = "/Script/Engine.Actor") -> str:
    """Creates a new Blueprint asset in the content browser with a specified parent class.

    :param asset_path: Full path for the new Blueprint (e.g., '/Game/Blueprints/BP_MyActor').
    :param parent_class_path: Parent class path (e.g., '/Script/Engine.Actor' for C++ or
                              '/Game/Blueprints/BP_Base.BP_Base_C' for a Blueprint class).
    :return: JSON string with creation result.
    """
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        # Parse asset_path: /Game/Folder/AssetName or /Game/Folder/AssetName.AssetName
        clean_path = asset_path
        if "." in asset_path:
            # Has .AssetName suffix — use the part before the dot as package+name
            clean_path = asset_path.rsplit(".", 1)[0]

        parts = clean_path.rsplit("/", 1)
        if len(parts) != 2:
            return json.dumps({"success": False, "message": f"Invalid asset_path format: {asset_path}"})
        package_path = parts[0]
        asset_name = parts[1]

        # Load parent class
        parent_class = unreal.load_class(name=parent_class_path)
        if not parent_class:
            return json.dumps({"success": False, "message": f"Failed to load parent class: {parent_class_path}"})

        # Create factory with parent class
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("ParentClass", parent_class)

        # Create the Blueprint asset
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        new_bp = asset_tools.create_asset(asset_name, package_path, unreal.Blueprint, factory)

        if new_bp:
            unreal.EditorAssetLibrary.save_asset(new_bp.get_path_name())
            bp_path = new_bp.get_path_name()
            return json.dumps({
                "success": True,
                "asset_path": bp_path,
                "parent_class": parent_class_path,
                "message": f"Blueprint created at {bp_path} with parent {parent_class_path}"
            })
        else:
            return json.dumps({"success": False, "message": f"Failed to create Blueprint at {asset_path}. Check if parent class is valid."})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_remove_function_graph(asset_path: str = None, func_name: str = None) -> str:
    """Removes a function graph from a Blueprint by name. Returns JSON."""
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if func_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'func_name' is missing."})
    try:
        bp, err = _load_asset(asset_path, unreal.Blueprint)
        if err:
            return err
        result_json = unreal.MCPythonHelper.remove_function_graph(bp, func_name)
        return result_json
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})
