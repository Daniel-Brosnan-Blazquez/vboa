import * as query from "./query.js";
import * as selectors from "./selectors.js";

/* Functions for the query interface */
export function fill_gauges(){
    console.log("fill_gauges")
    const div_gauge_name_like = document.querySelector("#div-gauge-name-like");
    const datalist_gauge_name_like = div_gauge_name_like.getElementsByTagName("datalist")[0];
    const div_gauge_system_like = document.querySelector("#div-gauge-system-like");
    const datalist_gauge_system_like = div_gauge_system_like.getElementsByTagName("datalist")[0];
    const div_gauge_names = document.querySelector("#div-gauge-names");
    const select_gauge_names = div_gauge_names.getElementsByTagName("select")[0];
    const div_gauge_systems = document.querySelector("#div-gauge-systems");
    const select_gauge_systems = div_gauge_systems.getElementsByTagName("select")[0];
    
    const parameters = {
        "datalist_gauge_name_like": datalist_gauge_name_like,
        "datalist_gauge_system_like": datalist_gauge_system_like,
        "select_gauge_names": select_gauge_names,
        "select_gauge_systems": select_gauge_systems
    }
    query.request_info("/eboa_nav/query-jsonify-gauges", fill_gauges_into_selectors, parameters);
}

function fill_gauges_into_selectors(parameters, gauges){

    var gauge_names = new Set(gauges.map(gauge => gauge["name"]))
    var gauge_systems = new Set(gauges.map(gauge => gauge["system"]))
    for (const gauge_name of gauge_names){
        selectors.add_option(parameters["datalist_gauge_name_like"], gauge_name);
        selectors.add_option(parameters["select_gauge_names"], gauge_name);
    }
    for (const gauge_system of gauge_systems){
        selectors.add_option(parameters["datalist_gauge_system_like"], gauge_system);
        selectors.add_option(parameters["select_gauge_systems"], gauge_system);
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}
