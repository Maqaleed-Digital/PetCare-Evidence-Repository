export interface LifecycleReviewCadence {

reviewIntervalDays: number
reviewAuthority: string
assistiveOnlyBoundaryPreserved: true

}

export const MODEL_REVIEW_CADENCE: LifecycleReviewCadence = {

reviewIntervalDays: 90,

reviewAuthority: "PetCare AI Governance Council",

assistiveOnlyBoundaryPreserved: true

}
