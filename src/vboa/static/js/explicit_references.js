import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";

/* Functions for the query interface */
export function fill_ers(){
    const divs = document.getElementsByClassName("query-ers");
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
    query.request_info("/eboa_nav/query-jsonify-ers", fill_ers_into_selectors, selectors);
    return true
}

function fill_ers_into_selectors(selectors, ers){

    const er_names = new Set(ers.map(er => er["explicit_ref"]))

    for (const er_name of er_names){
        for (const selector of selectors){
            selectorFunctions.add_option(selector, er_name);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
