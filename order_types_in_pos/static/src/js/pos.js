odoo.define('order_types_in_pos.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var utils = require('web.utils');

var round_pr = utils.round_precision;

var _t = core._t;

models.load_fields('delivery.type','delivery_type');
models.load_models([
    {
        model: 'delivery.type',
        fields: ['name', 'id'],
        domain: null,
        loaded: function(self, delivery_types){
            console.log('delivery_types', delivery_types);
            self.delivery_types = delivery_types;
        },
    }
],{'after': 'product.product'});

var _super_pos = models.PosModel;
models.PosModel = models.PosModel.extend({
    get_available_delivery_types: function(){
        var self = this;
        var rewards = [];
        console.log('this.pos', self);
        for (var i = 0; i < self.delivery_types.length; i++) {
            var reward = self.delivery_types[i];
            rewards.push(reward);
        }
        return rewards;
    },
});

var _super = models.Order;
models.Order = models.Order.extend({
    get_delivery_type: function(){
        console.log('get_delivery_type', this);
        if (!this.pos.delivery_types || !this.delivery_type) {
            return 0;
        }
        return this.delivery_type;
    },

    set_delivery_type: function(delivery_type_id){
        if(delivery_type_id > 0){
            this.delivery_type = delivery_type_id;
        } else {
            this.delivery_type = false;
        }
    },
    export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        json.delivery_type = this.get_delivery_type();
        console.log('export_as_JSON', json);
        return json;
    },

    init_from_JSON: function(json){
        _super.prototype.init_from_JSON.apply(this,arguments);
        this.delivery_type = json.delivery_type;
    },
});
});
