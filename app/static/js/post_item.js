document.getElementById('reserve_check').onchange = function() {
      document.getElementById('reserve').disabled = !this.checked;
    };
    document.getElementById('reserve').disabled = !document.getElementById('reserve_check').checked;

    $('#auction_form').on('submit', function() {
      var input = $('#reserve');
      input.val(input.val().replace(/,/g, ''));
      input = $('#starting_bid');
      input.val(input.val().replace(/,/g, ''));
      input = $('#min_bid_inc');
      input.val(input.val().replace(/,/g, ''));
    });