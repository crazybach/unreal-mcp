# Copyright (c) 2025 GenOrca. All Rights Reserved.

import unreal
import json
import traceback


def ue_set_gameplay_effect_properties(asset_path: str = None, properties: dict = None) -> str:
    """Sets properties on a GameplayEffect Blueprint asset.

    Loads the GameplayEffect Blueprint, gets its CDO (Class Default Object),
    and sets the specified properties via set_editor_property.

    :param asset_path: Path to the GameplayEffect Blueprint (e.g., '/Game/GE_MyEffect.GE_MyEffect').
    :param properties: Dictionary of property names to values.
        Supported properties:
        - duration_policy (str): "Instant", "Infinite", "HasDuration"
        - duration_magnitude (dict): {"base_magnitude": float, "magnitude_calculation_type": str}
        - stacking_type (str): "None", "AggregateBySource", "AggregateByTarget"
        - stack_limit_count (int): Max stack count
        - stack_duration_refresh_policy (str): "NeverRefresh", "RefreshOnSuccessfulApplication"
        - stack_period_reset_policy (str): "NeverReset", "ResetOnSuccessfulApplication"
        - stack_expiration_policy (str): "ClearEntireStack", "RemoveSingleStackAndRefreshDuration", "RemoveSingleStack"
        - period (float): Period between executions (0 = no periodic effect) — sets ScalableFloat.Value
        - inherited_ownable_tags (dict): {"added": [{"tag_name": "Tag.Name"}]} for adding tags
          or {"removed": [{"tag_name": "Tag.Name"}]} for removing tags.
          Uses InheritableOwnedTagsContainer (UE 5.x property name).
    :return: JSON string with result.
    """
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if properties is None:
        return json.dumps({"success": False, "message": "Required parameter 'properties' is missing."})

    try:
        # Load the GameplayEffect Blueprint
        bp = unreal.EditorAssetLibrary.load_asset(asset_path)
        if not bp:
            return json.dumps({"success": False, "message": f"Asset not found: {asset_path}"})

        # Get the generated class and CDO
        generated_class = bp.generated_class()
        if not generated_class:
            return json.dumps({"success": False, "message": f"No generated class found for {asset_path}"})

        cdo = unreal.get_default_object(generated_class)
        if not cdo:
            return json.dumps({"success": False, "message": f"Failed to get CDO for {asset_path}"})

        results = {}
        errors = []

        for prop_name, prop_value in properties.items():
            try:
                if prop_name == "duration_policy":
                    # Map string to EGameplayEffectDurationType enum
                    policy_map = {
                        "Instant": unreal.GameplayEffectDurationType.INSTANT,
                        "Infinite": unreal.GameplayEffectDurationType.INFINITE,
                        "HasDuration": unreal.GameplayEffectDurationType.HAS_DURATION,
                    }
                    if isinstance(prop_value, str) and prop_value in policy_map:
                        cdo.set_editor_property("duration_policy", policy_map[prop_value])
                        results[prop_name] = prop_value
                    else:
                        errors.append(f"Invalid duration_policy: {prop_value}")

                elif prop_name == "stacking_type":
                    stack_map = {
                        "None": unreal.GameplayEffectStackingType.NONE,
                        "AggregateBySource": unreal.GameplayEffectStackingType.AGGREGATE_BY_SOURCE,
                        "AggregateByTarget": unreal.GameplayEffectStackingType.AGGREGATE_BY_TARGET,
                    }
                    if isinstance(prop_value, str) and prop_value in stack_map:
                        cdo.set_editor_property("stacking_type", stack_map[prop_value])
                        results[prop_name] = prop_value
                    else:
                        errors.append(f"Invalid stacking_type: {prop_value}")

                elif prop_name == "stack_limit_count":
                    cdo.set_editor_property("stack_limit_count", int(prop_value))
                    results[prop_name] = int(prop_value)

                elif prop_name == "stack_duration_refresh_policy":
                    policy_map = {
                        "NeverRefresh": unreal.GameplayEffectStackDurationPolicy.NEVER_REFRESH,
                        "RefreshOnSuccessfulApplication": unreal.GameplayEffectStackDurationPolicy.REFRESH_ON_SUCCESSFUL_APPLICATION,
                    }
                    if isinstance(prop_value, str) and prop_value in policy_map:
                        cdo.set_editor_property("stack_duration_refresh_policy", policy_map[prop_value])
                        results[prop_name] = prop_value
                    else:
                        errors.append(f"Invalid stack_duration_refresh_policy: {prop_value}")

                elif prop_name == "stack_period_reset_policy":
                    policy_map = {
                        "NeverReset": unreal.GameplayEffectStackPeriodPolicy.NEVER_RESET,
                        "ResetOnSuccessfulApplication": unreal.GameplayEffectStackPeriodPolicy.RESET_ON_SUCCESSFUL_APPLICATION,
                    }
                    if isinstance(prop_value, str) and prop_value in policy_map:
                        cdo.set_editor_property("stack_period_reset_policy", policy_map[prop_value])
                        results[prop_name] = prop_value
                    else:
                        errors.append(f"Invalid stack_period_reset_policy: {prop_value}")

                elif prop_name == "stack_expiration_policy":
                    policy_map = {
                        "ClearEntireStack": unreal.GameplayEffectStackExpirationPolicy.CLEAR_ENTIRE_STACK,
                        "RemoveSingleStackAndRefreshDuration": unreal.GameplayEffectStackExpirationPolicy.REMOVE_SINGLE_STACK_AND_REFRESH_DURATION,
                        "RemoveSingleStack": unreal.GameplayEffectStackExpirationPolicy.REMOVE_SINGLE_STACK,
                    }
                    if isinstance(prop_value, str) and prop_value in policy_map:
                        cdo.set_editor_property("stack_expiration_policy", policy_map[prop_value])
                        results[prop_name] = prop_value
                    else:
                        errors.append(f"Invalid stack_expiration_policy: {prop_value}")

                elif prop_name == "period":
                    period_struct = cdo.get_editor_property("period")
                    if period_struct is None:
                        errors.append("Could not read period from CDO")
                        continue
                    period_struct.set_editor_property("value", float(prop_value))
                    cdo.set_editor_property("period", period_struct)
                    results[prop_name] = float(prop_value)

                elif prop_name == "inherited_ownable_tags":
                    # Handle tag addition/removal via InheritableOwnedTagsContainer
                    tag_container = cdo.get_editor_property("InheritableOwnedTagsContainer")
                    if tag_container is None:
                        errors.append("Could not read InheritableOwnedTagsContainer from CDO")
                        continue

                    if "added" in prop_value:
                        added = tag_container.get_editor_property("added")
                        existing_text = added.export_text() if added else "()"
                        export_parts = []
                        for tag_entry in prop_value["added"]:
                            tag_name = tag_entry.get("tag_name", "")
                            if tag_name:
                                export_parts.append(f'(TagName="{tag_name}")')
                                results.setdefault("tags_added", []).append(tag_name)
                        # Build new container via import_text
                        new_text = existing_text.replace("))", ")")
                        for ep in export_parts:
                            new_text += f",{ep})"
                        if not new_text.endswith(")"):
                            new_text += ")"
                        new_added = unreal.GameplayTagContainer()
                        new_added.import_text(new_text)
                        tag_container.set_editor_property("added", new_added)

                    if "removed" in prop_value:
                        removed = tag_container.get_editor_property("removed")
                        existing_text = removed.export_text() if removed else "()"
                        remove_names = {e.get("tag_name", "") for e in prop_value["removed"]}
                        # Rebuild without removed tags
                        keep = []
                        for i in range(len(removed.gameplay_tags)):
                            tag_text = removed.gameplay_tags[i].export_text()
                            tag_name = tag_text.split('"')[1] if '"' in tag_text else ""
                            if tag_name not in remove_names:
                                keep.append(f'(TagName="{tag_name}")')
                            else:
                                results.setdefault("tags_removed", []).append(tag_name)
                        new_removed = unreal.GameplayTagContainer()
                        new_removed.import_text(f'((GameplayTags=({",".join(keep)})))' if keep else "()")
                        tag_container.set_editor_property("removed", new_removed)

                    cdo.set_editor_property("InheritableOwnedTagsContainer", tag_container)

                elif prop_name == "duration_magnitude":
                    if isinstance(prop_value, dict):
                        magnitude = cdo.get_editor_property("duration_magnitude")
                        if magnitude is None:
                            errors.append("Could not read duration_magnitude from CDO")
                            continue
                        if "base_magnitude" in prop_value:
                            fs = magnitude.get_editor_property("scalable_float_magnitude")
                            if fs:
                                fs.set_editor_property("value", float(prop_value["base_magnitude"]))
                                magnitude.set_editor_property("scalable_float_magnitude", fs)
                        if "magnitude_calculation_type" in prop_value:
                            calc_map = {
                                "ScalableFloat": unreal.GameplayEffectMagnitudeCalculation.SCALABLE_FLOAT,
                                "AttributeBased": unreal.GameplayEffectMagnitudeCalculation.ATTRIBUTE_BASED,
                                "CustomCalculationClass": unreal.GameplayEffectMagnitudeCalculation.CUSTOM_CALCULATION_CLASS,
                                "SetByCaller": unreal.GameplayEffectMagnitudeCalculation.SET_BY_CALLER,
                            }
                            calc_str = prop_value["magnitude_calculation_type"]
                            if calc_str in calc_map:
                                magnitude.set_editor_property("magnitude_calculation_type", calc_map[calc_str])
                        cdo.set_editor_property("duration_magnitude", magnitude)
                        results[prop_name] = prop_value
                    else:
                        errors.append("duration_magnitude must be a dict with base_magnitude, magnitude_calculation_type, etc.")

                else:
                    # Generic setter fallback — try direct set
                    cdo.set_editor_property(prop_name, prop_value)
                    results[prop_name] = prop_value

            except Exception as prop_err:
                errors.append(f"Failed to set '{prop_name}': {str(prop_err)}")

        # Save the asset
        unreal.EditorAssetLibrary.save_asset(bp.get_path_name())

        return json.dumps({
            "success": len(errors) == 0,
            "asset_path": asset_path,
            "results": results,
            "errors": errors,
            "message": f"Set {len(results)} properties on {asset_path}" + (f" with {len(errors)} errors" if errors else "")
        })

    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})
