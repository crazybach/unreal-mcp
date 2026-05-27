# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Blueprint Graph Tools

from typing import Annotated, Optional
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action

BP_ACTIONS_MODULE = "UnrealMCPython.blueprint_actions"

blueprint_mcp = FastMCP(
    name="BlueprintMCP",
    description="Tools for reading and writing Blueprint graphs in Unreal Engine."
)

# ─── Read Tools ───────────────────────────────────────────────────────────────

@blueprint_mcp.tool(
    name="get_selected_bp_nodes",
    description="Gets information about currently selected blueprint nodes in the editor.",
    tags={"unreal", "blueprint", "selection", "nodes", "read"}
)
async def get_selected_bp_nodes() -> dict:
    """Gets information about currently selected blueprint nodes in the editor."""
    return await send_unreal_action(BP_ACTIONS_MODULE, {})


@blueprint_mcp.tool(
    name="get_selected_bp_node_infos",
    description="Gets detailed info (including pin connections) about currently selected blueprint nodes. "
                "Optimized for LLM/external tools with compact output format.",
    tags={"unreal", "blueprint", "selection", "nodes", "connections", "read"}
)
async def get_selected_bp_node_infos() -> dict:
    """Gets detailed info about currently selected blueprint nodes."""
    return await send_unreal_action(BP_ACTIONS_MODULE, {})


