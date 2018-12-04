import * as query from "./query.js";
import * as selectors from "./selectors.js";

/* Functions for the query interface */
export function fill_keys(){
    console.log("fill_keys")
    const div_key_like = document.querySelector("#div-key-like");
    const datalist_key_like = div_key_like.getElementsByTagName("datalist")[0];
    const div_keys = document.querySelector("#div-keys");
    const select_keys = div_keys.getElementsByTagName("select")[0];
    
    const parameters = {
        "datalist_key_like": datalist_key_like,
        "select_keys": select_keys
    }
    query.request_info("/eboa_nav/query-jsonify-keys", fill_keys_into_selectors, parameters);
}

function fill_keys_into_selectors(parameters, keys){

    const key_names = new Set(keys.map(key => key["name"]))

    for (const key_name of key_names){
        selectors.add_option(parameters["datalist_key_like"], key_name);
        selectors.add_option(parameters["select_keys"], key_name);
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
