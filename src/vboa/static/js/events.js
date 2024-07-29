import * as query from "./query.js";
import * as dates from "./dates.js";
import * as graph from "./graph.js";

/*
* Functions for the EBOA navigation
*/

/* Function to create the text for the tooltip of the event information */
function create_event_tooltip_text(event){
    const event_duration = dates.date_difference_in_m(event["stop"], event["start"])
    
    return "<table border='1'>" +
        "<tr><td>UUID</td><td>" + event['id'] + "</td></tr>" +
        "<tr><td>Explicit reference</td><td><a href='/eboa_nav/query-er/" + event["explicit_ref_uuid"] + "'>" + event['explicit_reference'] + "</a></td></tr>" +
        "<tr><td>Gauge name</td><td>" + event['gauge']['name'] + "</td></tr>" +
        "<tr><td>Gauge system</td><td>" + event['gauge']['system'] + "</td></tr>" +
        "<tr><td>Start</td><td>" + event["start"] + "</td></tr>" +
        "<tr><td>Stop</td><td>" + event["stop"] + "</td></tr>" +
        "<tr><td>Duration (m)</td><td>" + event_duration.toFixed(3) + "</td></tr>" +
        "<tr><td>Source</td><td><a href='/eboa_nav/query-source/" + event["source_uuid"] + "'>" + event['source'] + "</a></td></tr>" +
        "<tr><td>Ingestion time</td><td>" + event['ingestion_time'] + "</td></tr>" +
        "<tr><td>Links</td><td><a href='/eboa_nav/query-event-links/" + event["id"] + "'><i class='fa fa-link'></i></a></td></tr>" +
        "<tr id='expand-tooltip-values-event-" + event["id"] + "'><td>Values</td><td><i class='fa fa-plus-square green' onclick='" + 'vboa.expand_event_values_in_tooltip("expand-tooltip-values-event-' + event["id"] + '", "' + event["id"] + '")' + "' data-toggle='tooltip' title='Click to show the related values'></i></td></tr>" +
        "</table>"
};

/* Function to create a network graph for the EBOA navigation view */
export function create_event_network(linked_events, dom_id){
    var unique_event_uuids = new Set(linked_events.map(event => event["id"]));
    var prime_event_id = linked_events.filter(event => event["label"] == "prime_events").map(event => event["id"])[0];

    var nodes = []
    var edges = []
    for (const id of unique_event_uuids){
        var associated_events = linked_events.filter(event => event["id"] == id)

        for (const event of associated_events){
            var shape = "box";
            var background_color = "lightblue";
            if (event["label"] == "prime_events"){
                shape = "elipse";
                background_color = "lightgreen";
            }
            else if (event["label"] == "events_linking"){
                edges.push({
                    "from": event["id"],
                    "to": prime_event_id,
                    "arrows": "to",
                    "label": event["link_name"]
                })
            }
            else{
                edges.push({
                    "from": prime_event_id,
                    "to": event["id"],
                    "arrows": "to",
                    "label": event["link_name"]
                })
            }
        }
        nodes.push({
            "id": associated_events[0]["id"],
            "color": background_color,
            "shape": shape,
            "tooltip": create_event_tooltip_text(associated_events[0]),
            "label": "Gauge name: " + associated_events[0]['gauge']['name'] + "\nGauge system: " + associated_events[0]['gauge']['system'] + "\nStart: " + associated_events[0]['start'] + "\nStop: " + associated_events[0]['stop'],
            "font": {"align": "left"}
        });
    }
    graph.display_network(dom_id, nodes, edges);

};

/* Function to create a timeline graph for the EBOA navigation view */
export function create_event_timeline(events, dom_id){
    var groups = [];
    var items = [];

    var gauge_systems = new Set(events.map(event => event["gauge"]["system"]))

    for (const gauge_system of gauge_systems){
        var associated_gauges = new Set(events.filter(event => event["gauge"]["system"] == gauge_system).map(event => event["gauge"]["name"]));
        var tree_level = 1;
        if (gauge_system != "None"){
            var associated_gauge_ids = Array.from(new Set(events.filter(event => event["gauge"]["system"] == gauge_system).map(event => "GAUGE_NAME_" + event["gauge"]["system"] + "_" + event["gauge"]["name"])));
            groups.push({
                id: "GAUGE_SYSTEM_" + gauge_system,
                treeLevel: 1,
                content: gauge_system,
                nestedGroups: associated_gauge_ids
            })
            tree_level = 2;
        }
        for (const associated_gauge of associated_gauges){
            var id = "GAUGE_NAME_" + associated_gauge;
            if (gauge_system != "None"){
                id = "GAUGE_NAME_" + gauge_system + "_" + associated_gauge
            }
            groups.push({
                id: id,
                treeLevel: tree_level,
                content: associated_gauge
            })
        }
    }

    var unique_event_uuids = new Set(events.map(event => event["id"]));
    for (const event_uuid of unique_event_uuids){
        var event = events.filter(event => event["id"] == event_uuid)[0]
        var group = "GAUGE_NAME_" + event["gauge"]["name"]
        if (event["gauge"]["system"] != "None"){
            group = "GAUGE_NAME_" + event["gauge"]["system"] + "_" + event["gauge"]["name"]
        }

        items.push({
            id: event["id"],
            group: group,
            start: event["start"],
            end: event["stop"],
            tooltip: create_event_tooltip_text(event)
        })
    }

    graph.display_timeline(dom_id, items, groups);

};

