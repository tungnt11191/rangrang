odoo.define("tas_cash_control.show_dashboard", function(require) {
  "use strict";

  var core = require("web.core");
  var dataset = require("web.data");
  var AbstractAction = require('web.AbstractAction');
  var _t = core._t;
  var QWeb = core.qweb;

  var tas_cash_control_dashboard = AbstractAction.extend({
    template: 'tas_revenue_template',
    events: {
      'click #quet_du_lieu': 'bms_quet_du_lieu',
    },

    //Filter by locations
    locations_selectbox_onchange: function(e) {
      var self = this;
      var current_val = $(e.currentTarget).val();
      self.fetchlocationblocks(current_val);
    },

    //Quet du lieu
    bms_quet_du_lieu: function(e) {
      var self = this;
      self.fetchlocationblocks();

    },

    // Code chay khoi dong trang
    start: function() {
      var self = this;
      this._rpc({
        model: 'tas.revenue.report',
        method: 'get_start_datetime',
        args: [],
      }).then(function(data) {
        $("#start_date").val(data['start_date']);
        $("#end_date").val(data['end_date']);
      });
    },

    // Load du lieu tu location
    fetchlocationblocks: function() {
      var self = this;
      var start_date = $("#start_date").val();
      var end_date = $("#end_date").val();

      this._rpc({
        model: 'tas.revenue.report',
        method: 'get_revenue_data',
        args: [start_date, end_date],
      }).then(function(xdata) {
        $('#example').DataTable().destroy();
        $('#example').DataTable({
          dom: 'Bfrtipl',
          language: {
            search: "Tìm Kiếm&nbsp;:",
            lengthMenu: "Xem _MENU_ phiếu đối soát một trang",
            paginate: {
              previous: "Trang Trước",
              next: "Trang Tiếp",
            },
            decimal: ".",
            info: "Đang xem phiếu từ _START_ đến _END_ trong tổng số _TOTAL_ Phiếu"
          },
          fixedHeader: {
            header: true,
          },
          "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
          "ordering": false,
          "processing": true,
          "info": true,
          "stateSave": true,
          data: xdata,
          "columns": [{
              "data": "invoice"
            },
            {
              "data": "einvoice"
            },
            {
              "data": "sale_team"
            },
            {
              "data": "seller"
            },
            {
              "data": "sale_order"
            },
            {
              "data": "customer_id"
            },
            {
              "data": "customer_name"
            },
            {
              "data": "total_3387",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.',  0, '')
            },
            {
              "data": "3387_to_5113",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.', 0, '')
            },
            {
              "data": "5113_total",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.',  0, '')
            },
            {
              "data": "remainnng_amount",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.', 0, '')
            },
          ]
        });

      });

    },

  });
  core.action_registry.add("resful.dashboard", tas_cash_control_dashboard);
});
