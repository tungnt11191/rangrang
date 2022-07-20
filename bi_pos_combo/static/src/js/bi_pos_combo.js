// pos_product_bundle_pack js
odoo.define('bi_pos_combo.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var core = require('web.core');
	var utils = require('web.utils');
	var _t = core._t;
	var round_di = utils.round_decimals;
	var round_pr = utils.round_precision;
	var printer = require('pos_restaurant.multiprint');

	var QWeb = core.qweb;
	var exports = {};


	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function (session, attributes) {
			var product_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
			product_model.fields.push('is_pack','pack_ids');
			return _super_posmodel.initialize.call(this, session, attributes);
		},
	});

	models.load_models({
		model: 'product.pack',
		fields: ['product_ids', 'is_required', 'category_id','bi_product_product','bi_product_template','name'],
		domain: null,
		loaded: function(self, pos_product_pack) {
			self.pos_product_pack = pos_product_pack;
			self.set({
				'pos_product_pack': pos_product_pack
			});
		},
	});

	var orderline_id = 1;

	var OrderlineSuper = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
		initialize: function(attr,options){
			OrderlineSuper.initialize.apply(this, arguments);
			this.pos   = options.pos;
			this.order = options.order;
			var self = this;
			if (options.json) {
				this.init_from_JSON(options.json);
				return;
			}
			this.combo_products = this.combo_products;

			var final_data = self.pos.get('final_products')
			if(final_data){
				for (var i = 0; i < final_data.length; i++) {
					if(final_data[i][0] == this.product.id){
						this.combo_products = final_data[i][1];
						self.pos.set({
							'final_products': null,
						});
					}
				}
			}
			
			this.set_combo_products(this.combo_products);
			this.combo_prod_ids =  this.combo_prod_ids || [];
			this.is_pack = this.is_pack;
		},

		clone: function(){
	        var orderline = OrderlineSuper.clone.call(this);
	        orderline.is_pack = this.is_pack;
	        orderline.price_manually_set = this.price_manually_set;
	        orderline.combo_prod_ids = this.combo_prod_ids || [];
			orderline.combo_products = this.combo_products || [];
	        return orderline;
	    },
		
		
		init_from_JSON: function(json) {
            OrderlineSuper.init_from_JSON.apply(this,arguments);
			this.combo_prod_ids = json.combo_prod_ids;
			this.is_pack = json.is_pack;
        },

		export_as_JSON: function() {
			var json = OrderlineSuper.export_as_JSON.apply(this,arguments);
			json.combo_products = this.get_combo_products();
			json.combo_prod_ids= this.combo_prod_ids;
			json.is_pack=this.is_pack;
			return json;
		},

		export_for_printing: function(){
			var json = OrderlineSuper.export_for_printing.apply(this,arguments);
			json.combo_products = this.get_combo_products();
			json.combo_prod_ids= this.combo_prod_ids;
			json.is_pack=this.is_pack;
			return json;
		},

		
		set_combo_prod_ids:function(ids){
			this.combo_prod_ids = ids
			this.trigger('change',this);
		},
		set_combo_products: function(products) {
			var ids = [];
			if(this.product.is_pack)
			{	
				if(products)
				{
					products.forEach(function (prod) {
						if(prod != null)
						{
							ids.push(prod.id)
						}
					});
				}
				this.combo_products = products;
				this.set_combo_prod_ids(ids)
				if(this.combo_prod_ids)
				{
					this.set_combo_price(this.price);
				}
				this.trigger('change',this);
			}
			
		},
		set_is_pack:function(is_pack){
			this.is_pack = is_pack
			this.trigger('change',this);
		},

		set_unit_price: function(price){
			this.order.assert_editable();
			if(this.product.is_pack)
			{
				this.set_is_pack(true);
				var prods = this.get_combo_products()
				var total = price;
			
				this.price = round_di(parseFloat(total) || 0, this.pos.dp['Product Price']);
			}
			else{
				this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
			}
			this.trigger('change',this);
		},

		set_combo_price: function(price){
			var prods = this.get_combo_products()
			var total = 0;
			prods.forEach(function (prod) {
				if(prod)
				{
					total += prod.lst_price	
				}	
			});
			if(self.pos.config.combo_pack_price== 'all_product'){
				this.set_unit_price(total);
			}
			else{
				let prod_price = this.product.lst_price;
				this.set_unit_price(prod_price);
			}
			this.trigger('change',this);
		},

		
		// Pass Bundle Pack Products in Orderline WIdget.
		get_combo_products: function() {
			self = this;
			if(this.product.is_pack)
			{
				var get_sub_prods = [];
				if(this.combo_prod_ids)
				{
					this.combo_prod_ids.forEach(function (prod) {
						var sub_product = self.pos.db.get_product_by_id(prod);
						get_sub_prods.push(sub_product)
					});
					return get_sub_prods;
				}
				if(this.combo_products)
				{
					if(! null in this.combo_products){
						return this.combo_products
					}
				}
			}
			
		},

		
	});

	var posorder_super = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attr, options) {
			this.barcode = this.barcode || "";
			posorder_super.initialize.call(this,attr,options);
		},

		build_line_resume: function(){
			var resume = posorder_super.build_line_resume.apply(this,arguments);
			var self = this;
			let cnt = 1000;
			this.orderlines.each(function(line){
				if(line.combo_prod_ids && line.combo_prod_ids.length > 0){
					var combo = line.get_combo_products();
					combo.forEach(function(prod){
						if (typeof resume[cnt] === 'undefined') {
							resume[cnt] = {
								qty: 1,
								note: '',
								product_id: prod.id,
								product_name_wrapped: [prod.display_name],
							};
						} else {
							resume[cnt].qty += 1;
						}
						cnt += 1;
					})
				}
			});
			return resume;
		},

	});
});
