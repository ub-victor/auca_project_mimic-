(function () {
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".dash-button[href='#']").forEach(function (link) {
            link.addEventListener("click", function (event) {
                event.preventDefault();
            });
        });
    });
})();
