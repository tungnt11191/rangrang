odoo.define('order_types_in_pos.OrderTypeListScreen', function (require) {
    'use strict';

    const { debounce } = owl.utils;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { isConnectionError } = require('point_of_sale.utils');
    const { useAsyncLockedMethod } = require('point_of_sale.custom_hooks');

    /**
     * Render this screen using `showTempScreen` to select client.
     * When the shown screen is confirmed ('Set Customer' or 'Deselect Customer'
     * button is clicked), the call to `showTempScreen` resolves to the
     * selected client. E.g.
     *
     * ```js
     * const { confirmed, payload: selectedClient } = await showTempScreen('OrderTypeListScreen');
     * if (confirmed) {
     *   // do something with the selectedClient
     * }
     * ```
     *
     * @props client - originally selected client
     */
    class OrderTypeListScreen extends PosComponent {
        constructor() {
            super(...arguments);
            console.log("this.props.client", this.props.client);
            console.log("delivery_types", this.props.delivery_types)
            this.delivery_types = this.props.delivery_types;
            this.selected_delivery_type_id = this.props.selected_delivery_type_id;
            this.state = {
                            detailIsShown: false,

            };
        }
        async click_delivery_type(delivery_type_id, event) {
            console.log("click_delivery_type", event);
            console.log("click_delivery_type_id", delivery_type_id);

            var self = this;
            var tr = $(event.target).closest('.delivery-type-line');
            var deliverTypeHtmlElements = $(this.el).find(".delivery-type-line");
            if(tr.hasClass( "highlight" )){
                self.selected_delivery_type_id = 0;
                tr.removeClass("highlight");
            } else {
                deliverTypeHtmlElements.each(function(index) {
                  $(deliverTypeHtmlElements[index]).removeClass("highlight");
                });
                self.selected_delivery_type_id = delivery_type_id;
                tr.addClass("highlight");
            }
            let order = this.env.pos.get_order();
            order.set_delivery_type(self.selected_delivery_type_id);
        }

        // Lifecycle hooks
        back() {
            if(this.state.detailIsShown) {
                this.state.detailIsShown = false;
                this.render();
            } else {
                this.props.resolve({ confirmed: false, payload: false });
                this.trigger('close-temp-screen');
            }
        }
        confirm() {
            this.props.resolve({ confirmed: true, payload: this.state.selectedClient });
            this.trigger('close-temp-screen');
        }
    }
    OrderTypeListScreen.template = 'OrderTypeListScreen';

    Registries.Component.add(OrderTypeListScreen);

    return OrderTypeListScreen;
});