/* Function to create a map for the EBOA navigation view */
export function create_event_map(events_geometries, dom_id){

    var polygons = [];

    for (const event_geometries of events_geometries){
        var i = 0;
        for (const geometry of event_geometries["geometries"]){
            polygons.push({"polygon": geometry["value"],
                           "id": event_geometries["id"] + "_" + i,
                           "tooltip": create_event_tooltip_text(event_geometries)})
            i = i + 1;
        }
    }
    graph.display_map(dom_id, polygons);
};

/*
* Functions to build the needed structures for the graph library (data is already formated by the calling module)

/* Function to prepare data from events for a bar graph given the events to be displayed */
export function prepare_events_data_for_bar(events, items, groups){

    var event_groups = new Set(events.map(event => event["group"]))

    for (const group of event_groups){
        groups.push({
            id: group,
            content: group,
        })
    }

    for (const event of events){
        var item = {
            id: event["id"],
            group: event["group"],
            x: event["x"],
            y: event["y"],
            tooltip: event["tooltip"]
        }
        items.push(item)
    }

};

/* Function to prepare the timeline groups following the nested logic */
function prepare_timeline_groups(groups, timeline_groups){

    for (const group of groups){
        var timeline_group = timeline_groups;
        var id = ""
        for (const label of group.split(";")){
            // Id is the concatenation of the previous and current ids
            id = id + label;
            // Check if label already exists in dictionary
            if (!(label in timeline_group)){
                timeline_group[label] = {"id": id, "subgroups": {}};
            }
            // Timeline group now points to the subgroups
            timeline_group = timeline_group[label]["subgroups"];
            id = id + ";";
        }
    }
    
}

function populate_timeline_groups(timeline_groups, groups, tree_level){

    for (const group in timeline_groups){

        // Prepare nested groups
        var nested_groups = [];
        for (const nested_group in timeline_groups[group]["subgroups"]){
            nested_groups.push(timeline_groups[group]["subgroups"][nested_group]["id"])
        }

        if (nested_groups.length > 0){
            // Prepare group with nested groups
            groups.push({
                id: timeline_groups[group]["id"],
                content: group,
                treeLevel: tree_level,
                nestedGroups: nested_groups
            })
        }
        else{
            // Prepare group without nested groups
            groups.push({
                id: timeline_groups[group]["id"],
                content: group,
                treeLevel: tree_level
            })
        }

        // Recursive call to include subgroups
        populate_timeline_groups(timeline_groups[group]["subgroups"], groups, tree_level + 1)
    }
    
}

/* Function to prepare data from events for a timeline given the events to be displayed */
export function prepare_events_data_for_timeline(events, items, groups){

    // Groups should be only defined by group. event["timeline"] is mantained for backwards compatibility. 
    var event_groups = new Set(events.map(event => event["group"] + ";" + event["timeline"]));

    // Obtain the nested timeline groups
    var timeline_groups = {};
    var event_groups_array = Array.from(event_groups);
    prepare_timeline_groups(event_groups_array, timeline_groups);

    // Populate groups for the timeline with nested logic
    populate_timeline_groups(timeline_groups, groups, 1);

    // Populate items (be aware that event["timeline"] is mantained for backwards compatibility.)
    for (const event of events){
        var item = {
            id: event["id"],
            group: event["group"] + ";" + event["timeline"],
            content: event["content"],
            start: event["start"],
            end: event["stop"],
            tooltip: event["tooltip"]
        }
        if ("className" in event){
            item["className"] = event["className"]
        }
        items.push(item)
    }

};