@blueprint_mcp.tool(
    name="get_blueprint_graph_info",
    description="Returns the full graph structure of a Blueprint (all nodes, pins, and connections). "
                "Use this to understand the current state of a Blueprint's event graph or function graph.",
    tags={"unreal", "blueprint", "graph", "read", "structure"}
)
async def get_blueprint_graph_info(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset (e.g., '/Game/Blueprints/BP_MyActor').")],
    graph_name: Annotated[str, Field(description="Name of the graph to read. Usually 'EventGraph'.")] = "EventGraph"
) -> dict:
    """Returns the full graph info for a Blueprint graph."""
    params = {"asset_path": asset_path, "graph_name": graph_name}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="list_callable_functions",
    description="Lists functions callable from a Blueprint context. "
                "Useful for discovering valid function_name values for add_blueprint_node with type=CallFunction. "
                "Optionally filter by keyword.",
    tags={"unreal", "blueprint", "functions", "list", "read"}
)
async def list_callable_functions(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    filter: Annotated[str, Field(description="Optional keyword filter for function/class names.")] = ""
) -> dict:
    """Lists callable functions available in a Blueprint context."""
    params = {"asset_path": asset_path, "filter": filter}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="list_blueprint_variables",
    description="Lists all variables defined in a Blueprint, including their types and default values.",
    tags={"unreal", "blueprint", "variables", "list", "read"}
)
async def list_blueprint_variables(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")]
) -> dict:
    """Lists all variables defined in a Blueprint."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


# ─── Write Tools ──────────────────────────────────────────────────────────────

@blueprint_mcp.tool(
    name="add_blueprint_node",
    description=(
        "Adds a single node to a Blueprint graph. Returns the created node name and its pins for connecting. "
        "Supported node types: "
        "CallFunction (requires function_name, optional target class), "
        "Event (requires event_name like 'ReceiveBeginPlay'), "
        "CustomEvent (requires event_name), "
        "Branch (if/else), "
        "Sequence (execution sequence), "
        "VariableGet (requires variable_name), "
        "VariableSet (requires variable_name), "
        "MacroInstance (requires macro_name like 'ForEachLoop')."
    ),
    tags={"unreal", "blueprint", "node", "add", "write"}
)
async def add_blueprint_node(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    graph_name: Annotated[str, Field(description="Name of the graph. Usually 'EventGraph'.")] = "EventGraph",
    node_type: Annotated[str, Field(description="Type of node: CallFunction, Event, CustomEvent, Branch, Sequence, VariableGet, VariableSet, MacroInstance.")] = "",
    node_config: Annotated[dict, Field(description=(
        "Node configuration. Include 'type' if not specified in node_type. "
        "For CallFunction: {function_name, target?, pin_defaults?}. "
        "For Event: {event_name}. "
        "For CustomEvent: {event_name}. "
        "For VariableGet/Set: {variable_name}. "
        "For MacroInstance: {macro_name}. "
        "Optional: pos_x, pos_y for positioning."
    ))] = {}
) -> dict:
    """Adds a single node to a Blueprint graph."""
    node_json = dict(node_config)
    if node_type and "type" not in node_json:
        node_json["type"] = node_type
    params = {"asset_path": asset_path, "graph_name": graph_name, "node_json": node_json}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="connect_blueprint_pins",
    description="Connects two pins in a Blueprint graph. Use node names from add_blueprint_node or get_blueprint_graph_info. "
                "Pin names can be found in the node's pin list (e.g., 'execute', 'then', 'ReturnValue').",
    tags={"unreal", "blueprint", "pin", "connect", "write"}
)
async def connect_blueprint_pins(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    source_node: Annotated[str, Field(description="Name of the source node.")],
    source_pin: Annotated[str, Field(description="Name of the output pin on the source node.")],
    target_node: Annotated[str, Field(description="Name of the target node.")],
    target_pin: Annotated[str, Field(description="Name of the input pin on the target node.")],
    graph_name: Annotated[str, Field(description="Name of the graph. Usually 'EventGraph'.")] = "EventGraph"
) -> dict:
    """Connects two pins in a Blueprint graph."""
    params = {
        "asset_path": asset_path,
        "graph_name": graph_name,
        "source_node": source_node,
        "source_pin": source_pin,
        "target_node": target_node,
        "target_pin": target_pin
    }
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="remove_blueprint_node",
    description="Removes a node from a Blueprint graph by name. Breaks all pin connections before removal.",
    tags={"unreal", "blueprint", "node", "remove", "delete", "write"}
)
async def remove_blueprint_node(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    node_name: Annotated[str, Field(description="Name of the node to remove.")],
    graph_name: Annotated[str, Field(description="Name of the graph. Usually 'EventGraph'.")] = "EventGraph"
) -> dict:
    """Removes a node from a Blueprint graph."""
    params = {"asset_path": asset_path, "graph_name": graph_name, "node_name": node_name}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="build_blueprint_graph",
    description=(
        "Builds a Blueprint graph from a JSON adjacency list. Removes existing non-event nodes and replaces "
        "them with the provided structure. Use get_blueprint_graph_info to read the current state first. "
        "JSON format: {nodes: [{id, type, ...}], connections: [{source_node, source_pin, target_node, target_pin}]}. "
        "Node types: CallFunction, Event, CustomEvent, Branch, Sequence, VariableGet, VariableSet, MacroInstance."
    ),
    tags={"unreal", "blueprint", "graph", "build", "write"}
)
async def build_blueprint_graph(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    graph_structure: Annotated[dict, Field(description=(
        "JSON object with 'nodes' array and 'connections' array. "
        "Each node: {id, type, function_name?, event_name?, variable_name?, macro_name?, pin_defaults?, pos_x?, pos_y?}. "
        "Each connection: {source_node, source_pin, target_node, target_pin}."
    ))],
    graph_name: Annotated[str, Field(description="Name of the graph. Usually 'EventGraph'.")] = "EventGraph"
) -> dict:
    """Builds a Blueprint graph from JSON adjacency list."""
    params = {"asset_path": asset_path, "graph_name": graph_name, "graph_structure": graph_structure}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="compile_blueprint",
    description="Compiles a Blueprint and returns the compilation result (success/error). "
                "Use after making changes to verify the Blueprint is valid.",
    tags={"unreal", "blueprint", "compile", "write"}
)
async def compile_blueprint(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")]
) -> dict:
    """Compiles a Blueprint and returns the result."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


# ─── Component Management Tools ───────────────────────────────────────────────

@blueprint_mcp.tool(
    name="list_blueprint_components",
    description=(
        "Lists all SCS (Simple Construction Script) components on a Blueprint. "
        "Returns each component's variable name, class, and parent component name."
    ),
    tags={"unreal", "blueprint", "component", "list", "read"}
)
async def list_blueprint_components(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")]
) -> dict:
    return await send_unreal_action(BP_ACTIONS_MODULE, {"asset_path": asset_path})


