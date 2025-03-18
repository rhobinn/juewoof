function collectFormData(form) {
    const formData = new FormData(form);
    const formDataObject = {};

    formData.forEach((value, key) => {
        if (value === "on" || value === "") {
            formDataObject[key] = form.elements[key].type === "checkbox" ? form.elements[key].checked : value;
        } else {
            formDataObject[key] = value;
        }
    });

    // Replace empty string fields with null
    Object.keys(formDataObject).forEach(key => {
        if (formDataObject[key] === "") formDataObject[key] = null;
    });

    return formDataObject;
}

function generateIdempotencyKey(actionType) {
    if (!actionType) {
        console.warn("Idempotency requires an actionType.");
        return null;
    }
    
    let idempotencyKey = sessionStorage.getItem(`${actionType}IdempotencyKey`);
    if (!idempotencyKey) {
        idempotencyKey = crypto.randomUUID();
        sessionStorage.setItem(`${actionType}IdempotencyKey`, idempotencyKey);
    }
    return idempotencyKey;
}

async function submitForm({ formData, submitUrl, useIdempotency, actionType, formMethod }) {
    const headers = { 'Content-Type': 'application/json' };

    if (useIdempotency) {
        const idempotencyKey = generateIdempotencyKey(actionType);
        if (idempotencyKey) {
            headers['Idempotency-Key'] = idempotencyKey;
        }
    }

    return fetch(submitUrl, {
        method: formMethod,
        headers,
        body: JSON.stringify(formData),
        redirect: 'follow',
    });
}

async function handleResponse({ response, shouldRedirect, useIdempotency, actionType }) {
    if (shouldRedirect && response.redirected) {
        if (useIdempotency && actionType) {
            sessionStorage.removeItem(`${actionType}IdempotencyKey`);
        }
        window.location.href = response.url;
        return;
    }

    if (response.ok) {
        if (useIdempotency && actionType) {
            sessionStorage.removeItem(`${actionType}IdempotencyKey`);
        }
    } else {
        const errorData = await response.json();
        console.log("error_data:", errorData);
        displayErrors(errorData.detail);
        throw new Error('Error validating form');
    }
}

function setupFormSubmission({ form, submitUrl, shouldRedirect = true, useIdempotency = false, actionType = null, formMethod='POST' }) {
    if (useIdempotency && !actionType) {
        console.warn("Idempotency is enabled but no actionType was provided.");
    }

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = collectFormData(form);

        try {
            const response = await submitForm({ formData, submitUrl, useIdempotency, actionType, formMethod });
            await handleResponse({ response, shouldRedirect, useIdempotency, actionType});
        } catch (error) {
            console.error('Error submitting form:', error);
        }
    });
}


function activateOrDeactivateEntity(activateUrl, event) {
    event.preventDefault();  // Prevent form submission
    // console.log("url: ", activateUrl);

    fetch(activateUrl, {
        method: 'PATCH',
    })
    .then(response => {
        if (response.ok) {
            // console.log("Valid response");
            if (response.redirected) {
                // console.log('Redirecting to: ', response.url);
                window.location.href = response.url;
            }
        }
    })
    .catch(error => {
        console.error("Error during the activation:", error);
    });
}


function displayErrors(errors) {
    // Clear existing error messages and remove has-icons-right for all fields

    const helpElements = document.querySelectorAll('.help.is-danger');
    helpElements.forEach(element => {
        element.textContent = '';  // Clear existing error messages
    });

    const controlElements = document.querySelectorAll('[id^="control-"]'); 
    controlElements.forEach(element => {
        element.classList.remove('has-icons-right');  // Remove has-icons-right for all fields

    });
    const iconElements = document.querySelectorAll('[id^="error-icon-"]'); 
    iconElements.forEach(element => {
        element.classList.add('is-hidden');  // Remove has-icons-right for all fields

    });

    // Iterate over the error dictionary errors and display them next to the corresponding select field
    errors.forEach(error => {
        const field = error.loc[1];  // Obtains Field name (e.g., "genero")
        const errorMsg = error.msg;  // Error message (e.g., "Field required")

        // Find the select field by its id
        const helpElement =document.getElementById(`error-${field}`); 
        if (helpElement) {
            helpElement.textContent = errorMsg;  // Set the error message
        }
        // Find the control field by its id
        const controlElement =document.getElementById(`control-${field}`); 
        if (controlElement) {
            controlElement.classList.add('has-icons-right');  // Add the has-icons-right class for error fields
        }
        // Find the icon elements by its id
        const iconElement =document.getElementById(`error-icon-${field}`); 
        if (iconElement) {
            iconElement.classList.remove('is-hidden');  // Add the has-icons-right class for error fields
        }
    });
}


function clearFormOnNavigation() {
    // Clear the form data when the user navigates away or refreshes the page
    window.addEventListener("beforeunload", function() {
        const form = document.querySelector("form");
        if (form) {
            form.reset(); // Clears form fields
        }
    });

    // Also clear form when navigating back in browser
    if (window.performance) {
        if (performance.navigation.type === 2) {  // Type 2 = Back/Forward navigation
            const form = document.querySelector("form");
            if (form) {
                form.reset();  // Clears form fields
            }
        }
    }
}


function highlightModifiedFields(formId, highlightClass = 'is-info') {
    const form = document.getElementById(formId);
    if (!form) {
        console.warn(`Form with ID "${formId}" not found.`);
        return;
    }

    const inputsAndSelects = form.querySelectorAll('input, select');

    inputsAndSelects.forEach(element => {
        if (element.tagName.toLowerCase() === 'input') {
            element.addEventListener('input', function() {
                element.classList.add(highlightClass);
            });
        } else if (element.tagName.toLowerCase() === 'select') {
            element.addEventListener('change', function() {
                const parentDiv = element.closest('.field')?.querySelector('.select');
                if (parentDiv) {
                    parentDiv.classList.add(highlightClass);
                } else {
                    element.classList.add(highlightClass); // Fallback if no `.select` wrapper
                }
            });
        }
    });
}
