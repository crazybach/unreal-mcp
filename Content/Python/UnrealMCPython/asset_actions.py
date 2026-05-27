# Copyright (c) 2025 GenOrca. All Rights Reserved.

import unreal
import json
import traceback

ASSET_ACTIONS_MODULE = "asset_actions"

def ue_find_by_query(name : str = None, asset_type : str = None) -> str:
    """
    Returns a JSON list of asset paths under '/Game' matching the given query dict.
    Supported keys: 'name' (substring match), 'asset_type' (Unreal class name, e.g. 'StaticMesh')
    At least one of name or asset_type must be provided.
    """
    if name is None and asset_type is None: # This check is specific to this function's logic
        return json.dumps({"success": False, "message": "At least one of 'name' or 'asset_type' must be provided for ue_find_by_query.", "assets": []})

    assets = unreal.EditorAssetLibrary.list_assets('/Game', recursive=True)
    matches = []
    for asset_path in assets:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
        
        current_asset_type_str = ""
        if hasattr(asset_data, 'asset_class_str') and asset_data.asset_class_str:
            current_asset_type_str = str(asset_data.asset_class_str)
        elif hasattr(asset_data, 'asset_class') and asset_data.asset_class:
            current_asset_type_str = str(asset_data.asset_class)
        else:
            # Fallback if asset class information is not directly available or named differently
            # This might happen with certain asset types or engine versions
            # unreal.log_warning(f"Could not determine asset class for {asset_path}")
            pass # Continue checking name if type is indeterminable but name is specified

        name_match = True
        if name is not None:
            name_match = name.lower() in asset_path.lower()

        type_match = True
        if asset_type is not None:
            if not current_asset_type_str: # If type couldn't be determined, it can't match a specified type
                type_match = False
            else:
                type_match = asset_type.lower() == current_asset_type_str.lower()

        if name_match and type_match:
            matches.append(asset_path)
            
    return json.dumps({"success": True, "assets": matches, "message": f"{len(matches)} assets found matching query."})

def ue_create_folder(folder_path: str = None) -> str:
    """Creates a folder in the Unreal content browser."""
    if folder_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'folder_path' is missing."})
    try:
        success = unreal.EditorAssetLibrary.make_directory(folder_path)
        if success:
            return json.dumps({"success": True, "folder_path": folder_path, "message": f"Folder created at {folder_path}"})
        else:
            return json.dumps({"success": False, "message": f"Failed to create folder at {folder_path} (may already exist)"})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_duplicate_asset(source_asset_path: str = None, destination_path: str = None) -> str:
    """Duplicates an asset in the Unreal content browser to a new path."""
    if source_asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'source_asset_path' is missing."})
    if destination_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'destination_path' is missing."})
    try:
        duplicated = unreal.EditorAssetLibrary.duplicate_asset(source_asset_path, destination_path)
        if duplicated:
            result_path = duplicated.get_path_name() if hasattr(duplicated, 'get_path_name') else str(duplicated)
            return json.dumps({"success": True, "source": source_asset_path, "destination": result_path, "message": f"Asset duplicated to {result_path}"})
        else:
            return json.dumps({"success": False, "message": f"Failed to duplicate {source_asset_path} to {destination_path}"})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})


def ue_get_static_mesh_details(asset_path: str = None) -> str:
    """
    Retrieves the bounding box and dimensions of a static mesh asset.

    :param asset_path: Path to the static mesh asset (e.g., "/Game/Meshes/MyCube.MyCube").
    :return: JSON string with asset details including bounding box and dimensions.
    """
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    try:
        static_mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
        if not static_mesh or not isinstance(static_mesh, unreal.StaticMesh):
            return json.dumps({"success": False, "message": f"Asset is not a StaticMesh or could not be loaded: {asset_path}"})

        bounds = static_mesh.get_bounding_box()  # This returns a Box type object
        
        min_point = bounds.min
        max_point = bounds.max

        dimensions = {
            "x": max_point.x - min_point.x,
            "y": max_point.y - min_point.y,
            "z": max_point.z - min_point.z
        }

        details = {
            "asset_path": asset_path,
            "bounding_box_min": {"x": min_point.x, "y": min_point.y, "z": min_point.z},
            "bounding_box_max": {"x": max_point.x, "y": max_point.y, "z": max_point.z},
            "dimensions": dimensions
        }
        return json.dumps({"success": True, "details": details})
    except Exception as e:
        tb_str = traceback.format_exc()
        unreal.log_error(f"Error in ue_get_static_mesh_details for {asset_path}: {str(e)}\n{tb_str}")
        return json.dumps({"success": False, "message": str(e), "traceback": tb_str})
