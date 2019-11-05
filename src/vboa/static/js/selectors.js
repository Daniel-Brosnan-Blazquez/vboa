import * as query from "./query.js";

/* Function to add options to the specified DOM */
export function add_option(node, value){
    if (jQuery(node).find("option[value='" + value + "']").length < 1){
        var option = document.createElement("option");
        option.innerHTML = value;
        option.setAttribute("value", value);
        node.appendChild(option);
    }
}

/* Function to add options to the specified DOM with a corresponding tooltip */
export function add_option_tooltip(node, value, tooltip){
    var option = document.createElement("option");
    option.innerHTML = value
    option.setAttribute("value", value);
    option.setAttribute("data-toggle", "tooltip");
    option.setAttribute("data-placement", "right");
    option.setAttribute("title", tooltip);
    node.appendChild(option);
}

export function fill_elements_into_selector(input_node, route, field_name, limit, offset){
    
    var parent_node = input_node.parentNode

    var selector = parent_node.getElementsByTagName("select")[0];
    var loader = parent_node.getElementsByClassName("circle")[0];
    loader.className = "circle loader"

    var parameters = {
        "input_node": input_node,
        "selector": selector,
        "limit": limit,
        "offset": offset,
        "field_name": field_name
    }
    query.request_info(route + "?search=" + input_node.value + "&limit=" + limit + "&offset=" + offset, do_fill_elements_into_selector, parameters);
    return true
    
}

function do_fill_elements_into_selector(parameters, sources){
    
    var source_names = new Set(sources.map(source => source[parameters["field_name"]]))
    for (const source of source_names){
        add_option(parameters["selector"], source);
    }

    parameters["selector"].style.display = "block"

    var parent_node = parameters["input_node"].parentNode
    var loader = parent_node.getElementsByClassName("circle")[0];
    loader.className = "circle"
    
}
