# Unreal MCP — AI Usage Guide

## Core Concepts

### Input vs Output Pins in Function Graphs

This is the most important thing to understand. The Blueprint details panel shows function parameters under **Inputs** and **Outputs** sections. How it works:

| Details Panel | Blueprint Node | Pin Direction |
|---|---|---|
| **Inputs** | `K2Node_FunctionEntry` | `EGPD_Output` |
| **Outputs** | `K2Node_FunctionResult` | `EGPD_Input` |

This is counter-intuitive: pins on FunctionEntry have `EGPD_Output` direction but appear as **Inputs** in the details panel. Pins on FunctionResult have `EGPD_Input` direction but appear as **Outputs**.

**To add function parameters correctly**, use `ModifyFunctionEntry` node type:
```json
{
  "node_type": "ModifyFunctionEntry",
  "params": [
    {"name": "MyInput",  "type": "Vector",    "is_output": false},
    {"name": "MyOutput", "type": "Transform",  "is_output": true}
  ]
}
```
- `is_output: false` → goes to FunctionEntry → shows under **Inputs**
- `is_output: true`  → goes to FunctionResult → shows under **Outputs**

**Never** put output parameters on FunctionEntry. They will show under Inputs and cause compile errors.

### FunctionResult Must Be Preserved

`BuildBlueprintGraph` removes existing nodes. By default it keeps `FunctionEntry`, `Event`, and `CallParentFunction` nodes but deletes everything else — including `FunctionResult`. If FunctionResult gets deleted, output parameters disappear. The fix was adding `FunctionResult` to the keep list.

### Variable Types & SubTypes

Common type strings and what to pass:

| Type String | SubType | Example |
|---|---|---|
| `bool` | — | `{"type": "bool"}` |
| `int` | — | `{"type": "int"}` |
| `real` / `float` | — | `{"type": "real"}` |
| `Vector` / `Rotator` / `Transform` | — | `{"type": "Vector"}` |
| `object` | class name | `{"type": "object", "sub_type": "Actor"}` |
| `object` (array) | class name | `{"type": "object", "sub_type": "Actor", "is_array": true}` |
| `struct` | struct name | `{"type": "struct", "sub_type": "GameplayTagContainer"}` |

### Class Lookup: Short Names vs Full Paths

When specifying a class/sub_type, the code resolves it in order:
1. `FindObject<UClass>(ANY_PACKAGE, "Name")` — short name like `"Actor"` or `"HelicopterAbilityData"`
2. `LoadClass("/Script/Engine.Name")` — engine classes
3. `LoadClass("Full/Asset/Path.Name")` — blueprint asset paths

Always try the short name first. If it fails, use the full path like `"/Script/GameplayTags.BlueprintGameplayTagLibrary"`.

For Blueprint-defined structs (like `HelicopterAbilityData`), use the short name — it will be found via `ANY_PACKAGE`.

### Functin Names for CallFunction

Use the **C++ function name**, not the Blueprint display name:

| Blueprint Display | C++ Function | Target |
|---|---|---|
| `Get Actor Location` | `K2_GetActorLocation` | Actor |
| `Get Actor Forward Vector` | `GetActorForwardVector` | Actor |
| `Project Vector on to Plane` | `ProjectVectorOnToPlane` | KismetMathLibrary |
| `Normalize` | `Normal` | KismetMathLibrary |
| `Equal (Vector)` | `EqualEqual_VectorVector` | KismetMathLibrary |
| `vector + vector` | `Add_VectorVector` | KismetMathLibrary |
| `vector - vector` | `Subtract_VectorVector` | KismetMathLibrary |
| `vector * float` | `Multiply_VectorFloat` | KismetMathLibrary |
| `Make Vector` | `MakeVector` | KismetMathLibrary |
| `Make Transform` | `MakeTransform` | KismetMathLibrary |
| `Make Rot from X` | `MakeRotFromX` | KismetMathLibrary |
| `Break Hit Result` | `BreakHitResult` | GameplayStatics |
| `Box Trace By Channel` | `BoxTraceSingle` | KismetSystemLibrary |
| `Get All Actors Of Class` | `GetAllActorsOfClass` | GameplayStatics |
| `Has Tag` | `HasTag` | /Script/GameplayTags.BlueprintGameplayTagLibrary |
| `To Float (Integer)` | `Conv_IntToDouble` | KismetMathLibrary |
| `Break Vector` | `BreakVector` | KismetMathLibrary |

Use `list_callable_functions` to discover available functions and their parameters. If a function isn't found, try without a `target` parameter.

### Struct Member Functions

Some functions live on USTRUCTs (not UCLASSes). Examples: `HasTag` on `GameplayTagContainer`. These require special handling — the MCP now searches UScriptStruct Children for UFUNCTIONs. Use the `/Script/GameplayTags.BlueprintGameplayTagLibrary` target path for tag functions.

---

## Node Type Reference

### Supported Node Types