@blueprint_mcp.tool(
    name="add_component_to_blueprint",
    description=(
        "Adds a new component to a Blueprint's SCS. "
        "component_class_path is a fully qualified UE class path such as '/Script/Engine.SphereComponent', "
        "'/Script/Engine.CameraComponent', '/Script/Engine.StaticMeshComponent'. "
        "component_name becomes the variable name. "
        "parent_component_name: variable name of the parent SCS node, or empty to attach to the existing root."
    ),
    tags={"unreal", "blueprint", "component", "add", "write"}
)
async def add_component_to_blueprint(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    component_class_path: Annotated[str, Field(description="UE class path (e.g. '/Script/Engine.SphereComponent').")],
    component_name: Annotated[str, Field(description="Variable name for the new component.")],
    location_x: Annotated[float, Field(description="Relative X offset from parent.")] = 0.0,
    location_y: Annotated[float, Field(description="Relative Y offset from parent.")] = 0.0,
    location_z: Annotated[float, Field(description="Relative Z offset from parent.")] = 0.0,
    rotation_pitch: Annotated[float, Field(description="Relative pitch in degrees.")] = 0.0,
    rotation_yaw: Annotated[float, Field(description="Relative yaw in degrees.")] = 0.0,
    rotation_roll: Annotated[float, Field(description="Relative roll in degrees.")] = 0.0,
    parent_component_name: Annotated[str, Field(description="Variable name of the parent component, or empty for root.")] = ""
) -> dict:
    return await send_unreal_action(BP_ACTIONS_MODULE, {
        "asset_path": asset_path,
        "component_class_path": component_class_path,
        "component_name": component_name,
        "location_x": location_x,
        "location_y": location_y,
        "location_z": location_z,
        "rotation_pitch": rotation_pitch,
        "rotation_yaw": rotation_yaw,
        "rotation_roll": rotation_roll,
        "parent_component_name": parent_component_name,
    })


@blueprint_mcp.tool(
    name="remove_component_from_blueprint",
    description=(
        "Removes a component from a Blueprint's SCS by its variable name. "
        "Children of the removed node are promoted to the removed node's parent (safe remove). "
        "Use list_blueprint_components first to find the correct variable name."
    ),
    tags={"unreal", "blueprint", "component", "remove", "delete", "write"}
)
async def remove_component_from_blueprint(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    component_name: Annotated[str, Field(description="Variable name of the component to remove.")]
) -> dict:
    return await send_unreal_action(BP_ACTIONS_MODULE, {
        "asset_path": asset_path,
        "component_name": component_name,
    })


@blueprint_mcp.tool(
    name="set_component_property",
    description=(
        "Sets a property on a component template in a Blueprint's SCS. "
        "The value must be a string representation accepted by Unreal's property import: "
        "vectors as '(X=0,Y=0,Z=100)', bools as 'True'/'False', floats as '50.0'. "
        "Use list_blueprint_components to find the correct component_name first."
    ),
    tags={"unreal", "blueprint", "component", "property", "set", "write"}
)
async def set_component_property(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    component_name: Annotated[str, Field(description="Variable name of the target component.")],
    property_name: Annotated[str, Field(description="Property name (C++ name, e.g. 'SphereRadius', 'RelativeLocation').")],
    value: Annotated[str, Field(description="String representation of the value (e.g. '50.0', '(X=0,Y=0,Z=100)').")]
) -> dict:
    return await send_unreal_action(BP_ACTIONS_MODULE, {
        "asset_path": asset_path,
        "component_name": component_name,
        "property_name": property_name,
        "value": value,
    })


# ─── Graph Layout Tools ────────────────────────────────────────────────────────

@blueprint_mcp.tool(
    name="set_blueprint_node_position",
    description="Moves a single Blueprint graph node to the given canvas coordinates. "
                "Use get_blueprint_graph_info to find node names first.",
    tags={"unreal", "blueprint", "node", "position", "layout", "write"}
)
async def set_blueprint_node_position(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    node_name: Annotated[str, Field(description="Name of the node to reposition.")],
    pos_x: Annotated[float, Field(description="X position on the graph canvas.")] = 0.0,
    pos_y: Annotated[float, Field(description="Y position on the graph canvas.")] = 0.0,
    graph_name: Annotated[str, Field(description="Name of the graph. Usually 'EventGraph'.")] = "EventGraph"
) -> dict:
    return await send_unreal_action(BP_ACTIONS_MODULE, {
        "asset_path": asset_path,
        "graph_name": graph_name,
        "node_name": node_name,
        "pos_x": pos_x,
        "pos_y": pos_y,
    })


