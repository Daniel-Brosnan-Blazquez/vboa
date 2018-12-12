/* Function to add options to the specified DOM */
export function add_option(dom_id, value){
    var option = document.createElement("option");
    option.innerHTML = value
    option.setAttribute("value", value);
    dom_id.appendChild(option);
}

/* Function to add options to the specified DOM with a corresponding tooltip */
export function add_option_tooltip(dom_id, value, tooltip){
    var option = document.createElement("option");
    option.innerHTML = value
    option.setAttribute("value", value);
    option.setAttribute("data-toggle", "tooltip");
    option.setAttribute("data-placement", "right");
    option.setAttribute("title", tooltip);
    dom_id.appendChild(option);
}
