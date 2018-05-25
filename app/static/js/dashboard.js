$('#feedbackModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var recp = button.data('recpname');
    var recpid = button.data('recpid');
    var sellerid = button.data('sellerid');
    var aucid = button.data('aucid');
    var itemid = button.data('itemid');
    var price = button.data('price');
    var item = button.data('item');
    var quality = button.data('quality');

    $(this).find('#score-0').prop("selected", true);
    $(this).find('#score-1').prop("disabled", sellerid != recpid);
    $(this).find('#score-2').prop("disabled", sellerid != recpid);

    $(this).find('.modal-title').text('Leave feedback for ' + recp);
    $(this).find('.itemname').text(item);
    $(this).find('.price').text(price);
    $(this).find('#auc_id').val(aucid);
    $(this).find('#quality').val(quality);
    $(this).find('#recp_id').val(recpid);
    $(this).find('.feedback-img').attr('src', '/static/images/' + itemid + '.png');
    $(this).find('.itemname').attr('class', 'itemname text-i' + quality);
  });

  $('#messageModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var recp = button.data('recpname');
    var recpid = button.data('recpid');

    $(this).find('.modal-title').text('Send message to ' + recp);
    $(this).find('#recp_id').val(recpid);
  });

  $('#endEarlyModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var aucid = button.data('aucid');
    $(this).find('#auc_id_early').val(aucid);
  });

  $('#endAuctionYes').on('click', function (event) {
    location.href = '/early/' + $('#endEarlyModal').find('#auc_id_early').val();
  });

  $('#cancelAuctionModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var aucid = button.data('aucid');
    $(this).find('#auc_id_cancel').val(aucid);
  });

  $('#cancelAuctionYes').on('click', function (event) {
    location.href = '/cancel/' + $('#cancelAuctionModal').find('#auc_id_cancel').val();
  });