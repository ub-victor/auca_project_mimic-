document.addEventListener('DOMContentLoaded', () => {
    applyFormValidation();
    bindAjaxForms();
});

function applyFormValidation() {
    const forms = document.querySelectorAll('.auth-form');
    if (!forms.length) return;

    forms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                form.classList.add('was-validated');
                return;
            }

            const password1 = form.querySelector('input[name=password1]');
            const password2 = form.querySelector('input[name=password2]');
            if (password1 && password2 && password1.value !== password2.value) {
                event.preventDefault();
                const message = form.querySelector('.validation-feedback');
                if (message) {
                    message.textContent = 'Passwords do not match.';
                    message.classList.add('alert-error');
                }
                password2.focus();
                return;
            }

            const submitButton = form.querySelector('button[type=submit]');
            if (submitButton) {
                setLoadingState(submitButton, true);
            }
        });
    });
}

function bindAjaxForms() {
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    if (!ajaxForms.length) return;

    ajaxForms.forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!form.checkValidity()) {
                form.classList.add('was-validated');
                return;
            }

            const feedback = form.querySelector('.auth-feedback');
            if (feedback) {
                feedback.innerHTML = '';
            }

            const submitButton = form.querySelector('button[type=submit]');
            setLoadingState(submitButton, true);

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                const text = await response.text();
                const parser = new DOMParser();
                const htmlDoc = parser.parseFromString(text, 'text/html');
                const messageNode = htmlDoc.querySelector('.alert-success, .alert-error');

                if (messageNode && feedback) {
                    feedback.innerHTML = messageNode.outerHTML;
                } else if (feedback) {
                    feedback.innerHTML = '<div class="alert alert-success">If this email exists in the system, reset instructions were sent.</div>';
                }

                if (response.ok && form.dataset.resetOnSuccess === 'true') {
                    form.reset();
                }
            } catch (error) {
                if (feedback) {
                    feedback.innerHTML = '<div class="alert alert-error">Unable to submit request. Please check your connection and try again.</div>';
                }
            } finally {
                setLoadingState(submitButton, false);
            }
        });
    });
}

function setLoadingState(button, loading) {
    if (!button) return;
    button.disabled = loading;
    if (loading) {
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
    } else {
        button.textContent = button.dataset.originalText || 'Submit';
    }
}
