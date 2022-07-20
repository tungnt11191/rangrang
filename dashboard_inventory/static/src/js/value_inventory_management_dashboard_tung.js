odoo.define("dashboard_inventory.value_xnt_management_dashboard_tung", function(require) {
  "use strict";

  var core = require("web.core");
  var dataset = require("web.data");
  var AbstractAction = require('web.AbstractAction');
  var _t = core._t;
  var QWeb = core.qweb;

  var value_xnt_dashboard = AbstractAction.extend({
//    hasControlPanel: true,
    template: 'value_xnt_dashboard_tung',
    events: {
      'change #locations_selectbox': 'locations_selectbox_onchange',
      'click #quet_du_lieu': 'bms_quet_du_lieu',
      'click .productid': 'bms_click_tr',
    },

    //Filter by locations
    locations_selectbox_onchange: function(e) {
      var self = this;
      var current_val = $(e.currentTarget).val();
      self.fetchlocationblocks(current_val);
      console.log("Toi da chay toi day");
    },

    //Quet du lieu
    bms_quet_du_lieu: function(e) {
      var self = this;
      var current_val = $("#locations_selectbox").val();
      self.fetchlocationblocks(current_val);
    },

    bms_click_tr: function(e) {
      var self = this;
      var current_val = $(e.currentTarget).text();
      var location_val = $("#locations_selectbox").val();
      var current_id =  $(e.currentTarget).attr("id");
      console.log("aaaaaaaaaaaaaaaaa");
      console.log(current_id);
      console.log(location_val);
      console.log($("#start_date").val());
      console.log($("#end_date").val());
      console.log("aaaaaaaaaaaaaaaaa");
      this.do_action({
        name: "Chi tiết xuất nhập tồn sản phẩm",
        params: {
          'product_id': current_id,
          'location_id': location_val,
          'start_date': $("#start_date").val(),
          'end_date': $("#end_date").val(),
        },
        target: 'new',
        type: 'ir.actions.client',
        tag: 'dashboard_inventory.overview_xnt_dashboard_tung'
      });
    },

    // Code chay khoi dong trang
    start: function() {
      var self = this;
      this._rpc({
        model: 'inventory.management.dashboard',
        method: 'get_xnt_all_locations',
        args: [],
      }).then(function(data) {
        _.each(data['locations'], function(location) {
          $('.locations-container select').append('<option value="' + location.id + '">' + location.display_name + '</option>');
        });
        $("#start_date").val(data['start_date']);
        $("#end_date").val(data['end_date']);
      });
    },

    // Load du lieu tu location
    fetchlocationblocks: function(location_id) {
      var self = this;
      var start_date = $("#start_date").val();
      var end_date = $("#end_date").val();

      var check_include_sub_location = $("#include_sub_location").is(":checked");
      if (check_include_sub_location == true) {
        console.log('gọi đến subdata');
        console.log(location_id);
        this._rpc({
          model: 'inventory.management.dashboard',
          method: 'get_value_include_sub_dashboard_data_tung',
          args: [location_id, start_date, end_date, 1],
        }).then(function(xdata) {
          console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
          console.log(xdata);
          console.log(xdata['result']);
          console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
          $('#xntkemgiatri').DataTable().destroy();
          var xnt_table = $('#xntkemgiatri').DataTable({
            dom: 'Bfrtipl',
            // responsive: true,
            language: {
              search: "Tìm Sản Phẩm&nbsp;:",
              lengthMenu: "Xem _MENU_ sản phẩm một trang",
              paginate: {
                previous: "Trang Trước",
                next: "Trang Tiếp",
              },
              info: "Đang xem SP từ _START_ đến _END_ trong tổng số _TOTAL_ SP"
            },
            fixedHeader: {
              header: true,
            },
            "lengthMenu": [
              [15, 30, 50, -1],
              [15, 30, 50, "Tất cả"]
            ],
            "pageLength": 25,
            "processing": true,
            "info": true,
            "stateSave": true,
            "createdRow": function(row, data, dataIndex) {
              var idclass = "productid";
                $(row).addClass(idclass);
                $(row).attr('id', data.ID);
            },
            data: xdata,
            "columns": [{
                "data": "Mã VT",
              },
              {
                "data": "Tên vật tư"
              },
              {
                "data": "ĐVT"
              },
              {
                "data": "SL Tồn Đầu",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "GT Tồn Đầu",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "tongnhapncc",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "gttongnhapncc",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "nhapnoibo",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "gtnhapnoibo",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "xuatdinhluong",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "gtxuatdinhluong",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "xuattra",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "gtxuattra",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "xuathuy",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "gtxuathuy",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "xuatkhac",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "gtxuatkhac",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "SL Nhập",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "GT Nhập",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "SL Xuất",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "GT Xuất",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
              {
                "data": "SL Tồn Cuối",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 2, '')
              },
              {
                "data": "GT Tồn Cuối",
                className: "text-right",
                render: $.fn.dataTable.render.number(',', '.', 0, '')
              },
            ],
            buttons: [
              'copy', 'csv', 'excel', 'pdf', 'print'
            ],
            drawCallback: function () {
              var api = this.api();
//              $( api.table().footer() ).html(
//                api.column(7).data().sum()
//              );

              api.table().columns().every(function() {
                console.log(this.footer())
                var column_index = this[0][0];
                if(column_index > 2){
                    $(this.footer()).html(
                        api.column(column_index).data().sum()
                    );
                }

              })
            }
          });
//          xnt_table.column( 7 ).data().sum();
        });
      } else {
        this._rpc({
          model: 'inventory.management.dashboard',
          method: 'get_value_dashboard_data',
          args: [location_id, start_date, end_date],
        }).then(function(xdata) {
          $('#xntkemgiatri').DataTable().destroy();
          $('#xntkemgiatri').DataTable({
            dom: 'Bfrtip',
            language: {
              search: "Tìm Sản Phẩm&nbsp;:",
              lengthMenu: "Xem _MENU_ sản phẩm một trang",
              paginate: {
                previous: "Trang Trước",
                next: "Trang Tiếp",
              },
              info: "Đang xem SP từ _START_ đến _END_ trong tổng số _TOTAL_ SP"
            },
            "processing": true,
            "info": true,
            "stateSave": true,
            data: xdata,
            "columns": [{
                "data": "Mã VT"
              },
              {
                "data": "Tên vật tư"
              },
              {
                "data": "ĐVT"
              },
              {
                "data": "SL Tồn Đầu",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
              {
                "data": "SL Nhập",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
              {
                "data": "SL Xuất",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
              {
                "data": "SL Tồn Cuối",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
              {
                "data": "GT Tồn Đầu",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
              {
                "data": "GT Nhập",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
              {
                "data": "GT Xuất",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
              {
                "data": "GT Tồn Cuối",
                render: $.fn.dataTable.render.number('.', ',', 0, '')
              },
            ],
            buttons: [
              'copy', 'csv', 'excel', 'pdf', 'print'
            ]
          });
        });
      };

    },

  });
  core.action_registry.add("dashboard_inventory.value_dashboard_tung", value_xnt_dashboard);
});
