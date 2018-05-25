$('#item_name').autocomplete({
  serviceUrl: '/autocomplete',
  minChars: 2,
  dataType: 'json',
  deferRequestBy: 100,
  onSelect: function (suggestion) {
    document.getElementById("next_btn").disabled = false;
    document.getElementById("item_id").value = suggestion.id;
    document.getElementById("item_card").hidden = false;
    document.getElementById("item_card_image").src = "static/images/" + suggestion.id + ".png";
    document.getElementById("item_card_title").innerHTML = suggestion.value;
    document.getElementById("item_card_desc").innerHTML = suggestion.desc;
  },
  onInvalidateSelection: function () {
     document.getElementById("next_btn").disabled = true;
     document.getElementById("next_btn").disabled = true;
     document.getElementById("item_card").hidden = true;
  }
});

