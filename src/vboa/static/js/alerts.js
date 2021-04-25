import * as graph from "./graph.js";

/*
* Functions for the general view of alerts
*/

/* Function to create the text for the tooltip of the alert information */
function create_alert_tooltip_text(alert){
    
    return "<table border='1'>" +
        "<tr><td>Name</td><td>" + alert["name"] + "</td></tr>" +
        "<tr><td>Group</td><td>" + alert["group_alert"] + "</td></tr>" +
        "<tr><td>Severity</td><td><span class=" + alert["severity"] + "-severity>" + alert["severity"] + "</span></td></tr>" +
        "<tr><td>Description</td><td>" + alert["description"] + "</td></tr>" +
        "<tr><td>Message</td><td>" + alert['message'] + "</td></tr>" +
        "<tr><td>Validated</td><td>" + alert['validated'] + "</td></tr>" +
        "<tr><td>Ingestion time</td><td>" + alert['ingestion_time'] + "</td></tr>" +
        "<tr><td>Generator</td><td>" + alert['generator'] + "</td></tr>" +
        "<tr><td>Notified</td><td>" + alert['notified'] + "</td></tr>" +
        "<tr><td>Solved</td><td>" + alert['solved'] + "</td></tr>" +
        "<tr><td>Solved time</td><td>" + alert['solved_time'] + "</td></tr>" +
        "<tr><td>Notification time</td><td>" + alert['notification_time'] + "</td></tr>" +
        "<tr><td>Justification</td><td>" + alert['justification'] + "</td></tr>" +
        "<tr><td>Alert UUID</td><td>" + alert['alert_uuid'] + "</td></tr>" +
        "<tr><td>" + alert["entity"] + " UUID</td><td>" + alert["entity_uuid"] + "</td></tr>" +
        "</table>"

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

/* Function to prepare data from alerts for a timeline given the alerts to be displayed */
export function create_alert_timeline(alerts, dom_id){

    var groups = [];
    var items = [];

    // Groups should be only defined by group. alert["timeline"] is mantained for backwards compatibility. 
    var alert_groups = new Set(alerts.map(alert => alert["group"] + ";" + alert["timeline"]));

    // Obtain the nested timeline groups
    var timeline_groups = {};
    var alert_groups_array = Array.from(alert_groups);
    prepare_timeline_groups(alert_groups_array, timeline_groups);

    // Populate groups for the timeline with nested logic
    populate_timeline_groups(timeline_groups, groups, 1);

    // Populate items (be aware that alert["timeline"] is mantained for backwards compatibility.)
    for (const alert of alerts){
        var item = {
            id: alert["id"],
            group: alert["group"] + ";" + alert["timeline"],
            content: alert["content"],
            start: alert["start"],
            end: alert["stop"],
            tooltip: create_alert_tooltip_text(alert)
        }

        items.push(item)
    }

    graph.display_timeline(dom_id, items, groups);
};