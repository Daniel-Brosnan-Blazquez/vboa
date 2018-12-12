import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";

/* Functions for the query interface */
export function fill_dim_signatures(){
    const divs = document.getElementsByClassName("query-dims");
    var dim_signature_selectors = []
    var processor_selectors = []
    for (const div of divs){
        const dim_signature_div = div.getElementsByClassName("query-dim-signatures")[0];
        const processor_div = div.getElementsByClassName("query-processors")[0];

        /* DIM signature */
        var dim_signature_selector = dim_signature_div.getElementsByTagName("datalist")[0];
        if (dim_signature_selector == null){
           dim_signature_selector = dim_signature_div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (dim_signature_div.getElementsByTagName("option").length != 0){
            return false
        }
        dim_signature_selectors.push(dim_signature_selector);

        /* Processor */
        var processor_selector = processor_div.getElementsByTagName("datalist")[0];
        if (processor_selector == null){
           processor_selector = processor_div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (processor_div.getElementsByTagName("option").length != 0){
            return false
        }
        processor_selectors.push(processor_selector);
    }
    var selectors = {
        "dim_signature_selectors": dim_signature_selectors,
        "processor_selectors": processor_selectors
    }
    query.request_info("/eboa_nav/query-jsonify-dim-signatures", fill_dim_signatures_into_selectors, selectors);
    return true
}

function fill_dim_signatures_into_selectors(selectors, dim_signatures){

    var dim_signature_names = new Set(dim_signatures.map(dim_signature => dim_signature["dim_signature"]))
    var processors = new Set(dim_signatures.map(dim_signature => dim_signature["dim_exec_name"]))
    for (const dim_signature_name of dim_signature_names){
        for (const selector of selectors["dim_signature_selectors"]){
            selectorFunctions.add_option(selector, dim_signature_name);
        }
    }
    for (const processor of processors){
        for (const selector of selectors["processor_selectors"]){
            selectorFunctions.add_option(selector, processor);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
