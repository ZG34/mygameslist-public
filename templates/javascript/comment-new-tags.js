    // can use game_index, search_index, or make a new index
      var whitelist_1 = [
        {% for item in search_index %}
            "{{item}}",
        {% endfor %}
      ]

    var input = document.querySelector('[name=body]'),

        tagify2 = new Tagify(input, {
            mode: 'mix',
            pattern: /@|#/,
            tagTextProp: 'text',
            enforceWhitelist: 'false',
            backspace: 'false',
            editTags: 'false',

            whitelist: whitelist_1.map(function(item){
                return typeof item == 'string' ? {value:item} : item
            }),

            dropdown : {
                enabled: 1,
                position: 'text',
                mapValueTo: 'text',
                highlightFirst: true
            },
            callbacks: {
                add: console.log,
                remove: console.log
            }
        })

    tagify2.on('input', function(e){
        var prefix = e.detail.prefix;

        if( prefix ){
            if( prefix == '@' )
                tagify2.whitelist = whitelist_1;

            if( e.detail.value.length > 1 )
                tagify2.dropdown.show(e.detail.value);
        }

        console.log( tagify2.value )
        console.log('mix-mode "input" event value: ', e.detail)

    })

    tagify2.on('add', function(e){
        console.log(e)

    })