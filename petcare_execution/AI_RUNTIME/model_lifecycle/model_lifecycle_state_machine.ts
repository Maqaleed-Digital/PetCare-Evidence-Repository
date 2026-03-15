export type ModelLifecycleState =
  | "experimental"
  | "pilot"
  | "certified"
  | "production"
  | "retired"

export interface ModelLifecycleRecord {

modelName: string
version: string
state: ModelLifecycleState
assistiveOnly: true

}

export const MODEL_LIFECYCLE_REGISTRY: ModelLifecycleRecord[] = [

{
modelName: "PetCare Clinical Copilot",
version: "v1",
state: "production",
assistiveOnly: true
}

]
