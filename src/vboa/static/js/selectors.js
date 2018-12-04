/* Function to add options to the specified DOM */
export function add_option(dom_id, value){
    var option = document.createElement("option");
    option.innerHTML = value
    option.setAttribute("value", value);
    dom_id.appendChild(option);
}
