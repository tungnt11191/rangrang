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
          console.log('override getGiftCard');
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
            this.env.pos.get_order().globle_giftcard = giftCard;
            return giftCard;
          } else {
            var current_pos_config = this.env.pos.config_id;
            console.log("giftCard.pos_config_ids", giftCard.pos_config_ids);
            for (let i in giftCard.pos_config_ids) {
                 if(current_pos_config == giftCard.pos_config_ids[i]){
                    console.log("equal config");
                    this.env.pos.get_order().globle_giftcard = giftCard;
                    return giftCard;
                  }
            }

          }
          return false;
        }

        async addGiftCardProduct(giftCard) {
          console.log("override addGiftCardProduct");


          let can_be_sold = true;
          if (giftCard) {
            can_be_sold = !(giftCard.buy_pos_order_line_id || giftCard.buy_line_id);
          }
            let gift =
                this.env.pos.db.product_by_id[giftCard.gift_card_product_id[0]];
          if (can_be_sold) {
            this.env.pos.get_order().add_product(gift, {
              price: this.state.amountToSet,
              quantity: 1,
              merge: false,
              generated_gift_card_ids: giftCard ? giftCard.id : false,
              extras: { price_manually_set: true },
            });
            console.log('get_order().add_product success');
            console.log(this.env.pos.get_order());
          } else {
            await this.showPopup('ErrorPopup', {
              'title': this.env._t('This gift card has already been sold'),
              'body': this.env._t('You cannot sell a gift card that has already been sold'),
            });
          }
        }


        async payWithGiftCard() {
            console.log('override payWithGiftCard');
          let giftCard = await this.getGiftCard();
          if (!giftCard) return;
          console.log('payWithGiftCard giftCard', giftCard);
          console.log('payWithGiftCard gift_card_product_id', giftCard.gift_card_product_id[0]);

          let gift = this.env.pos.db.product_by_id[giftCard.gift_card_product_id[0]];
            console.log('gift product', gift);
          let currentOrder = this.env.pos.get_order();

          currentOrder.add_product(gift, {
            price: this.getPriceToRemove(giftCard),
            quantity: 1,
            merge: false,
            gift_card_id: giftCard.id,
          });

          this.cancel();
        }


        async isGiftCardAlreadyUsed() {
          console.log('override isGiftCardAlreadyUsed');
          let order = this.env.pos.get_order();
          let giftProduct = order.globle_giftcard;

          for (let line of order.orderlines.models) {
            if (line.product.id === giftProduct.id && line.price < 0) {
              if (line.gift_card_id === await this.getGiftCard().id) return line;
            }
          }
          return false;
        }
    };

    Registries.Component.extend(GiftCardPopup, CustomGiftCardPopup);

    return GiftCardPopup;
});