@blueprint_mcp.tool(
    name="auto_layout_graph",
    description=(
        "Automatically lays out all nodes in a Blueprint graph using topological sort. "
        "Entry nodes (BeginPlay, Tick, custom events, input events) are placed at column 0; "
        "each subsequent execution step moves one column to the right. "
        "Within a column, nodes are stacked vertically. "
        "x_step and y_step control pixel spacing between columns and rows respectively."
    ),
    tags={"unreal", "blueprint", "layout", "graph", "auto", "write"}
)
async def auto_layout_graph(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    graph_name: Annotated[str, Field(description="Name of the graph. Usually 'EventGraph'.")] = "EventGraph",
    x_step: Annotated[float, Field(description="Horizontal pixel spacing between columns.")] = 380.0,
    y_step: Annotated[float, Field(description="Vertical pixel spacing between rows.")] = 200.0,
) -> dict:
    return await send_unreal_action(BP_ACTIONS_MODULE, {
        "asset_path": asset_path,
        "graph_name": graph_name,
        "x_step": x_step,
        "y_step": y_step,
    })


# ─── Variable Lifecycle Tools ──────────────────────────────────────────────────

@blueprint_mcp.tool(
    name="add_blueprint_variable",
    description="Adds a new variable to a Blueprint. "
                "var_type supports: bool, int, float, double, string, name, text, byte, "
                "vector, rotator, transform, linear_color, object, class, softobject, softclass, "
                "interface, struct, enum. "
                "var_sub_type is the asset path for object/struct/enum types. "
                "is_array creates a TArray of the given type. "
                "default_value sets the default value as a string.",
    tags={"unreal", "blueprint", "variable", "add", "write"}
)
async def add_blueprint_variable(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    var_name: Annotated[str, Field(description="Name for the new variable.")],
    var_type: Annotated[str, Field(description="Type of the variable (e.g., 'bool', 'int', 'float', 'string', 'object', 'vector', 'rotator').")] = "bool",
    var_sub_type: Annotated[str, Field(description="Sub-type path for object/struct/enum types (e.g., '/Script/Engine.StaticMesh').")] = "",
    is_array: Annotated[bool, Field(description="Whether the variable is a TArray.")] = False,
    default_value: Annotated[str, Field(description="Default value for the variable as a string.")] = "",
) -> dict:
    """Adds a new variable to a Blueprint."""
    params = {
        "asset_path": asset_path,
        "var_name": var_name,
        "var_type": var_type,
        "var_sub_type": var_sub_type,
        "is_array": is_array,
        "default_value": default_value,
    }
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="remove_blueprint_variable",
    description="Removes a variable from a Blueprint by its name. "
                "Use list_blueprint_variables first to find valid variable names.",
    tags={"unreal", "blueprint", "variable", "remove", "delete", "write"}
)
async def remove_blueprint_variable(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    var_name: Annotated[str, Field(description="Name of the variable to remove.")],
) -> dict:
    """Removes a variable from a Blueprint."""
    params = {"asset_path": asset_path, "var_name": var_name}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="set_blueprint_variable_property",
    description="Sets a metadata property on an existing Blueprint variable. "
                "Supported properties: category, tooltip, default_value, "
                "expose_on_spawn (bool), instance_editable (bool), "
                "blueprint_read_only (bool), blueprint_read_only_owner (bool), "
                "private (bool), exposetoowner (bool). "
                "Use list_blueprint_variables first to find valid variable names.",
    tags={"unreal", "blueprint", "variable", "property", "set", "write"}
)
async def set_blueprint_variable_property(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    var_name: Annotated[str, Field(description="Name of the target variable.")],
    property: Annotated[str, Field(description="Property name to set (e.g., 'category', 'tooltip', 'expose_on_spawn').")],
    value: Annotated[str, Field(description="Value to set. For bool properties, use 'true' or 'false'.")],
) -> dict:
    """Sets a property on a Blueprint variable."""
    params = {
        "asset_path": asset_path,
        "var_name": var_name,
        "property": property,
        "value": value,
    }
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


# ─── Expose Existing C++ Tools ──────────────────────────────────────────────────

