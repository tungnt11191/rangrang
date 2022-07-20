// ProductCategoriesWidget
odoo.define('bi_pos_combo.ProductCategoriesWidget', function(require) {
	"use strict";

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { useListener } = require('web.custom_hooks');
	const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
	const { useState } = owl.hooks;

	const ProductsWidget = require('point_of_sale.ProductsWidget');

	const ProductCategoriesWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			constructor() {
				super(...arguments);
			}

			_updateSearch(event) {
            	this.state.searchWord = event.detail;
        	}
		};

	Registries.Component.extend(ProductsWidget, ProductCategoriesWidget);

	return ProductsWidget;

});
