odoo.define('order_types_in_pos.tas_gift_card_percentage_discount', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var utils = require('web.utils');

var round_pr = utils.round_precision;

var _t = core._t;
//
//var _super_pos = models.PosModel;
//models.PosModel = models.PosModel.extend({
//    get_available_delivery_types: function(){
//        var self = this;
//        var rewards = [];
//        console.log('this.pos', self);
//        console.log('this.pos.delivery_methods', self.delivery_methods)
//        for (var i = 0; i < self.delivery_types.length; i++) {
//            var reward = self.delivery_types[i];
//            rewards.push(reward);
//        }
//        console.log('this.pos.delivery_methods 2', rewards)
//        return rewards;
//    },
//    get_delivery_type_name: function(delivery_type_id){
//        var self = this;
//        for (var i = 0; i < self.delivery_types.length; i++) {
//            if(self.delivery_types[i]['id'] == delivery_type_id){
//                return self.delivery_types[i]['name'];
//            }
//        }
//        return 'Order Type';
//    },
//});

var _super = models.Order;
models.Order = models.Order.extend({
    //@override
//    wait_for_push_order: function () {
//        if(this.pos.config.use_gift_card) {
//            let giftProduct = this.pos.db.product_by_id[this.pos.config.gift_card_product_id[0]];
//            for (let line of this.orderlines.models) {
//                if(line.product.id === giftProduct.id)
//                    return true;
//            }
//        }
//        return _order_super.wait_for_push_order.apply(this, arguments);
//    },
//    //@override
//    _reduce_total_discount_callback: function(sum, orderLine) {
//        console.log('_reduce_total_discount_callback', orderLine.product)
//        if (this.pos.config.gift_card_product_id[0] === orderLine.product.id) {
//            return sum;
//        }
//        return _order_super._reduce_total_discount_callback.apply(this, arguments);
//    },

    initialize: function(attributes,options){
        _super.prototype.initialize.call(this,attributes,options);
        if(this.env.pos.config.use_gift_card) {
            this.globle_giftcard = false;
        }
    },

    //@override
    wait_for_push_order: function () {
        if(this.pos.config.use_gift_card) {
            let giftProduct = this.globle_giftcard;
            for (let line of this.orderlines.models) {
                if(line.product.id === giftProduct.id)
                    return true;
            }
        }
        return _order_super.wait_for_push_order.apply(this, arguments);
    },
    //@override
    _reduce_total_discount_callback: function(sum, orderLine) {
        if (this.globle_giftcard === orderLine.product.id) {
            return sum;
        }
        return _order_super._reduce_total_discount_callback.apply(this, arguments);
    },
});
});
