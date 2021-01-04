import * as graph from "./graph.js";

/*
* Functions for the general view of alerts
*/

/* Function to create the text for the tooltip of the alert information */
function create_alert_tooltip_text(alert){
 
    return "<table border='1'>" +
        "<tr><td>UUID</td><td>" + alert['id'] + "</td></tr>" +
        "<tr><td>Name</td><td>" + alert["name"] + "</td></tr>" +
        "<tr><td>Severity</td><td>" + alert["severity"] + "</td></tr>" +
        "<tr><td>Description</td><td>" + alert["description"] + "</td></tr>" +
        "<tr><td>Message</td><td>" + alert['message'] + "</td></tr>" +
        "<tr><td>Notification time</td><td>" + alert['notification_time'] + "</td></tr>" +
        "<tr><td>" + alert["entity"][0] + alert["entity"].slice(1).toLowerCase() + " UUID</td><td>" + alert["group_uuid"] + "</td></tr>" +
        "<tr><td>Group</td><td>" + alert["group"] + "</td></tr>" +
        "<tr><td>Entity</td><td>" + alert["entity"] + "</td></tr>" +
        "</table>"
};

/* Function to create a timeline graph for the general view of alerts view */
export function create_alert_timeline(alerts, dom_id){
    var groups = [];
    var items = [];

    var entity_types = new Set(alerts.map(alert => alert["entity"]))

    for (const entity_type of entity_types){
        var associated_entities = new Set(alerts.filter(alert => alert["entity"] == entity_type).map(alert => alert["entity"] + "_" + alert["group"] + "_" + alert["name"]))
        
        for (const associated_entity of associated_entities){
            groups.push({
                id: associated_entity,
                treeLevel: 1,
                content: associated_entity
            })
        }
    }

    var unique_alert_uuids = new Set(alerts.map(alert => alert["id"]));

    for (const alert_uuid of unique_alert_uuids){
        var alert = alerts.filter(alert => alert["id"] == alert_uuid)[0]
        var group = alert["entity"] + "_" + alert["group"] + "_" + alert["name"]
       
        items.push({
            id: alert["id"],
            group: group,
            start: alert["notification_time"],
            end: alert["notification_time"],
            tooltip: create_alert_tooltip_text(alert)
        })
        console.log(items);
    }

    graph.display_timeline(dom_id, items, groups);

};