    var tagifyFields = document.getElementsByName("loadedBody");
    var tagifyFieldsList = Array.prototype.slice.call(tagifyFields);
	if(tagifyFieldsList.length){
		tagifyFieldsList.forEach(createTagifyFields);
	}

	function createTagifyFields(field) {

		var dropdown = {
			enabled: 1,
            position: 'text',
            mapValueTo: 'text',
            highlightFirst: true
		};

		var pattern = /@/
        var tagTextProp = 'text'
        var mode = 'mix'

		var settings = {
		    mode : mode,
		    tagTextProp : tagTextProp,
		    pattern : pattern,
			dropdown : dropdown,
		};

        var tagify = new Tagify(field, settings);

        tagify.on('click', redirect)

        function redirect(e){
            window.location = "https://127.0.0.1:5000/tagclicked/redirect/" + e.detail.data.value
            // console.log(e.detail.data.value);
        }

		var sourceurl = field.dataset.sourceurl;
		if(sourceurl){
			var tagifyAjaxRequest = null;

			tagify.on('input', function(e){
			    var prefix = e.detail.prefix;

				tagify.settings.whitelist.length = 0;
			})
		}
	}