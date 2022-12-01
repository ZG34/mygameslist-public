            function liveRefresh(){
                document.getElementById("mylistform").submit();
                };

            document.getElementById("game_sorter-selector").onchange = liveRefresh
            document.getElementById("game_sorter-order_by").onchange = liveRefresh
            document.getElementById("game_filter-starts_with").onchange = liveRefresh
            document.getElementById("game_filter-category_filter").onchange = liveRefresh
            document.getElementById("game_filter-status").onchange = liveRefresh