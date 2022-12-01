var splides = document.querySelectorAll('.splide');
if(splides.length){
    for(var i=0; i<splides.length; i++){
        var splideElement = splides[i];
        var splideDefaultOptions =
        {
            type   : 'loop',
            perPage: 3,
            perMove: 1,
        }
        var splide = new Splide( splideElement, splideDefaultOptions );
        splide.mount();
    }
}