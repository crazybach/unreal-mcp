# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Asset Tools

from typing import Annotated, Optional, List
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action, ToolInputError

ASSET_ACTIONS_MODULE = "UnrealMCPython.asset_actions"

asset_mcp = FastMCP(name="AssetMCP", description="Tools for managing and querying Unreal Engine assets.")

@asset_mcp.tool(
    name="find",
    description="Finds Unreal Engine assets by name and/or type within the project's /Game directory. At least one of name or asset_type must be provided.",
    tags={"unreal", "asset", "search", "content-browser"}
)
async def find_by_query(
    name: Annotated[Optional[str], Field(description="Substring to match in asset names. Case-insensitive.", min_length=1)] = None,
    asset_type: Annotated[Optional[str], Field(description="Unreal class name of the asset type to filter by (e.g., 'StaticMesh', 'Blueprint').", min_length=1)] = None
) -> dict:
    """Finds Unreal Engine assets by name and/or type."""
    if name is None and asset_type is None:
        raise ToolInputError("At least one of 'name' or 'asset_type' must be provided.")

    params = {"name": name, "asset_type": asset_type}
    return await send_unreal_action(ASSET_ACTIONS_MODULE, params)

@asset_mcp.tool(
    name="get_static_mesh_details",
    description="Retrieves details for a static mesh asset, including its bounding box and dimensions.",
    tags={"unreal", "asset", "staticmesh", "details", "geometry"}
)
async def get_static_mesh_details(
    asset_path: Annotated[str, Field(description="Path to the static mesh asset (e.g., '/Game/Meshes/MyCube.MyCube').", min_length=1)]
) -> dict:
    """Retrieves details for a static mesh asset."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(ASSET_ACTIONS_MODULE, params)


@asset_mcp.tool(
    name="create_folder",
    description="Creates a new folder in the Unreal Engine content browser at the specified path.",
    tags={"unreal", "asset", "folder", "create", "content-browser"}
)
async def create_folder(
    folder_path: Annotated[str, Field(description="Path for the new folder (e.g., '/Game/MyFolder').", min_length=1)]
) -> dict:
    """Creates a folder in the content browser."""
    params = {"folder_path": folder_path}
    return await send_unreal_action(ASSET_ACTIONS_MODULE, params)


@asset_mcp.tool(
    name="duplicate_asset",
    description="Duplicates an asset in the Unreal Engine content browser to a new path. "
                "The destination path must include both the package path and asset name "
                "(e.g., '/Game/Folder/NewAssetName.NewAssetName').",
    tags={"unreal", "asset", "duplicate", "copy", "content-browser"}
)
async def duplicate_asset(
    source_asset_path: Annotated[str, Field(description="Path to the source asset (e.g., '/Game/Meshes/MyMesh.MyMesh').", min_length=1)],
    destination_path: Annotated[str, Field(description="Full destination path including asset name (e.g., '/Game/Meshes/MyMesh_Copy.MyMesh_Copy').", min_length=1)],
) -> dict:
    """Duplicates an asset to a new path."""
    params = {"source_asset_path": source_asset_path, "destination_path": destination_path}
    return await send_unreal_action(ASSET_ACTIONS_MODULE, params)
