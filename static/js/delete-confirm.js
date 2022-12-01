function ActiveSpoiler(){
    var x = document.getElementById("spoiler");
        if (x.style.display === "none") {
            x.style.display = "block";
        } else {
            x.style.display = "none";
        }
    }

function ConfirmDelete(event) {
    var result = confirm("Are you sure ? This can NOT be reversed! \n CANCEL will prevent deletion.");
        if (!result) {
        event.preventDefault();
    }
}

document.getElementById("delete").addEventListener('click', ConfirmDelete);

document.getElementById("spoil-button").addEventListener('click', ActiveSpoiler);

document.getElementById("spoiler").style.display = "none";