/* Function to prepare data from events for a XY graph given the events to be displayed */
export function prepare_events_data_for_xy(events, items, groups, title){

    var event_groups = new Set(events.map(event => event["group"]))

    for (const group of event_groups){
        groups.push({
            id: group,
            content: group,
            options: {
                drawPoints: {
                    style: "circle"
                },
                interpolation: false
            }
        })
    }

    for (const event of events){
        items.push({
            id: event["id"],
            group: event["group"],
            x: event["x"],
            y: event["y"],
            tooltip: event["tooltip"]
        })
    }

    var options = {
        legend: true,
        dataAxis: {
            left: {
                title: {
                    text: title
                }
            }
        }
    };
    return options;

};

export function prepare_events_geometries_for_map(events_geometries, polygons){

    for (const event_geometries of events_geometries){
        var i = 0;
        for (const geometry of event_geometries["geometries"]){
            var polygon = {"polygon": geometry["value"],
                           "id": event_geometries["id"] + "_" + i,
                           "tooltip": event_geometries["tooltip"]};
            if ("style" in event_geometries){
                polygon["style"] = event_geometries["style"]
            }
            polygons.push(polygon)
            i = i + 1;
        }
    }
}

/*
* Query functions
*/

/* Function to add more value filter selectors when commanded */
export function add_value_query(dom_id){
    
    jQuery.ajax({url: "/static/html/more_value_query_events.html",
                cache: false}).done(function (data){
                    jQuery("#" + dom_id).append(data);
                });

};

/* Function to show the values related to an event */
export function expand_values(dom_id, event_uuid){
    
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
        query.request_info("/eboa_nav/query-jsonify-event-values/" + event_uuid, show_event_values, parameters);
        tr.addClass('shown');
        tdi.first().removeClass('fa-plus-square');
        tdi.first().removeClass('green');
        tdi.first().addClass('fa-minus-square');
        tdi.first().addClass('red');
    }
};

/* Function to show the values related to an event in a tooltip */
export function expand_values_in_tooltip(dom_id, event_uuid){

    var tr = document.getElementById(dom_id);
    // Structure is /div/div/table/tbody/tr
    var container_div = tr.parentNode.parentNode.parentNode.parentNode;
    var tdi = tr.getElementsByTagName("i")[0];

    var expanded_div = container_div.querySelector("#expanded_values")
    if (tr.classList.contains("expanded")) {
        // This tr is already open - close it
        expanded_div.style.display = 'none';
        tr.classList.remove('expanded');
        tdi.classList.remove('fa-minus-square');
        tdi.classList.remove('red');
        tdi.classList.add('fa-plus-square');
        tdi.classList.add('green');
    }
    else if (expanded_div == undefined){
        // Create the expanded tr
        const expanded_div = document.createElement("div");
        expanded_div.id = "expanded_values"        
        container_div.appendChild(expanded_div);
        var parameters = {
            "row": expanded_div,
            "insert_method": insert_in_html_table
        }
        query.request_info("/eboa_nav/query-jsonify-event-values/" + event_uuid, show_event_values, parameters);
        tr.classList.add('expanded');
        tdi.classList.remove('fa-plus-square');
        tdi.classList.remove('green');
        tdi.classList.add('fa-minus-square');
        tdi.classList.add('red');
    }
    else {
        // Open this tr
        tr.classList.add('expanded');
        tdi.classList.remove('fa-plus-square');
        tdi.classList.remove('green');
        tdi.classList.add('fa-minus-square');
        tdi.classList.add('red');
        expanded_div.style.display = 'block';        
    }
};

function show_event_values(parameters, values){

    var row = parameters["row"]

    var table = '<table class="table">' +
        '<thead>' +
        '<tr>' +
        '<th>Type</th>' +
        '<th>Name</th>' +
        '<th>Value</th>' +
        '<th>Position</th>' +
        '<th>Parent level</th>' +
        '<th>Parent position</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody>';

    for (const value of values){
        table = table + 
            '<tr>' +
            '<td>' + value["type"] + '</td>' +
            '<td>' + value["name"] + '</td>' +
            '<td>' + value["value"] + '</td>' +
            '<td>' + value["position"] + '</td>' +
            '<td>' + value["parent_level"] + '</td>' +
            '<td>' + value["parent_position"] + '</td>' +
            '</tr>'
    }
    table = table + '</tbody>' +
        '</table>';

    parameters["insert_method"](row, table);
    
}

function insert_in_datatable(row, table){
    row.child(table).show();
}

function insert_in_html_table(row, table){
    row.innerHTML = table;
}
