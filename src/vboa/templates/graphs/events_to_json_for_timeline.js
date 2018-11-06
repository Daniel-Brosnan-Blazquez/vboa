var events = {
    "events": [
        {% for event in events %}
        {
            "id": "{{ event.event_uuid }}",
            "gauge":{
                "name": "{{ event.gauge.name }}",
                "system": "{{ event.gauge.system }}"
            },
            "start": "{{ event.start }}",
            "stop": "{{ event.stop }}"
        },
        {% endfor %}
    ]
}
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
        tooltip: "<table border='1'>" +
            "<tr><td>Event UUID</td><td>" + event["id"] + "</td>" +
            "<tr><td>Start</td><td>" + event["start"] + "</td>" +
            "<tr><td>Stop</td><td>" + event["stop"] + "</td>" +
            "</tr></table>"
    })
}
