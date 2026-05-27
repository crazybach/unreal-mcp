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

### SpawnActor Crashes Unreal

Root cause: `FGraphNodeCreator::Finalize()` calls `PostPlacedNewNode()` BEFORE `AllocateDefaultPins()`. `UK2Node_SpawnActorFromClass::PostPlacedNewNode()` calls `FindPinChecked()` which asserts because pins don't exist yet.

Fix: Call `AllocateDefaultPins()` manually before `Finalize()`:
```cpp
SpawnNode->AllocateDefaultPins();  // pins created here
SpawnNode->NodePosX = PosX;
SpawnNode->NodePosY = PosY;
Creator.Finalize();  // PostPlacedNewNode now finds pins, no crash
```

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

## EventGraph Management

### The Execution Pin Is the Program Counter

Think of the event graph like a normal program. The **execution pins** (`then`, `True`, `False`, `then_0`, `then_1`) are the program counter — they define the control flow. **Data pins** are just variable assignments. When tracing or comparing graphs, always follow the exec pins first to understand the main logic flow.

**Dump the exec tree** whenever comparing or verifying a chain:
```
0: Event ActivateAbility
  [then]
  1: Branch (IsOwnerBotControlled)
    [then] → Bot path
    2: WaitTargetData (Instant)
    [else] → Player path  
    2: WaitTargetData (Confirmed)
```

This exec tree is the single source of truth. If two graphs have the same exec tree, they have the same logic flow.

### Golden Rule: Never Trust Cached Data

After ANY mutation (add, connect, build, remove, compile), the graph changes. **Always call `get_blueprint_graph_info` fresh** to get the current state. Saved tool-result JSON files are snapshots from a past point in time — they become stale immediately after any write operation.

### The Execution Pin Is the Only Truth

The `then` pin (exec output) is the definitive evidence of whether an event is wired. **No `then` connection = empty event.** Period. Even if body nodes exist in the graph, if the event's `then` pin isn't linked to them, they're orphaned and will be pruned by the compiler.

When checking event status:
1. Look at the event node's `then` pin
2. If `linked_to` is empty → **event is empty** (no matter what other nodes exist)
3. If `linked_to` has entries → event is wired (trace the chain to count body nodes)
- `then` → an `execute` pin on a downstream node
- Any output data pins connected to their consumers

### After Every MCP Interaction, Summarize the EventGraph

After each round of changes (add nodes, connect, build), call `get_blueprint_graph_info` on the EventGraph and report a concise summary:

```
EventGraph status:
  ActivateAbility          → connected (N nodes in chain)
  OnTargetDataReceived     → connected (N nodes in chain)
  OnPickupTaken            → connected (3 nodes)
  BP_OnAbilityDataSet      → connected (4 nodes)
  BP_OnSummonDealDamage    → connected (6 nodes)
  OnSummonLifeEnded        → 0 nodes (empty — event stub only)
```

This lets the user immediately see which events are wired and which are empty stubs.

### Never Trust "Success" from connect_blueprint_pins

`connect_blueprint_pins` can return `"success": true` even when the connection silently failed (schema rejected it, node not found, etc.). **Always verify** by calling `get_blueprint_graph_info` fresh and checking the event's `then` pin `linked_to` array. If the connection succeeded, it will appear there. If not, the pin is still empty and you need to re-connect.

### Detect and Report Dead/Orphaned Nodes

After every round of EventGraph changes, scan for dead nodes. A node is **dead** if:
- It has exec pins (`execute`, `then`, etc.) but no exec input connection from any upstream node
- It has no data connections at all (no links in or out)
- It cannot trace back to an event node via the execution chain

Dead nodes are pruned by the compiler and their data outputs read as defaults. Common causes:
- `build_blueprint_graph` created nodes that were never connected to events
- A node's exec input was disconnected but the node wasn't removed
- A `ClassDynamicCast` or `CastTo` that's wired for data but has no exec flow

**Always report dead nodes to the user** and offer to remove them.

### How to Check If an Event Is Empty

1. Call `get_blueprint_graph_info` on the EventGraph
2. For each `K2Node_Event` / `K2Node_CustomEvent`, check the `then` pin:
   - If `linked_to` is empty → the event is **empty** (stub, does nothing)
   - If `linked_to` has entries → the event is **wired** (has a body)
3. Report empty events explicitly: `"OnPickupTaken: 0 nodes (empty)"`

### Never Touch Already-Wired Chains When Fixing Another

When working on one event chain (e.g., OnTargetDataReceived), **never** modify, delete, or reconnect nodes belonging to other already-wired chains. If a necessary operation would affect a wired chain, **stop and ask the user** for confirmation before proceeding. Explain what would be affected and wait for approval.

Example: If `OnPickupTaken → CallFunction_25` is wired and working, do not touch `K2Node_CallFunction_25` or any of its connections while fixing `OnTargetDataReceived`.

### Never Use build_blueprint_graph on EventGraph Incrementally

`BuildBlueprintGraph` **deletes all non-Event nodes** before recreating from JSON. It only preserves:
- `UK2Node_Event` (and `UK2Node_CustomEvent` which inherits it)
- `UK2Node_FunctionEntry` / `UK2Node_FunctionResult`
- `UK2Node_CallParentFunction`

Every call wipes all body nodes (CallFunction, VariableGet, Branch, Sequence, CastTo, etc.). For incremental work, always use `add_blueprint_node` + `connect_blueprint_pins`.

If you must use `build_blueprint_graph`, include ALL body nodes for ALL event chains in a single JSON to avoid data loss.

### Fixing Stale/Broken Event Chains

When a chain is broken:
1. `remove_blueprint_node` the broken body nodes (keep the Event itself)
2. `add_blueprint_node` fresh body nodes
3. `connect_blueprint_pins` with exact node names from the add results
4. `compile_blueprint` to verify
5. Check the output log for `[Compiler]` errors if compilation fails

---

## Appendix: Engine Source Analysis

For deeper issues, the relevant engine source files are:

- `BlueprintDetailsCustomization.cpp:4595-4657` — Inputs/Outputs categorization
- `K2Node_FunctionEntry.cpp:436-462` — CanCreateUserDefinedPin (EGPD_Output only)
- `K2Node_FunctionResult.cpp:181-191` — CanCreateUserDefinedPin (EGPD_Input only)
- `K2Node_EditablePinBase.cpp:160-176` — CreateUserDefinedPin (no CanCreate check)
- `BlueprintEditorUtils.h:1726` — FindOrCreateFunctionResultNode
- `EdGraphSchema_K2.cpp:3651` — bIsReference from CPF_OutParm|CPF_ReferenceParm
