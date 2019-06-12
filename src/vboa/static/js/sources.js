import * as dates from "./dates.js";
import * as graph from "./graph.js";
import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";

/*
* Functions for the EBOA navigation
*/

/* Function to establish the groups of sources using the DIM signatures */
function create_sources_groups_by_dim_signature(sources){
    var groups = [];
    var dim_signatures = new Set(sources.map(source => source["dim_signature"]))

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
        "<tr><td>Source UUID</td><td>" + source["id"] + "</td></tr>" +
        "<tr><td>Name</td><td>" + source["name"] + "</td></tr>" +
        "<tr><td>DIM Signature</td><td>" + source["dim_signature"] + "</td></tr>" +
        "<tr><td>Processor</td><td>" + source["processor"] + "</td></tr>" +
        "<tr><td>Version of processor</td><td>" + source["version"] + "</td></tr>" +
        "<tr><td>Validity start</td><td>" + source["validity_start"] + "</td></tr>" +
        "<tr><td>Validity stop</td><td>" + source["validity_stop"] + "</td></tr>" +
        "<tr><td>Generation time</td><td>" + source["generation_time"] + "</td></tr>" +
        "<tr><td>Ingestion time</td><td>" + source["ingestion_time"] + "</td></tr>" +
        "<tr><td>Ingestion duration</td><td>" + source["ingestion_duration"] + "</td></tr>" +
        "<tr><td>Number of events</td><td>" + source["number_of_events"] + "</td></tr>" +
        "<tr><td>Ingestion time - generation time (m)</td><td>" + ingestion_minus_generation + "</td></tr>" +
        "</tr></table>"
};

export function create_source_validity_timeline(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources){
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
    for (const source of sources){
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
    for (const source of sources){
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
    for (const source of sources){
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
    for (const source of sources){
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

/*
* Query functions
*/

/* Functions for the query interface */
export function fill_sources(){
    const divs = document.getElementsByClassName("query-sources");
    var source_selectors = []
    var processor_selectors = []
    for (const div of divs){
        const source_divs = div.getElementsByClassName("query-source-names");
        const processor_divs = div.getElementsByClassName("query-source-processors");

        /* Source */
        for (const source_div of source_divs){
            var source_selector = source_div.getElementsByTagName("datalist")[0];
            if (source_selector == null){
                source_selector = source_div.getElementsByTagName("select")[0];
            }
            /* If the options were already filled exit */
            if (source_div.getElementsByTagName("option").length != 0){
                return false
            }
            source_selectors.push(source_selector);
        }

        /* Processor */
        for (const processor_div of processor_divs){
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
    }
    var selectors = {
        "source_selectors": source_selectors,
        "processor_selectors": processor_selectors
    }
    query.request_info("/eboa_nav/query-jsonify-sources", fill_sources_into_selectors, selectors);
    return true
}

function fill_sources_into_selectors(selectors, sources){

    var source_names = new Set(sources.map(source => source["name"]))
    var processors = new Set(sources.map(source => source["processor"]))
    for (const source of source_names){
        for (const selector of selectors["source_selectors"]){
            selectorFunctions.add_option(selector, source);
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

export function fill_statuses(){
    const divs = document.getElementsByClassName("query-source-statuses");
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
    query.request_info("/eboa_nav/get-source-status", fill_statuses_into_selectors, selectors);
    return true
}

function fill_statuses_into_selectors(selectors, statuses){

    for (const status of Object.keys(statuses)){
        for (const selector of selectors){
            selectorFunctions.add_option_tooltip(selector, status, statuses[status]["message"]);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");

    /* Activate tooltips */
    jQuery("[data-toggle='tooltip']").tooltip();
}
