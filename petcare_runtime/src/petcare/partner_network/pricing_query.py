from typing import List

from .pricing import PricingOutput


class PricingQuery:
    def sort_offers_low_to_high(self, offers: List[PricingOutput]) -> List[PricingOutput]:
        return sorted(
            offers,
            key=lambda item: (
                item.final_price,
                item.partner_id,
                item.catalog_item_id,
            ),
        )

    def select_best_offer(self, offers: List[PricingOutput]) -> PricingOutput:
        sorted_offers = self.sort_offers_low_to_high(offers)
        if not sorted_offers:
            raise ValueError("offers cannot be empty")
        return sorted_offers[0]
