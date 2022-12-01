
    $(document).ready(function() {
        $("#gameTags").tagit();
    });

    $("#gameTags").tagit({
        availableTags: [
        {% for game in game_index %}
            "{{game | safe}}",
        {% endfor %}],
    readOnly: false,
    });
