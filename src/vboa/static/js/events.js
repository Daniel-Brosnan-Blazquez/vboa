import * as query from "./query.js";
import * as dates from "./dates.js";
import * as graph from "./graph.js";

/* Function to create the text for the tooltip of the event information */
function create_event_tooltip_text(event){

    return "<table border='1'>" +
            "<tr><td>UUID</td><td>" + event['id'] + "</td>" +
            "<tr><td>Gauge name</td><td>" + event['gauge']['name'] + "</td>" +
            "<tr><td>Gauge system</td><td>" + event['gauge']['system'] + "</td>" +
            "<tr><td>Start</td><td>" + event["start"] + "</td>" +
            "<tr><td>Stop</td><td>" + event["stop"] + "</td>" +
            "<tr><td>Source</td><td>" + event['source'] + "</td>" +
            "</tr></table>"
};

export function create_event_network(linked_events, dom_id){
    var unique_event_uuids = new Set(linked_events["events"].map(event => event["id"]));
    var prime_event_id = linked_events["events"].filter(event => event["label"] == "prime_events").map(event => event["id"])[0];

    var nodes = []
    var edges = []
    for (const id of unique_event_uuids){
        var associated_events = linked_events["events"].filter(event => event["id"] == id)

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

export function create_event_timeline(events, dom_id){
    var groups = [];
    var items = [];

    var gauge_systems = new Set(events["events"].map(event => event["gauge"]["system"]))

    for (const gauge_system of gauge_systems){
        var associated_gauges = new Set(events["events"].filter(event => event["gauge"]["system"] == gauge_system).map(event => event["gauge"]["name"] + "_" + event["gauge"]["system"]))
        groups.push({
            id: gauge_system,
            content: gauge_system,
            nestedGroups: Array.from(associated_gauges)
        })
        for (const associated_gauge of associated_gauges){
            groups.push({
                id: associated_gauge,
                content: associated_gauge
            })
        }
    }

    var unique_event_uuids = new Set(events["events"].map(event => event["id"]));

    for (const event_uuid of unique_event_uuids){
        var event = events["events"].filter(event => event["id"] == event_uuid)[0]
        items.push({
            id: event["id"],
            group: event["gauge"]["name"] + "_" + event["gauge"]["system"],
            start: event["start"],
            end: event["stop"],
            tooltip: create_event_tooltip_text(event)
        })
    }

    graph.display_timeline(dom_id, items, groups);

};

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
        query.request_info("/eboa_nav/query-jsonify-event-values/" + event_uuid, show_event_values, row);
        tr.addClass('shown');
        tdi.first().removeClass('fa-plus-square');
        tdi.first().removeClass('green');
        tdi.first().addClass('fa-minus-square');
        tdi.first().addClass('red');
    }
};

function show_event_values(row, values){

    var table = '<table class="table">' +
        '<thead>' +
        '<tr>' +
        '<th>Type</th>' +
        '<th>Name</th>' +
        '<th>Value</th>' +
        '<th>Level position</th>' +
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
            '<td>' + value["level_position"] + '</td>' +
            '<td>' + value["parent_level"] + '</td>' +
            '<td>' + value["parent_position"] + '</td>' +
            '</tr>'
    }
    table = table + '</tbody>' +
        '</table>';
    
    row.child(table).show();

    return
}
