  $( function() {
    var indexResults = [
        {% for item in search_index %}
            "{{item}}",
        {% endfor %}
    ];
    $( "#items" ).autocomplete({
      source: indexResults
    });
  } );