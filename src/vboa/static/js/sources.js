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
                },
                interpolation: false
            }
        })
    }
    return groups;
}

/* Function to create the text for the tooltip of the source information */
function create_source_tooltip_text(source){
    const ingestion_minus_generation = dates.date_difference_in_m(source["ingestion_time"], source["generation_time"])

    var ingestion_error = "<span class='bold-green'>" + source["ingestion_error"] + "</span>"
    if (source["ingestion_error"] == "True"){
        ingestion_error = "<span class='bold-red'>" + source["ingestion_error"] + "</span>"
    }
    
    return "<table border='1'>" +
        "<tr><td>Source UUID</td><td>" + source["id"] + "</td></tr>" +
        "<tr><td>Name</td><td>" + source["name"] + "</td></tr>" +
        "<tr><td>DIM Signature</td><td>" + source["dim_signature"] + "</td></tr>" +
        "<tr><td>Processor</td><td>" + source["processor"] + "</td></tr>" +
        "<tr><td>Version of processor</td><td>" + source["version"] + "</td></tr>" +
        "<tr><td>Validity start</td><td>" + source["validity_start"] + "</td></tr>" +
        "<tr><td>Validity stop</td><td>" + source["validity_stop"] + "</td></tr>" +
        "<tr><td>Reported validity start</td><td>" + source["reported_validity_start"] + "</td></tr>" +
        "<tr><td>Reported validity stop</td><td>" + source["reported_validity_stop"] + "</td></tr>" +
        "<tr><td>Reception time</td><td>" + source["reception_time"] + "</td></tr>" +
        "<tr><td>Ingestion time</td><td>" + source["ingestion_time"] + "</td></tr>" +
        "<tr><td>Processing duration (hh:mm:ss.000)</td><td>" + source["processing_duration"] + "</td></tr>" +
        "<tr><td>Ingestion duration (hh:mm:ss.000)</td><td>" + source["ingestion_duration"] + "</td></tr>" +
        "<tr><td>Generation time</td><td>" + source["generation_time"] + "</td></tr>" +
        "<tr><td>Reported generation time</td><td>" + source["reported_generation_time"] + "</td></tr>" +
        "<tr><td>Number of events</td><td>" + source["number_of_events"] + "</td></tr>" +
        "<tr><td>Priority</td><td>" + source["priority"] + "</td></tr>" +
        "<tr><td>Ingestion completeness</td><td>" + source["ingestion_completeness"] + "</td></tr>" +
        "<tr><td>Ingestion completeness message</td><td>" + source["ingestion_completeness_message"] + "</td></tr>" +
        "<tr><td>Ingestion time - generation time (m)</td><td>" + ingestion_minus_generation + "</td></tr>" +
        "<tr><td>Ingestion error</td><td>" + ingestion_error + "</td></tr>" +
        "</table>"
};

export function create_source_validity_timeline(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources){
        var item = {
            id: source["id"],
            group: source["dim_signature"],
            start: source["reported_validity_start"],
            end: source["reported_validity_stop"],
            tooltip: create_source_tooltip_text(source)
        }
        if ("ingestion_error" in source && source["ingestion_error"] == "True"){
            item["className"] = "background-red"
        }
        else{
            item["className"] = "background-green"
        }
        items.push(item)
    }
    graph.display_timeline(dom_id, items, groups);

};

export function create_source_generation_to_ingestion_timeline(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources){
        var item = {
            id: source["id"],
            group: source["dim_signature"],
            start: source["reported_generation_time"],
            end: source["ingestion_time"],
            tooltip: create_source_tooltip_text(source)
        }
        if ("ingestion_error" in source && source["ingestion_error"] == "True"){
            item["className"] = "background-red"
        }
        else{
            item["className"] = "background-green"
        }
        items.push(item)
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
            y: dates.interval_to_minutes(source["ingestion_duration"]),
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

export function create_source_generation_time_to_ingestion_time_xy(sources, dom_id){
    const groups = create_sources_groups_by_dim_signature(sources);
    var items = [];
    for (const source of sources){
        const ingestion_minus_generation = dates.date_difference_in_m(source["ingestion_time"], source["reported_generation_time"])
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

/* Function to show the statuses related to a source */
export function expand_source_statuses(dom_id, source_uuid){
    
    var table = jQuery("#" + dom_id).closest("table").DataTable();
    var tr = jQuery("#" + dom_id).closest("tr");
    var tdi = tr.find("i.fa");
    var row = table.row(tr);
    
    if (row.child.isShown()) {
        // This row is already open - close it
        row.child.hide();
        tr.removeClass('shown');
        tdi.first().removeClass('fa-minus-square');
        tdi.first().removeClass('red');
        tdi.first().addClass('fa-plus-square');
        tdi.first().addClass('green');
    }
    else {
        // Open this row
        var parameters = {
            "row": row,
            "insert_method": insert_in_datatable
        }
        query.request_info("/eboa_nav/query-jsonify-source-statuses/" + source_uuid, show_source_statuses, parameters);
        tr.addClass('shown');
        tdi.first().removeClass('fa-plus-square');
        tdi.first().removeClass('green');
        tdi.first().addClass('fa-minus-square');
        tdi.first().addClass('red');
    }
};

function show_source_statuses(parameters, statuses){

    var row = parameters["row"]

    var table = '<table class="table">' +
        '<thead>' +
        '<tr>' +
        '<th>Status</th>' +
        '<th>TIme stamp</th>' +
        '<th>Log</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody>';

    for (const status of statuses){
        table = table + 
            '<tr>' +
            '<td>' + status["status"] + '</td>' +
            '<td>' + status["time_stamp"] + '</td>' +
            '<td>' + status["log"] + '</td>' +
            '</tr>'
    }
    table = table + '</tbody>' +
        '</table>';

    parameters["insert_method"](row, table);
    
}

function insert_in_datatable(row, table){
    row.child(table).show();
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
