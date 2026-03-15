export interface ModelPromotionRule {

fromState: string
toState: string
approvalAuthority: string
assistiveOnly: true

}

export const MODEL_PROMOTION_RULES: ModelPromotionRule[] = [

{
fromState: "pilot",
toState: "certified",
approvalAuthority: "PetCare AI Governance Council",
assistiveOnly: true
},

{
fromState: "certified",
toState: "production",
approvalAuthority: "PetCare AI Governance Council",
assistiveOnly: true
}

]