| Node Type | Key Fields | Notes |
|---|---|---|
| `CallFunction` | `function_name`, `target` (optional), `pin_defaults` | Most common. Use C++ function names. |
| `Event` | `event_name` | Native events from parent class. Must match C++ name exactly. |
| `CustomEvent` | `event_name`, `params` | Custom-created events. `params` array of `{name, type, sub_type}`. |
| `ModifyFunctionEntry` | `params`, `remove_pins` | Add/remove function parameters. **Use this to set Inputs/Outputs.** |
| `Branch` | — | If/else execution fork. |
| `Sequence` | — | Sequential exec branching. |
| `VariableGet` | `variable_name`, `variable_class` (optional) | Read a BP variable. Use `variable_class` for struct member access. |
| `VariableSet` | `variable_name`, `variable_class` (optional) | Write a BP variable. |
| `CastTo` | `cast_class` | Dynamic cast. |
| `PromotableOperator` | `operation`, `extra_inputs` | Math operations. `operation` set via reflection. |
| `MacroInstance` | `macro_name` | ForEachLoop, ForLoopWithBreak, IsValid. |
| `CallParentFunction` | `function_name` | Call parent implementation of overridden function. |
| `AddDelegate` | `event_name` | Bind event to delegate. |
| `CreateDelegate` | `event_name` | Create a delegate reference. |
| `SpawnActor` | `spawn_class` | Spawn an actor from class. |
| `FunctionResult` | `return_values` | Return node with output params. |
| `LatentAbilityCall` | `task_class`, `task_function` | Async ability tasks (experimental). |

### Node Type NOT Supported

- `K2Node_Knot` (reroute nodes)
- `K2Node_AddPin` for dynamic pin arrays
- Some LatentAbilityCall variants

---

## Common Patterns

### Creating a New Function

```
1. remove_function_graph (if replacing)
2. add_function_graph
3. ModifyFunctionEntry to set inputs + outputs
4. build_blueprint_graph or add_blueprint_node incrementally
5. connect_blueprint_pins for all connections
6. auto_layout_graph
7. compile_blueprint
```

### Building a Graph from Scratch

Use `build_blueprint_graph` for bulk node creation (faster), then `connect_blueprint_pins` for wiring. Or build incrementally with `add_blueprint_node` + `connect_blueprint_pins` if you need to verify each step.

### Graph Names with Spaces

Internal graph object names often have spaces (e.g., `"Calculate Turret Spawn Transform"`). When functions are listed, the display name may differ from the internal name. Use the **internal UObject name** (try both with and without spaces).

### Struct Member Access

To read a member from a struct variable:
```json
{"node_type": "VariableGet", "variable_name": "ModuleAirSupport", "variable_class": "HelicopterAbilityData"}
```
This creates a node with a `self` input pin (connect the struct variable here) and the member as output.

---

## Troubleshooting

### "Pin named X doesn't match any parameters of function Y"

The function's UFunction signature doesn't match the call site. Usually caused by:
- Function was modified after compilation → recompile the blueprint
- Output param is on FunctionEntry instead of FunctionResult → use `ModifyFunctionEntry` with `is_output: true`
- Array sub_type doesn't match (e.g., `Array<Object>` vs `Array<Actor>`) → fix the function's FunctionResult sub_type

### "Connection not allowed: Array of Object is not compatible with Array of Actor"

Array sub_type resolution failed. The function's output pin has `Object` instead of `Actor`. Re-run `ModifyFunctionEntry` with correct `sub_type` — the class lookup fix ensures short names resolve correctly.

### "Function 'X' not found"

- Check C++ function name (not display name)
- Try with and without `target` parameter
- For struct functions, try full path like `/Script/GameplayTags.BlueprintGameplayTagLibrary`
- Use `list_callable_functions` to search for available functions

### "Event function 'X' not found in class hierarchy"

The event name must match a C++ UFUNCTION in the parent class. Common event naming:
- `BP_OnAbilityDataSet` (not "Event BP on Ability Data Set")
- `BP_OnSummonDealDamage` (not "Event BP on Summon Deal Damage")
- Search the C++ source for the actual function name using `grep`

### FunctionResult Gets Deleted After build_blueprint_graph

Fixed — `BuildBlueprintGraph` now preserves `FunctionResult` nodes. If you use an older version, re-add the FunctionResult manually after building.

### PromotableOperator Has No Pins / Wrong Type

`PromotableOperator` requires `operation` to be set via FProperty reflection AND `ReconstructNode()` called. The node type handles this automatically, but if pins don't appear, the operation name might not match. Use regular `CallFunction` with `Add_VectorVector` etc. as a fallback.

### BoxTraceSingle / Trace Functions

Use target `KismetSystemLibrary`. The function `BoxTraceSingle` resolves to "Box Trace By Channel". Key pins: `Start`, `End`, `HalfSize`, `Orientation`, `TraceChannel`, `ActorsToIgnore`, `OutHit`. The `OutHit` connects to `BreakHitResult.Hit`.

---

## Quick Reference: build_blueprint_graph JSON

```json
{
  "nodes": [
    {"id": "node1", "type": "CallFunction", "function_name": "...", "pos_x": 0, "pos_y": 0},
    {"id": "node2", "type": "VariableGet", "variable_name": "...", "pos_x": 200, "pos_y": 0},
    {"id": "node3", "type": "Branch", "pos_x": 400, "pos_y": 0}
  ],
  "connections": [
    {"source_node": "node1", "source_pin": "then", "target_node": "node3", "target_pin": "execute"}
  ]
}
```

Use short `id` strings — the tool returns a `node_id_to_name` map for connecting.

---

## Appendix: Engine Source Analysis

For deeper issues, the relevant engine source files are:

- `BlueprintDetailsCustomization.cpp:4595-4657` — Inputs/Outputs categorization
- `K2Node_FunctionEntry.cpp:436-462` — CanCreateUserDefinedPin (EGPD_Output only)
- `K2Node_FunctionResult.cpp:181-191` — CanCreateUserDefinedPin (EGPD_Input only)
- `K2Node_EditablePinBase.cpp:160-176` — CreateUserDefinedPin (no CanCreate check)
- `BlueprintEditorUtils.h:1726` — FindOrCreateFunctionResultNode
- `EdGraphSchema_K2.cpp:3651` — bIsReference from CPF_OutParm|CPF_ReferenceParm
