odoo.define("dashboard_inventory.overview_int_dashboard_tung", function(require) {
  "use strict";

  var core = require("web.core");
  var dataset = require("web.data");
  var AbstractAction = require('web.AbstractAction');
  var _t = core._t;
  var QWeb = core.qweb;

  var overview_int_dashboard = AbstractAction.extend({
    template: 'overview_xnt_dashboard_tung',
    events: {
      'click #quet_du_lieu': 'bms_quet_du_lieu',
      'click .detailmodel': 'bms_click_model_tr',
    },

    //Quet du lieu
    bms_quet_du_lieu: function(e) {
      var self = this;
      var current_val = $("#product_selectbox").val();
      if (!!current_val) {
        self.fetchlocationblocks(current_val);
      } else {
        alert('Chọn sản phẩm trước!')
      }
    },

    bms_click_model_tr: function(e) {
      var self = this;
      var data_model =  $(e.currentTarget).attr("data_model");
      var data_model_id =  $(e.currentTarget).attr("data_model_id");
      var base_url = "";
      this._rpc({
        model: 'inventory.management.dashboard',
        method: 'get_web_base_url',
        args: [],
      }).then(function(data) {
        base_url = data;
        base_url += '/'
        base_url += "web#id=" + data_model_id + "&view_type=form&model=" + data_model;
        window.open(base_url, '_blank');
        });
    },

    init: function(parent, action) {
      var self = this;
      this.product_id = action.params['product_id'];
      this.location_id = action.params['location_id'];
      this.start_date = action.params['start_date'];
      this.end_date = action.params['end_date'];
      console.log('Product ID: ', this.product_id)
      return this._super.apply(this, arguments);
    },

    // Code chay khoi dong trang
    start: function() {
      var self = this;
      var x = this.start_date;
      var y = this.end_date;
      this._rpc({
        model: 'inventory.management.dashboard',
        method: 'get_product_information',
        args: [this.product_id, this.location_id],
      }).then(function(data) {
        _.each(data['products'], function(product) {
          $('.product-container select').append('<option value="' + product.id + '">' +
            product.name + '</option>');
        });
        _.each(data['locations'], function(location) {
          $('.overview-location-container select').append('<option value="' + location.id + '">' + location.name + '</option>');
        });
        $("#pro_start_date").val(x);
        $("#pro_end_date").val(y);
      });

      this._rpc({
        model: 'inventory.management.dashboard',
        method: 'get_overview_dashboard_data_tung',
        args: [this.product_id, this.location_id, this.start_date, this.end_date],
      }).then(function(xdata) {

        function formatNumber(num) {
          return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
        };

        $('#tongnhapncc').html(formatNumber(xdata['tongnhapncc']));
        $('#nhapnoibo').html(formatNumber(xdata['nhapnoibo']));
        $('#xuatdinhluong').html(formatNumber(xdata['xuatdinhluong']));
        $('#xuattra').html(formatNumber(xdata['xuattra']));
        $('#xuathuy').html(formatNumber(xdata['xuathuy']));
        $('#xuatkhac').html(formatNumber(xdata['xuatkhac']));
        $('#tongnhap').html(formatNumber(xdata['tongnhap']));
        $('#tongxuat').html(formatNumber(xdata['tongxuat']));
        $('#sodu').html(formatNumber(xdata['sodu']));
        $('#internal_stock_move').DataTable().destroy();
        $('#internal_stock_move').DataTable({
          dom: 'Bfrtipl',
          responsive: true,
          language: {
            search: "Tìm Kiếm&nbsp;:",
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
            [10, 25, 50, -1],
            [10, 25, 50, "Tất cả"]
          ],
          "processing": true,
          "info": true,
          "stateSave": true,
          "createdRow": function(row, data, dataIndex) {
            var idclass = "detailmodel";
              $(row).addClass(idclass);
              $(row).attr('id', data.ID);
              $(row).attr('data_model', data.data_model);
              $(row).attr('data_model_id', data.data_model_id);
          },
          data: xdata['result'],
          "columns": [{
              "data": "sopn"
            },
            {
              "data": "ngaychungtu"
            },
            {
              "data": "loaiphieu"
            },
            {
              "data": "quantity",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.', 2, '')
            },
            {
              "data": "dvt",
            },
            {
              "data": "giatri",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.', 0, '')
            },
            {
              "data": "makhoxuat"
            },
            {
              "data": "makhonhap"
            },
            {
              "data": "mavt"
            }
          ],
          buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
          ]
        });
      });
    },

    // Load du lieu tu location
    fetchlocationblocks: function(product_id) {
      var self = this;
      var start_date = $("#pro_start_date").val();
      var end_date = $("#pro_end_date").val();
      this._rpc({
        model: 'inventory.management.dashboard',
        method: 'get_overview_dashboard_data',
        args: [product_id, this.location_id, start_date, end_date],
      }).then(function(xdata) {
        function formatNumber(num) {
          return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
        };

        $('#tongnhapncc').html(formatNumber(xdata['tongnhapncc']));
        $('#xuathuysanxuat').html(formatNumber(xdata['xuathuysanxuat']));
        $('#sanxuatduoc').html(formatNumber(xdata['slsanxuatra']));
        $('#boxuathuy').html(formatNumber(xdata['boxuathuy']));
        $('#xuatsanxuat').html(formatNumber(xdata['xuatsanxuat']));
        $('#trahangncc').html(formatNumber(xdata['trahangncc']));
        $('#xuathuykhac').html(formatNumber(xdata['xuathuykhac']));
        $('#thuakiemke').html(formatNumber(xdata['thuakiemke']));
        $('#thieukiemke').html(formatNumber(xdata['thieukiemke']));
        $('#xuatkhachhang').html(formatNumber(xdata['xuatkhachhang']));
        $('#xuatkhac').html(formatNumber(xdata['xuatkhac']));
        $('#nhapkhac').html(formatNumber(xdata['nhapkhac']));
        $('#xuatnoibo').html(formatNumber(xdata['xuatnoibo']));
        $('#tongnhap').html(formatNumber(xdata['tongnhap']));
        $('#tongxuat').html(formatNumber(xdata['tongxuat']));
        $('#slsanxuatnhapkho').html(formatNumber(xdata['slsanxuatnhapkho']));
        $('#nhapnvlsanxuat').html(formatNumber(xdata['nhapnvlsanxuat']));
        $('#sodu').html(formatNumber(xdata['sodu']));
        $('#internal_stock_move').DataTable().destroy();
        $('#internal_stock_move').DataTable({
          dom: 'Bfrtipl',
          responsive: true,
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
            [10, 25, 50, -1],
            [10, 25, 50, "Tất cả"]
          ],
          "processing": true,
          "info": true,
          "stateSave": true,
          "createdRow": function(row, data, dataIndex) {
            var idclass = "detailmodel";
              $(row).addClass(idclass);
              $(row).attr('id', data.ID);
              $(row).attr('data_model', data.data_model);
              $(row).attr('data_model_id', data.data_model_id);
          },
          data: xdata,
          "columns": [{
              "data": "sopn"
            },
            {
              "data": "ngaychungtu"
            },
            {
              "data": "loaiphieu"
            },
            {
              "data": "quantity",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.', 0, '')
            },
            {
              "data": "dvt",
            },
            {
              "data": "giatri",
              className: "text-right",
              render: $.fn.dataTable.render.number(',', '.', 0, '')
            },
            {
              "data": "makhoxuat"
            },
            {
              "data": "makhonhap"
            },
            {
              "data": "mavt"
            }
          ],
          buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
          ]
        });
      });
    },
  });
  core.action_registry.add("dashboard_inventory.overview_xnt_dashboard_tung", overview_int_dashboard);
});
