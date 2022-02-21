var i = 1;
function add_input_form() {
    var input_datax = document.createElement('input');
    input_datax.type = 'text';
    input_datax.id = 'inputform_x' + i;
    input_datax.placeholder = 'x' + i;
    var parentx = document.getElementById('form_area');
    parentx.appendChild(input_datax);
    var input_datay = document.createElement('input');
    input_datay.type = 'text';
    input_datay.id = 'inputform_y' + i;
    input_datay.placeholder = 'y' + i;
    var parenty = document.getElementById('form_area');
    parenty.appendChild(input_datay);
    parenty.innerHTML += "<br>";
    i++;
    
}

function layout_save() {
    /*
    for (let j = 0; j < i-1; j++){
        eval("var x" + j + "= document.getElementById('inputform_x0');" );
    }
    */
    eval("var x" + 0 + "= document.getElementById('inputform_x0');" );
    document.getElementById("output").innerHTML = x0.value;

    //var x0 = document.getElementById("inputform_x0");
}
