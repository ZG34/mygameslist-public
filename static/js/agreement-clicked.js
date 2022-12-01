var elements = document.getElementsByTagName("a"); 
for(var i=0; i<elements.length; i++){
    if (elements[i].className == 'agreement') {
         elements[i].onclick = function(){ 
           document.querySelector('.box').disabled = false;
   }
 } 
}
