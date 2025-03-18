// async function handleFormSubmit(formId, submitUrl) {
//     const form = document.getElementById(formId);
//     form.addEventListener('submit', async function (event) {
//         event.preventDefault();  // Prevent the form from submitting the traditional way

//         const formData = new FormData(form);
//         const formDataObject = {};

//         formData.forEach((value, key) => {
//             if (value === "on" || value === "") {
//                 formDataObject[key] = form.elements[key].type === "checkbox" ? form.elements[key].checked : value;
//             } else {
//                 formDataObject[key] = value;
//             }
//         });

//         // Replace empty string fields with null (for optional fields)
//         for (const key in formDataObject) {
//             if (formDataObject[key] === "") {
//                 formDataObject[key] = null;  // Set empty fields to null
//             }
//         }

//         // console.log('Form Data:', formDataObject);

//         // Send the data as a JSON object in the body of the POST request
//         try {
//             const response = await fetch(submitUrl, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify(formDataObject)
//             });

//             // Handle the response
//             if (!response.ok) {
//                 const errorData = await response.json();
//                 console.log("errorData: ", errorData);
//                 displayErrors(errorData.detail);  // Function to display error messages
//                 throw new Error('Error submitting form');
//             }

//             const data = await response.json();
//             console.log('Form submitted successfully:', data);

//             // handles redirection

//             if (data.redirect_url && data.redirect_url._url) {
//                 window.location.href = data.redirect_url._url;  // Redirect to the URL provided by the backend
//             }
//         } catch (error) {
//             console.log("errorData: ", errorData);
//             console.error('Error submitting form:', error);
//         }
//     });
// }


// async function FormSubmitAndRedirect(formId, submitUrl) {
//     const form = document.getElementById(formId);
//     form.addEventListener('submit', async function (event) {
//         event.preventDefault();  // Prevent the form from submitting the traditional way

//         const formData = new FormData(form);
//         const formDataObject = {};

//         formData.forEach((value, key) => {
//             if (value === "on" || value === "") {
//                 formDataObject[key] = form.elements[key].type === "checkbox" ? form.elements[key].checked : value;
//             } else {
//                 formDataObject[key] = value;
//             }
//         });

//         // Replace empty string fields with null (for optional fields)
//         for (const key in formDataObject) {
//             if (formDataObject[key] === "") {
//                 formDataObject[key] = null;  // Set empty fields to null
//             }
//         }

//         // console.log('Form Data:', formDataObject);

//         // Send the data as a JSON object in the body of the POST request
//         try {
//             const response = await fetch(submitUrl, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify(formDataObject),
//                 redirect: 'follow',
//             });

//             if (response.redirected) {
//                 // If redirected, change the location to the new URL
//                 window.location.href = response.url;
//                 return;  // Exit the function as we are redirecting
//             }
//             // Handle the response
//             if (!response.ok) {
//                 const errorData = await response.json();
//                 // console.log("errorData: ", errorData);
//                 displayErrors(errorData.detail);  // Function to display error messages
//                 throw new Error('Error submitting form');
//             }


//         } catch (error) {
//             console.error('Error submitting form:', error);
//         }
//     });
// }

async function FormSubmitAndRedirectWithIdempotency(formId, submitUrl, actionType, formMethod) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', async function (event) {
        event.preventDefault();  // Prevent the form from submitting the traditional way

        const formData = new FormData(form);
        const formDataObject = {};

        formData.forEach((value, key) => {
            if (value === "on" || value === "") {
                formDataObject[key] = form.elements[key].type === "checkbox" ? form.elements[key].checked : value;
            } else {
                formDataObject[key] = value;
            }
        });

        // Replace empty string fields with null (for optional fields)
        for (const key in formDataObject) {
            if (formDataObject[key] === "") {
                formDataObject[key] = null;  // Set empty fields to null
            }
        }

        // **Generate & store an idempotency key if it doesn't exist**
        let idempotencyKey = sessionStorage.getItem(`${actionType}IdempotencyKey`);
        if (!idempotencyKey) {
            idempotencyKey = crypto.randomUUID();
            sessionStorage.setItem(`${actionType}IdempotencyKey`, idempotencyKey);
        }
        // console.log(sessionStorage)

        try {
            const response = await fetch(submitUrl, {
                method: formMethod,
                headers: {
                    'Content-Type': 'application/json',
                    'Idempotency-Key': idempotencyKey // **Ensure request uniqueness**
                },
                body: JSON.stringify(formDataObject),
                redirect: 'follow',
            });

            if (response.redirected) {
                // **Redirect = Success, so clear the idempotency key**
                sessionStorage.removeItem(`${actionType}IdempotencyKey`);
                window.location.href = response.url;
                return;
            }

            if (response.ok) {
                // **Explicitly check for success (2xx status) and clear the key**
                sessionStorage.removeItem(`${actionType}IdempotencyKey`);
            } else {
                const errorData = await response.json();
                console.log("error_data:", errorData);
                displayErrors(errorData.detail);  // Function to display error messages
                throw new Error('Error validating form');
            }

        } catch (error) {
            console.error('Error submitting form:', error);
        }
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