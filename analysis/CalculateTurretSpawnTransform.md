# CalculateTurretSpawnTransform — Analysis (GA_Helicopter)

## Signature
- **Inputs:** none
- **Output param:** `CameraDirection` (Vector) — pass-through camera aim direction
- **Return value:** `SpawnTransform` (Transform) — final spawn location/rotation

## Logic

### Phase 1: Get Tank
```
Tank = GetOwningActorFromActorInfo()
```

### Phase 2: Compute Spawn Direction
```
NormalizedDirection = Normalize(ProjectVectorOnToPlane(CameraDirection, (0,0,1)))
if NormalizedDirection ≈ (0,0,0):
    NormalizedDirection = Tank.GetActorForwardVector()
```

### Phase 3: Compute Trace Positions  
```
MidPoint = Tank.Location + NormalizedDirection * DeploymentRange
TraceStart = MidPoint + (0, 0, Z_Trace_Offset)
TraceEnd = MidPoint - (0, 0, Z_Trace_Offset)
```

### Phase 4: Trace and Build Result
```
IgnoredActors = GetTraceIgnoredActors()
Hit = BoxTraceSingleWithTag(Tag=HelicopterSpawnTrace, Start, End, HalfSize=BoxTraceSize, IgnoreActors)
SpawnLocation = Hit.Location + (0, 0, Z_Spawn_Offset)
SpawnRotation = RotationFromXVector(NormalizedDirection)
SpawnTransform = MakeTransform(SpawnLocation, SpawnRotation)
return SpawnTransform
```

## Variables Required
| Variable | Type |
|---|---|
| Tank | Actor |
| NormalizedDirection | Vector |
| MidPoint | Vector |
| TraceStart | Vector |
| TraceEnd | Vector |
| DeploymentRange | float |
| Z_Trace_Offset | float |
| Z_Spawn_Offset | float |
| BoxTraceSize | Vector |

## Key Functions
| BP Name | C++ Name | Target |
|---|---|---|
| Get Owning Actor | GetOwningActorFromActorInfo | GameplayAbility |
| Project Vector on to Plane | ProjectVectorOnToPlane | KismetMathLibrary |
| Normalize | Normal | KismetMathLibrary |
| Equal (Vector) | EqualEqual_VectorVector | KismetMathLibrary |
| Get Actor Forward Vector | GetActorForwardVector | Actor |
| Get Actor Location | K2_GetActorLocation | Actor |
| vector * float | Multiply_VectorFloat | KismetMathLibrary |
| vector + vector | Add_VectorVector | KismetMathLibrary |
| vector - vector | Subtract_VectorVector | KismetMathLibrary |
| Rotation From X Vector | MakeRotFromX | KismetMathLibrary |
| Make Transform | MakeTransform | KismetMathLibrary |
| Break Hit Result | BreakHitResult | GameplayStatics |
| BoxTraceSingleWithTag | BoxTraceSingle | KismetSystemLibrary |
| Get Trace Ignored Actors | GetTraceIgnoredActors | (self) |
