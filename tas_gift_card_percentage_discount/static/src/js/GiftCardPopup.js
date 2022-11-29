odoo.define('tas_gift_card_percentage_discount.pos_order_gift_card_discount', function (require) {
"use strict";

    var GiftCardPopup = require('pos_gift_card.GiftCardPopup');
    var core = require('web.core');
    var utils = require('web.utils');
    console.log('GiftCardPopup', GiftCardPopup);
    var _t = core._t;

    const Registries = require('point_of_sale.Registries');

    const CustomGiftCardPopup = GiftCardPopup => class extends GiftCardPopup {
        getPriceToRemove(giftCard) {
            console.log('getPriceToRemove');
//            return super.getPriceToRemove(giftCard);
            let currentOrder = this.env.pos.get_order();
            var discountPrice = currentOrder.get_total_with_tax() * (giftCard.percentage / 100)
            return discountPrice > giftCard.balance
                ? -giftCard.balance
                : -discountPrice;
        }
        async getGiftCard() {
          console.log('getGiftCard');
          console.log('POS', this.env.pos);
          if (this.state.giftCardBarcode == "") return;

          let giftCard = await this.rpc({
              model: "gift.card",
              method: "search_read",
              args: [[["code", "=", this.state.giftCardBarcode]]],
          });
          if (giftCard.length) {
              giftCard = giftCard[0];
          } else {
              return false;
          }
          if (!giftCard.apply_for_pos){
            return giftCard;
          } else {
            var current_pos_config = this.env.pos.config_id;

            for (let i = 0; i < giftCard.pos_config_ids; i++) {
                 if(current_pos_config == giftCard.pos_config_ids[i]){
                    console.log("equal config");
                    return giftCard;
                  }
            }

          }
          return false;
        }
    };

    Registries.Component.extend(GiftCardPopup, CustomGiftCardPopup);

    return GiftCardPopup;
});
