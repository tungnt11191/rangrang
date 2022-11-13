odoo.define("order_types_in_pos.OrderTypeButton", function (require) {
  "use strict";

  const PosComponent = require("point_of_sale.PosComponent");
  const ProductScreen = require("point_of_sale.ProductScreen");
  const { useListener } = require("web.custom_hooks");
  const Registries = require("point_of_sale.Registries");
  const { Gui } = require("point_of_sale.Gui");

  class OrderTypeButton extends PosComponent {
    constructor() {
      super(...arguments);
      useListener("click", this.onClick);
    }
    async onClick() {
        let order = this.env.pos.get_order();
        let selected_delivery_type_id = order.get_delivery_type();
        console.log('selected_delivery_type_id', selected_delivery_type_id);
        let delivery_types = this.env.pos.get_available_delivery_types();
        const {
            confirmed,
            payload: newClient,
        } = await this.showTempScreen('OrderTypeListScreen', {
                                                                'delivery_types': delivery_types,
                                                                'selected_delivery_type_id': selected_delivery_type_id
                                                            });
        console.log(confirmed);
        console.log(newClient);

        if (confirmed) {
            var el_order_type = $(this.el).find("#order_type_id")
            el_order_type.text(this.env.pos.get_delivery_type_name(newClient))
        }
        return;
    }
  }
  OrderTypeButton.template = "OrderTypeButton";

  ProductScreen.addControlButton({
    component: OrderTypeButton,
    condition: function () {
      return this.env.pos.config.use_gift_card;
    },
  });

  Registries.Component.add(OrderTypeButton);

  return OrderTypeButton;
});
