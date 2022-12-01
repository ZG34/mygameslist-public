$('#body').keyup(function() {
    document.getElementById("showPostLen").innerHTML = this.value.length+'/200';
});