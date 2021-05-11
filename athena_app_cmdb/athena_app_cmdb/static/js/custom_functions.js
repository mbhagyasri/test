
function clickableTable( jQuery ) 
{
    $('#table-custom tr').click(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });
}

function idleLogout() {
    var t;
    window.onload = resetTimer;
    window.onmousemove = resetTimer;
    window.onmousedown = resetTimer;  // catches touchscreen presses as well
    window.ontouchstart = resetTimer; // catches touchscreen swipes as well
    window.onclick = resetTimer;      // catches touchpad clicks as well
    window.onkeypress = resetTimer;
    window.addEventListener('scroll', resetTimer, true); // improved; see comments

    function doLogout() {
        document.getElementById('logoutForm').submit()
    }

    function resetTimer() {
        clearTimeout(t);
        t = setTimeout(doLogout, 1800000);  // time is in milliseconds
    }
}
