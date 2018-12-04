import * as query from "./query.js";
import * as selectors from "./selectors.js";

/* Functions for the query interface */
export function fill_ers(){
    console.log("fill_ers")
    const div_er_like = document.querySelector("#div-er-like");
    const datalist_er_like = div_er_like.getElementsByTagName("datalist")[0];
    const div_ers = document.querySelector("#div-ers");
    const select_ers = div_ers.getElementsByTagName("select")[0];
    
    const parameters = {
        "datalist_er_like": datalist_er_like,
        "select_ers": select_ers
    }
    query.request_info("/eboa_nav/query-jsonify-ers", fill_ers_into_selectors, parameters);
}

function fill_ers_into_selectors(parameters, ers){

    const er_names = new Set(ers.map(er => er["name"]))

    for (const er_name of er_names){
        selectors.add_option(parameters["datalist_er_like"], er_name);
        selectors.add_option(parameters["select_ers"], er_name);
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
