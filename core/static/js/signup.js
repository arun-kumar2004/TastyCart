document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signup-form');
    const inputs = document.querySelectorAll('.form-control');
    const passwordInput = document.getElementById('id_password1');
    const confirmPasswordInput = document.getElementById('id_password2');
    const submitBtn = document.getElementById('submitBtn');
    const passwordStrengthMeter = document.getElementById('password-strength');
    const strengthBar = passwordStrengthMeter.querySelector('.strength-bar');
    const strengthText = passwordStrengthMeter.querySelector('.strength-text');

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const phoneRegex = /^(\+\d{1,3}[- ]?)?\d{10,15}$/;

    function showToastMsg(message, type="success") {
        if(typeof showToast !== "function") return;
        showToast(type === "success" ? "success-toast" : "error-toast", type === "success" ? 2500 : 4000, message);
    }

    // Password toggle
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const input = toggle.previousElementSibling;
            input.setAttribute('type', input.type === 'password' ? 'text' : 'password');
            toggle.classList.toggle('fa-eye');
            toggle.classList.toggle('fa-eye-slash');
        });
    });

    // Password strength
    passwordInput.addEventListener('input', () => {
        const strength = checkPasswordStrength(passwordInput.value);
        updatePasswordStrength(strength);
        validateField(passwordInput);
        validateField(confirmPasswordInput);
        checkFormValidity();
    });

    function checkPasswordStrength(password) {
        let strength = 0;
        if(password.length >= 8) strength++;
        if(/[a-z]/.test(password)) strength++;
        if(/[A-Z]/.test(password)) strength++;
        if(/[0-9]/.test(password)) strength++;
        if(/[^a-zA-Z0-9]/.test(password)) strength++;
        return strength;
    }

    function updatePasswordStrength(strength) {
        passwordStrengthMeter.style.display = 'block';
        let color='var(--weak-password)', text='Weak', width=(strength/5)*100;
        if(strength>=3){color='var(--medium-password)'; text='Medium';}
        if(strength>=5){color='var(--strong-password)'; text='Strong';}
        strengthBar.style.width = width+'%';
        strengthBar.style.backgroundColor = color;
        strengthText.textContent = text;
        strengthText.className = 'strength-text '+text.toLowerCase();
    }

    // Field validation
    inputs.forEach(input => {
        input.addEventListener('input', () => { validateField(input); checkFormValidity(); });
        input.addEventListener('blur', () => { validateField(input); checkFormValidity(); });
    });
    confirmPasswordInput.addEventListener('input', () => { validateField(confirmPasswordInput); checkFormValidity(); });

    function validateField(input) {
        const group = input.parentElement;
        const errEl = group.querySelector('.error-message');
        group.classList.remove('has-error'); if(errEl) errEl.textContent='';
        let isValid=true, message='';

        if(input.required && input.value.trim()===''){ isValid=false; message='This field is required.'; }
        else{
            switch(input.id){
                case 'id_first_name': if(input.value.trim().length<3){isValid=false; message='Name must be at least 3 characters.';} break;
                case 'id_phone': if(!phoneRegex.test(input.value.trim())){isValid=false; message='Enter a valid phone number.';} break;
                case 'id_address': if(input.value.trim().length<5){isValid=false; message='Enter a valid delivery address.';} break;
                case 'id_email': if(!emailRegex.test(input.value.trim())){isValid=false; message='Enter a valid email address.';} break;
                case 'id_password1': if(checkPasswordStrength(input.value)<3){isValid=false; message='Password too weak.';} break;
                case 'id_password2': if(input.value!==passwordInput.value){isValid=false; message='Passwords do not match.';} break;
            }
        }
        if(!isValid && message){ group.classList.add('has-error'); if(errEl) errEl.textContent=message; }
    }

    function checkFormValidity(){
        let allValid=true;
        inputs.forEach(input=>{if(input.required && (input.value.trim()==='' || input.parentElement.classList.contains('has-error'))){allValid=false;}});
        if(passwordInput.value!==confirmPasswordInput.value) allValid=false;
        submitBtn.disabled=!allValid;
    }

    // AJAX form submission
    form.addEventListener('submit', (e)=>{
        e.preventDefault();
        let isFormValid=true;
        inputs.forEach(input=>{validateField(input); if(input.parentElement.classList.contains('has-error')) isFormValid=false;});
        if(!isFormValid){ showToastMsg('Please correct the errors in the form.','error'); return; }

        const formData = new FormData(form);
        fetch(form.action, { method:"POST", body:formData, headers:{"X-Requested-With":"XMLHttpRequest"} })
        .then(res=>res.json().catch(()=>{throw new Error("Invalid server response");}))
        .then(data=>{
            if(data.success){
                showToastMsg(`✔️ ${data.name}, successfully Registered`,'success');
                setTimeout(()=>{ window.location.href=data.redirect||"/"; },2000);
            } else {
                // clear previous errors
                inputs.forEach(input=>{ const errEl=input.parentElement.querySelector('.error-message'); if(errEl) errEl.textContent=''; input.parentElement.classList.remove('has-error'); });
                // show server errors
                if(data.form_errors){
                    Object.keys(data.form_errors).forEach(field=>{
                        const fld=document.querySelector(`[name="${field}"]`);
                        if(fld){ const group=fld.parentElement; const errEl=group.querySelector('.error-message'); if(errEl) errEl.textContent=data.form_errors[field].join(' '); group.classList.add('has-error'); }
                    });
                }
                showToastMsg(data.error || "❌ Something went wrong",'error');
            }
        })
        .catch(err=>{ showToastMsg("❌ Server error, please try again.",'error'); console.error(err); });
    });
});
