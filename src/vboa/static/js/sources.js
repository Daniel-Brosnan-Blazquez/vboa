import * as dates from "./dates.js";
import * as graph from "./graph.js";
import * as query from "./query.js";
import * as selectors from "./selectors.js";

/* Functions for the query interface */
export function fill_sources(){
    console.log("fill_sources")
    const div_source_like = document.querySelector("#div-source-like");
    const datalist_source_like = div_source_like.getElementsByTagName("datalist")[0];
    const div_sources = document.querySelector("#div-sources");
    const select_sources = div_sources.getElementsByTagName("select")[0];
    
    const parameters = {
        "datalist_source_like": datalist_source_like,
        "select_sources": select_sources
    }
    query.request_info("/eboa_nav/query-jsonify-sources", fill_sources_into_selectors, parameters);
}

function fill_sources_into_selectors(parameters, sources){

    const source_names = new Set(sources.map(source => source["name"]))

    for (const source_name of source_names){
        selectors.add_option(parameters["datalist_source_like"], source_name);
        selectors.add_option(parameters["select_sources"], source_name);
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}


/* Function to establish the groups of sources using the DIM signatures */
function create_sources_groups_by_dim_signature(sources){
    var groups = [];
    var dim_signatures = new Set(sources["sources"].map(source => source["dim_signature"]))

    for (const dim_signature of dim_signatures){
        groups.push({
            id: dim_signature,
            content: dim_signature,
            options: {
                drawPoints: {
                    style: "circle"
                }
            }
        })
    }
    return groups;
}

/* Function to create the text for the tooltip of the source information */
function create_source_tooltip_text(source){
    const ingestion_minus_generation = dates.date_difference_in_m(source["ingestion_time"], source["generation_time"])
    return "<table border='1'>" +
        "<tr><td>Source UUID</td><td>" + source["id"] + "</td>" +
        "<tr><td>Name</td><td>" + source["name"] + "</td>" +
        "<tr><td>DIM Signature</td><td>" + source["dim_signature"] + "</td>" +
        "<tr><td>Processor</td><td>" + source["processor"] + "</td>" +
        "<tr><td>Version of processor</td><td>" + source["version"] + "</td>" +
        "<tr><td>Validity start</td><td>" + source["validity_start"] + "</td>" +
        "<tr><td>Validity stop</td><td>" + source["validity_stop"] + "</td>" +
        "<tr><td>Generation time</td><td>" + source["generation_time"] + "</td>" +
        "<tr><td>Ingestion time</td><td>" + source["ingestion_time"] + "</td>" +
        "<tr><td>Ingestion duration</td><td>" + source["ingestion_duration"] + "</td>" +
        "<tr><td>Number of events</td><td>" + source["number_of_events"] + "</td>" +
        "<tr><td>Ingestion time - generation time (m)</td><td>" + ingestion_minus_generation + "</td>" +
        "</tr></table>"
};

export function create_source_validity_timeline(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources["sources"]){
        items.push({
            id: source["id"],
            group: source["dim_signature"],
            start: source["validity_start"],
            end: source["validity_stop"],
            tooltip: create_source_tooltip_text(source)
        })
    }
    graph.display_timeline(dom_id, items, groups);

};

export function create_source_generation_to_ingestion_timeline(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources["sources"]){
        items.push({
            id: source["id"],
            group: source["dim_signature"],
            start: source["generation_time"],
            end: source["ingestion_time"],
            tooltip: create_source_tooltip_text(source)
        })
    }
    graph.display_timeline(dom_id, items, groups);

};

export function create_source_number_events_xy(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources["sources"]){
        items.push({
            id: source["id"],
            group: source["dim_signature"],
            x: source["ingestion_time"],
            y: source["number_of_events"],
            tooltip: create_source_tooltip_text(source)
        })
    }
    const options = {
        legend: true,
        dataAxis: {
            left: {
                title: {
                    text: "Number of events"
                }
            }
        }
    };

    graph.display_x_time(dom_id, items, groups, options);

};

export function create_source_ingestion_duration_xy(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources["sources"]){
        items.push({
            id: source["id"],
            group: source["dim_signature"],
            x: source["ingestion_time"],
            y: dates.interval_to_seconds(source["ingestion_duration"]),
            tooltip: create_source_tooltip_text(source)
        })
    }

    const options = {
        legend: true,
        dataAxis: {
            left: {
                title: {
                    text: "Seconds"
                }
            }
        }
    };

    graph.display_x_time(dom_id, items, groups, options);

};

export function create_source_generation_time_to_ingestion_time_xy(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources["sources"]){
        const ingestion_minus_generation = dates.date_difference_in_m(source["ingestion_time"], source["generation_time"])
        items.push({
            id: source["id"],
            group: source["dim_signature"],
            x: source["ingestion_time"],
            y: ingestion_minus_generation,
            tooltip: create_source_tooltip_text(source)
        })
    }

    const options = {
        legend: true,
        dataAxis: {
            left: {
                title: {
                    text: "Minutes"
                }
            }
        }
    };

    graph.display_x_time(dom_id, items, groups, options);

};
