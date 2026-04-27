(function () {
    function removeInlineError(field) {
        var next = field.nextElementSibling;
        if (next && next.classList.contains("field-error")) {
            next.remove();
        }
        field.removeAttribute("aria-invalid");
    }

    function addInlineError(field, message) {
        removeInlineError(field);
        var error = document.createElement("p");
        error.className = "field-error";
        error.textContent = message;
        field.setAttribute("aria-invalid", "true");
        field.insertAdjacentElement("afterend", error);
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".site-alert").forEach(function (alert) {
            window.setTimeout(function () {
                alert.classList.add("is-fading");
                window.setTimeout(function () {
                    alert.remove();
                }, 500);
            }, 5000);
        });

        document.querySelectorAll("[data-validate-form]").forEach(function (form) {
            form.addEventListener("submit", function (event) {
                var isValid = true;
                form.querySelectorAll("[required]").forEach(function (field) {
                    removeInlineError(field);
                    if (!field.value.trim()) {
                        isValid = false;
                        addInlineError(field, "This field is required.");
                    } else if (field.type === "email" && !field.checkValidity()) {
                        isValid = false;
                        addInlineError(field, "Enter a valid email address.");
                    }
                });

                var password = form.querySelector("#password");
                var confirmPassword = form.querySelector("#confirm_password");
                if (password && confirmPassword && password.value !== confirmPassword.value) {
                    isValid = false;
                    addInlineError(confirmPassword, "Passwords do not match.");
                }

                if (!isValid) {
                    event.preventDefault();
                }
            });
        });
    });
})();
