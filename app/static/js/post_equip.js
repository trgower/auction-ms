document.getElementById('upgrades').onchange = function() {
      var newMax = parseInt(document.getElementById('tuc').value) - document.getElementById('upgrades').value;
      document.getElementById('slots').max = newMax;
      if (document.getElementById('slots').value > newMax) {
        document.getElementById('slots').value = newMax;
      }
    };
    document.getElementById('reserve_check').onchange = function() {
      document.getElementById('reserve').disabled = !this.checked;
    };
    document.getElementById('reserve').disabled = !document.getElementById('reserve_check').checked;

    $('#auction_form').on('submit', function() {
      var newMax = parseInt(document.getElementById('tuc').value) - document.getElementById('upgrades').value;
      document.getElementById('slots').max = newMax;
      if (document.getElementById('slots').value > newMax) {
        document.getElementById('slots').value = newMax;
      }

      var input = $('#reserve');
      input.val(input.val().replace(/,/g, ''));
      input = $('#starting_bid');
      input.val(input.val().replace(/,/g, ''));
      input = $('#min_bid_inc');
      input.val(input.val().replace(/,/g, ''));
    });