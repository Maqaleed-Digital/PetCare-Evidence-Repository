from typing import Dict, List, Optional

from .pricing import PricingRule


class PricingRepository:
    def __init__(self) -> None:
        self._rules: Dict[str, PricingRule] = {}

    def save_rule(self, rule: PricingRule) -> PricingRule:
        rule.validate()
        self._rules[rule.rule_id] = rule
        return rule

    def get_rule(self, rule_id: str) -> Optional[PricingRule]:
        return self._rules.get(rule_id)

    def list_rules_for_partner(self, partner_id: str) -> List[PricingRule]:
        return sorted(
            [rule for rule in self._rules.values() if rule.partner_id == partner_id],
            key=lambda item: (item.catalog_item_id, item.rule_id),
        )

    def find_active_rule(self, partner_id: str, catalog_item_id: str) -> Optional[PricingRule]:
        matches = [
            rule
            for rule in self._rules.values()
            if rule.partner_id == partner_id
            and rule.catalog_item_id == catalog_item_id
            and rule.active
        ]
        matches.sort(key=lambda item: item.rule_id)
        return matches[0] if matches else None