@blueprint_mcp.tool(
    name="set_blueprint_cdo_property",
    description="Sets a CDO (Class Default Object) property on a Blueprint, "
                "including inherited C++ UPROPERTYs that Python's set_editor_property "
                "cannot access. Supports: class references, object references, "
                "bool, int, float, FString, FName, FText. "
                "Useful for setting DefaultPawnClass on GameModeBase Blueprints.",
    tags={"unreal", "blueprint", "cdo", "property", "set", "write"}
)
async def set_blueprint_cdo_property(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    property_name: Annotated[str, Field(description="C++ property name (case-insensitive, e.g., 'DefaultPawnClass').")],
    value: Annotated[str, Field(description="Value string. Class paths like '/Game/BP_MyPawn.BP_MyPawn_C', booleans 'true'/'false', or literal values.")],
) -> dict:
    """Sets a CDO property on a Blueprint."""
    params = {
        "asset_path": asset_path,
        "property_name": property_name,
        "value": value,
    }
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="set_blueprint_node_pin_default",
    description="Sets the default value of a specific pin on a Blueprint graph node. "
                "For object-type pins, Value should be an asset path like "
                "'/Engine/BasicShapes/Sphere.Sphere'. "
                "For numeric/bool pins, Value is the literal string like '3.14' or 'true'. "
                "Use get_blueprint_graph_info to discover valid node and pin names.",
    tags={"unreal", "blueprint", "pin", "default", "set", "write"}
)
async def set_blueprint_node_pin_default(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    node_name: Annotated[str, Field(description="Name of the target node.")],
    pin_name: Annotated[str, Field(description="Name of the target input pin.")],
    value: Annotated[str, Field(description="Default value to set (string representation).")],
    graph_name: Annotated[str, Field(description="Name of the graph. Usually 'EventGraph'.")] = "EventGraph",
) -> dict:
    """Sets a pin default value on a Blueprint graph node."""
    params = {
        "asset_path": asset_path,
        "graph_name": graph_name,
        "node_name": node_name,
        "pin_name": pin_name,
        "value": value,
    }
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


# ─── Function Graph Management Tools ────────────────────────────────────────────

@blueprint_mcp.tool(
    name="list_function_graphs",
    description="Lists all function graphs in a Blueprint. "
                "Returns each function's name, entry node name, and node count.",
    tags={"unreal", "blueprint", "function", "list", "read"}
)
async def list_function_graphs(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
) -> dict:
    """Lists all function graphs in a Blueprint."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="add_function_graph",
    description="Creates a new function graph in a Blueprint. "
                "After creation, use add_blueprint_node with the function name as graph_name "
                "to add nodes to the function. "
                "Use build_blueprint_graph to build the entire function graph from JSON.",
    tags={"unreal", "blueprint", "function", "add", "write"}
)
async def add_function_graph(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    func_name: Annotated[str, Field(description="Name for the new function.")],
) -> dict:
    """Creates a new function graph in a Blueprint."""
    params = {"asset_path": asset_path, "func_name": func_name}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


@blueprint_mcp.tool(
    name="remove_function_graph",
    description="Removes a function graph from a Blueprint by name. "
                "Use list_function_graphs first to find valid function names. "
                "Does not update existing call sites.",
    tags={"unreal", "blueprint", "function", "remove", "delete", "write"}
)
async def remove_function_graph(
    asset_path: Annotated[str, Field(description="Path to the Blueprint asset.")],
    func_name: Annotated[str, Field(description="Name of the function to remove.")],
) -> dict:
    """Removes a function graph from a Blueprint."""
    params = {"asset_path": asset_path, "func_name": func_name}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)


# ─── Asset Creation Tool ──────────────────────────────────────────────────────────

@blueprint_mcp.tool(
    name="create_blueprint",
    description="Creates a new Blueprint asset in the content browser with a specified parent class. "
                "For C++ parent classes use '/Script/ModuleName.ClassName' (e.g., '/Script/Engine.Actor', "
                "'/Script/GameplayAbilities.GameplayEffect'). "
                "For Blueprint parent classes use the full asset path with '_C' suffix "
                "(e.g., '/Game/Blueprints/BP_Base.BP_Base_C').",
    tags={"unreal", "blueprint", "create", "asset", "content-browser"}
)
async def create_blueprint(
    asset_path: Annotated[str, Field(description="Path for the new Blueprint (e.g., '/Game/Blueprints/BP_MyActor').")],
    parent_class_path: Annotated[str, Field(description="Parent class path. For C++: '/Script/Engine.Actor'. For BP: '/Game/BP_Base.BP_Base_C'.")] = "/Script/Engine.Actor",
) -> dict:
    """Creates a new Blueprint asset."""
    params = {"asset_path": asset_path, "parent_class_path": parent_class_path}
    return await send_unreal_action(BP_ACTIONS_MODULE, params)
