const roleSelect = document.querySelector('select[name="role"]');
const nameDiv = document.getElementById('name-div');
const passwordDiv = document.getElementById('password-div');

function toggleFields() {
    if(roleSelect.value === 'customer'){
        nameDiv.style.display = 'block';
        passwordDiv.style.display = 'none';
    } else {
        nameDiv.style.display = 'none';
        passwordDiv.style.display = 'block';
    }
}

roleSelect.addEventListener('change', toggleFields);
toggleFields();
