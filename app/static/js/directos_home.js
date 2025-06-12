var btnCreateRoom = document.querySelector('#btn-create-room');
var inputNameDisplay = document.querySelector('#input_name_display');
var inputDescription = document.querySelector('#input_descripcion');
var inputName = document.querySelector('#input_name');
var formTitle = document.querySelector('#form-title');

window.onload = function() {
    console.log(usertype);
    inputName.value = '';
    if (usertype == 'entrenador'){
        var formContainer = document.querySelector('#form-container');
        formContainer.style.visibility = 'visible';
        formContainer.style.display = '';

        btnCreateRoom.addEventListener('click', () => {
            console.log("He creado una sala");
            createRoom();
        });
    }

    if(error!=''){
        formTitle.innerHTML=error;
    }
    else{
        formTitle.innerHTML='Crea tu sala';
    }
}

function createRoom(){
    if (inputNameDisplay.value == '' || inputDescription.value ==''){
        formTitle.innerHTML='Tienes que cubrir ambos campos';
        return;
    }

    console.log(inputNameDisplay.value);

    var caracteres = /^[a-zA-Z0-9\d\ _]+$/;

    if(!caracteres.test(inputNameDisplay.value)){
        formTitle.innerHTML='Caracteres inválidos en el nombre';
        return;
    }

    var auxInputName = inputNameDisplay.value.split(' ');

    for (i in auxInputName){
        if(i==0) inputName.value = auxInputName[i];
        else inputName.value += '_' + auxInputName[i];
    }
    
    console.log(inputName.value);
    document.querySelector('form').submit();
}
