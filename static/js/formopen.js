function openForm() {
  document.getElementById("myForm").style.display = "block";
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
}

document.getElementById("open").addEventListener('click', openForm);
document.getElementById("close").addEventListener('click', closeForm);
