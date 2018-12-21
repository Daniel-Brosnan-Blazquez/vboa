import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";

/* Functions for the query interface */
export function fill_annotation_cnfs(){
    const divs = document.getElementsByClassName("query-annotation-cnfs");
    var annotation_name_selectors = []
    var annotation_system_selectors = []
    for (const div of divs){
        const annotation_name_div = div.getElementsByClassName("query-annotation-names")[0];
        const annotation_system_div = div.getElementsByClassName("query-annotation-systems")[0];

        /* Annotation name */
        var annotation_name_selector = annotation_name_div.getElementsByTagName("datalist")[0];
        if (annotation_name_selector == null){
           annotation_name_selector = annotation_name_div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (annotation_name_div.getElementsByTagName("option").length != 0){
            return false
        }
        annotation_name_selectors.push(annotation_name_selector);

        /* Annotation system */
        var annotation_system_selector = annotation_system_div.getElementsByTagName("datalist")[0];
        if (annotation_system_selector == null){
           annotation_system_selector = annotation_system_div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (annotation_system_div.getElementsByTagName("option").length != 0){
            return false
        }
        annotation_system_selectors.push(annotation_system_selector);
    }
    var selectors = {
        "annotation_name_selectors": annotation_name_selectors,
        "annotation_system_selectors": annotation_system_selectors
    }
    query.request_info("/eboa_nav/query-jsonify-annotation-cnfs", fill_annotation_cnfs_into_selectors, selectors);
    return true
}

function fill_annotation_cnfs_into_selectors(selectors, annotation_cnfs){

    var annotation_names = new Set(annotation_cnfs.map(annotation_cnf => annotation_cnf["name"]))
    var annotation_systems = new Set(annotation_cnfs.map(annotation_cnf => annotation_cnf["system"]))
    for (const annotation_name of annotation_names){
        for (const selector of selectors["annotation_name_selectors"]){
            selectorFunctions.add_option(selector, annotation_name);
        }
    }
    for (const annotation_system of annotation_systems){
        for (const selector of selectors["annotation_system_selectors"]){
            selectorFunctions.add_option(selector, annotation_system);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
