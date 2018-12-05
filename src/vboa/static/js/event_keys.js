import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";

/* Functions for the query interface */
export function fill_keys(){
    const divs = document.getElementsByClassName("query-keys");
    var selectors = []
    for (const div of divs){
        var selector = div.getElementsByTagName("datalist")[0];
        if (selector == null){
           selector = div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (selector.getElementsByTagName("option").length != 0){
            return false
        }
        selectors.push(selector);
    }
    query.request_info("/eboa_nav/query-jsonify-keys", fill_keys_into_selectors, selectors);
    return true
}

function fill_keys_into_selectors(selectors, keys){

    const key_names = new Set(keys.map(key => key["event_key"]))

    for (const key_name of key_names){
        for (const selector of selectors){
            selectorFunctions.add_option(selector, key_name);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
