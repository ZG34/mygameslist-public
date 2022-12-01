    $152(document).ready(function() {
        $("#gameTags").tagit();
    });

    $152("#gameTags").tagit({
        availableTags: [
        {% for game in game_index %}
            "{{game}}",
        {% endfor %}],
    readOnly: false,
    });