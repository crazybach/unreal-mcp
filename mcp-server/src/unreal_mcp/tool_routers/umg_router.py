# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for UMG (Unreal Motion Graphics) Widget Tools

from typing import Annotated, Optional
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action, ToolInputError

UMG_ACTIONS_MODULE = "UnrealMCPython.umg_actions"

umg_mcp = FastMCP(name="UmgMCP", description="Tools for creating and editing UMG Widget Blueprints in Unreal Engine.")

@umg_mcp.tool(
    name="create_widget_blueprint",
    description="Creates a new UMG Widget Blueprint asset at the specified content browser path.",
    tags={"unreal", "umg", "widget", "blueprint", "create"}
)
async def create_widget_blueprint(
    name: Annotated[str, Field(description="Name of the new Widget Blueprint asset.", min_length=1)],
    path: Annotated[str, Field(description="Content browser path where the asset will be created (e.g., '/Game/UI').", min_length=1)],
    parent_class: Annotated[Optional[str], Field(description="Parent class name for the widget (default: 'UserWidget').")] = "UserWidget"
) -> dict:
    """Creates a new Widget Blueprint asset."""
    params = {"name": name, "path": path, "parent_class": parent_class}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="get_widget_blueprint_info",
    description="Returns the widget tree hierarchy and widget list of an existing Widget Blueprint.",
    tags={"unreal", "umg", "widget", "info", "hierarchy"}
)
async def get_widget_blueprint_info(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint (e.g., '/Game/UI/MyWidget.MyWidget').", min_length=1)]
) -> dict:
    """Returns widget tree info for a Widget Blueprint."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="add_widget",
    description=(
        "Adds a new widget component to a Widget Blueprint's widget tree. "
        "Supported widget_type values: CanvasPanel, TextBlock, Button, Image, "
        "HorizontalBox, VerticalBox, Border, Overlay, ScrollBox, SizeBox, "
        "CheckBox, EditableText, EditableTextBox, ProgressBar, Slider."
    ),
    tags={"unreal", "umg", "widget", "add", "hierarchy"}
)
async def add_widget(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)],
    widget_type: Annotated[str, Field(description="Type of widget to add (e.g., 'TextBlock', 'Button', 'CanvasPanel').", min_length=1)],
    widget_name: Annotated[str, Field(description="Unique name for the new widget within the blueprint.", min_length=1)],
    parent_name: Annotated[Optional[str], Field(description="Name of the parent panel widget. If omitted, the widget becomes the root or is added to the existing root panel.")] = None
) -> dict:
    """Adds a widget component to a Widget Blueprint."""
    params = {"asset_path": asset_path, "widget_type": widget_type, "widget_name": widget_name, "parent_name": parent_name}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="set_widget_properties",
    description=(
        "Sets properties on a widget within a Widget Blueprint. "
        "Common widget properties: text (str), visibility (str: visible/collapsed/hidden/hit_test_invisible/self_hit_test_invisible), "
        "color_and_opacity ([r,g,b,a]), brush_color ([r,g,b,a] — Border widgets only), font_size (int), hint_text (str), percent (float). "
        "Canvas slot properties (when parent is CanvasPanel): slot_position ([x,y]), slot_size ([w,h]), "
        "slot_alignment ([x,y]), slot_z_order (int)."
    ),
    tags={"unreal", "umg", "widget", "properties", "set"}
)
async def set_widget_properties(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)],
    widget_name: Annotated[str, Field(description="Name of the widget to modify.", min_length=1)],
    properties: Annotated[dict, Field(description="Dictionary of property names to values to set on the widget.")]
) -> dict:
    """Sets properties on a widget in a Widget Blueprint."""
    if not properties:
        raise ToolInputError("'properties' must be a non-empty dictionary.")
    params = {"asset_path": asset_path, "widget_name": widget_name, "properties": properties}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="remove_widget",
    description="Removes a widget from the Widget Blueprint's widget tree.",
    tags={"unreal", "umg", "widget", "remove", "delete"}
)
async def remove_widget(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)],
    widget_name: Annotated[str, Field(description="Name of the widget to remove.", min_length=1)]
) -> dict:
    """Removes a widget from a Widget Blueprint."""
    params = {"asset_path": asset_path, "widget_name": widget_name}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="compile_widget_blueprint",
    description="Compiles a Widget Blueprint and returns the compilation result.",
    tags={"unreal", "umg", "widget", "compile"}
)
async def compile_widget_blueprint(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)]
) -> dict:
    """Compiles a Widget Blueprint."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="set_slot_layout",
    description=(
        "Sets the CanvasPanelSlot layout on a widget in one call. "
        "anchor_min/max are 0..1 fractions of the canvas (e.g. 0.5,0.5 = centre). "
        "offset_x/y are pixel offsets from the anchor point. "
        "size_x/y are the widget's pixel dimensions. "
        "Alignment is always (0.5, 0.5) — the anchor lands at the widget centre."
    ),
    tags={"unreal", "umg", "widget", "layout", "position", "anchor", "canvas"}
)
async def set_slot_layout(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)],
    widget_name: Annotated[str, Field(description="Name of the widget to reposition.", min_length=1)],
    anchor_min_x: Annotated[float, Field(description="Minimum anchor X (0..1).")] = 0.5,
    anchor_min_y: Annotated[float, Field(description="Minimum anchor Y (0..1).")] = 0.5,
    anchor_max_x: Annotated[float, Field(description="Maximum anchor X (0..1). Same as min for point anchors.")] = 0.5,
    anchor_max_y: Annotated[float, Field(description="Maximum anchor Y (0..1). Same as min for point anchors.")] = 0.5,
    offset_x: Annotated[float, Field(description="Pixel X offset from anchor (positive = right).")] = 0.0,
    offset_y: Annotated[float, Field(description="Pixel Y offset from anchor (positive = down).")] = 0.0,
    size_x: Annotated[float, Field(description="Widget width in pixels.")] = 100.0,
    size_y: Annotated[float, Field(description="Widget height in pixels.")] = 40.0,
) -> dict:
    """Sets CanvasPanelSlot layout on a widget."""
    params = {
        "asset_path": asset_path, "widget_name": widget_name,
        "anchor_min_x": anchor_min_x, "anchor_min_y": anchor_min_y,
        "anchor_max_x": anchor_max_x, "anchor_max_y": anchor_max_y,
        "offset_x": offset_x, "offset_y": offset_y,
        "size_x": size_x, "size_y": size_y,
    }
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="set_text_style",
    description=(
        "Sets the font size, text color, and outline size on a TextBlock widget in one call. "
        "Colors are linear 0..1 values. outline_size=-1 leaves the outline unchanged."
    ),
    tags={"unreal", "umg", "widget", "text", "font", "color", "style"}
)
async def set_text_style(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)],
    widget_name: Annotated[str, Field(description="Name of the TextBlock widget.", min_length=1)],
    font_size: Annotated[int, Field(description="Font size in points.")] = 24,
    color_r: Annotated[float, Field(description="Red channel (0..1).")] = 1.0,
    color_g: Annotated[float, Field(description="Green channel (0..1).")] = 1.0,
    color_b: Annotated[float, Field(description="Blue channel (0..1).")] = 1.0,
    color_a: Annotated[float, Field(description="Alpha channel (0..1).")] = 1.0,
    outline_size: Annotated[int, Field(description="Outline size in pixels. Pass -1 to leave unchanged.")] = 0,
) -> dict:
    """Sets font size, color, and outline on a TextBlock."""
    params = {
        "asset_path": asset_path, "widget_name": widget_name,
        "font_size": font_size,
        "color_r": color_r, "color_g": color_g, "color_b": color_b, "color_a": color_a,
        "outline_size": outline_size,
    }
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="get_widget_property",
    description=(
        "Gets the value of a C++ UPROPERTY on a named widget. "
        "property_name must be the C++ member name (PascalCase), e.g. 'Text', 'bIsEnabled', 'ColorAndOpacity'. "
        "Returns the value as a string along with the C++ type name."
    ),
    tags={"unreal", "umg", "widget", "property", "get", "inspect"}
)
async def get_widget_property(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)],
    widget_name: Annotated[str, Field(description="Name of the target widget.", min_length=1)],
    property_name: Annotated[str, Field(description="C++ UPROPERTY name (PascalCase), e.g. 'Text', 'bIsEnabled', 'ColorAndOpacity'.", min_length=1)]
) -> dict:
    """Gets a C++ UPROPERTY value from a widget."""
    params = {"asset_path": asset_path, "widget_name": widget_name, "property_name": property_name}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)


@umg_mcp.tool(
    name="set_widget_property",
    description=(
        "Sets a simple C++ UPROPERTY on a named widget from a string value. "
        "property_name must be the C++ member name (PascalCase), e.g. 'Text', 'bIsEnabled'. "
        "Supports bool ('True'/'False'), int, float, FText, and FString properties. "
        "For struct properties (layout, font), use set_slot_layout or set_text_style instead."
    ),
    tags={"unreal", "umg", "widget", "property", "set"}
)
async def set_widget_property(
    asset_path: Annotated[str, Field(description="Full content path to the Widget Blueprint.", min_length=1)],
    widget_name: Annotated[str, Field(description="Name of the target widget.", min_length=1)],
    property_name: Annotated[str, Field(description="C++ UPROPERTY name (PascalCase), e.g. 'Text', 'bIsEnabled', 'ToolTipText'.", min_length=1)],
    value: Annotated[str, Field(description="String representation of the value to set.", min_length=0)]
) -> dict:
    """Sets a C++ UPROPERTY on a widget from a string."""
    params = {"asset_path": asset_path, "widget_name": widget_name, "property_name": property_name, "value": value}
    return await send_unreal_action(UMG_ACTIONS_MODULE, params)
