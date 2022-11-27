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
            var discountPrice = currentOrder.get_total_without_tax() * (giftCard.percentage / 100)
            return discountPrice > giftCard.balance
                ? -giftCard.balance
                : -discountPrice;
            }
    };

    Registries.Component.extend(GiftCardPopup, CustomGiftCardPopup);

    return GiftCardPopup;
});
