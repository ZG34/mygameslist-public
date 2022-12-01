var fn = function () {
    document.cookie = "cookie_consent=true";
    document.getElementById('cookie-consent-container').hidden = true;
};
document.getElementById('cookie-consent').onclick = fn;