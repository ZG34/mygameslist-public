$('#reportMessage').keyup(function() {
    document.getElementById("charCount").textContent  = this.value.length+'/200';
});