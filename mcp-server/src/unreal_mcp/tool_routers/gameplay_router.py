# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Gameplay Ability System Tools

from typing import Annotated, Optional
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action

GAMEPLAY_ACTIONS_MODULE = "UnrealMCPython.gameplay_actions"

gameplay_mcp = FastMCP(
    name="GameplayMCP",
    description="Tools for managing GameplayAbility System assets in Unreal Engine."
)


@gameplay_mcp.tool(
    name="set_gameplay_effect_properties",
    description="Sets properties on a GameplayEffect Blueprint asset. "
                "Supports: duration_policy ('Instant'/'Infinite'/'HasDuration'), "
                "stacking_type ('None'/'AggregateBySource'/'AggregateByTarget'), "
                "stack_limit_count (int), stack_expiration_policy, period, "
                "and inherited_ownable_tags for adding/removing gameplay tags. "
                "Loads the GE CDO, sets properties, and saves the asset.",
    tags={"unreal", "gameplay", "gameplayeffect", "property", "set", "write"}
)
async def set_gameplay_effect_properties(
    asset_path: Annotated[str, Field(description="Path to the GameplayEffect Blueprint asset (e.g., '/Game/GE_MyEffect.GE_MyEffect').")],
    properties: Annotated[dict, Field(description="Dictionary of property names and values to set. "
                                                  "Keys: duration_policy, stacking_type, stack_limit_count, "
                                                  "stack_expiration_policy, period, inherited_ownable_tags.")],
) -> dict:
    """Sets properties on a GameplayEffect."""
    params = {"asset_path": asset_path, "properties": properties}
    return await send_unreal_action(GAMEPLAY_ACTIONS_MODULE, params)
