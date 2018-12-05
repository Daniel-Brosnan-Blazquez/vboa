import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";

/* Functions for the query interface */
export function fill_dim_signatures(){
    const divs = document.getElementsByClassName("query-dim-signatures");
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
    query.request_info("/eboa_nav/query-jsonify-dim-signatures", fill_dim_signatures_into_selectors, selectors);
    return true
}

function fill_dim_signatures_into_selectors(selectors, dim_signatures){

    const dim_signature_names = new Set(dim_signatures.map(dim_signature => dim_signature["dim_signature"]))

    for (const dim_signature_name of dim_signature_names){
        for (const selector of selectors){
            selectorFunctions.add_option(selector, dim_signature_name);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
