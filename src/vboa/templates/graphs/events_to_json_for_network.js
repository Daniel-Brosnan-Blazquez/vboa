var events = {
    "events": [
        {% for key in links %}
        {% for link in links[key] %}
        {% if key == "prime_events" %}
        {% set event = link %}
        {% set link_name = "" %}
        {% else %}
        {% set event = link["event"] %}
        {% set link_name = link["link_name"] %}
        {% endif %}
        {
            "id": "{{ event.event_uuid }}",
            "gauge":{
                "name": "{{ event.gauge.name }}",
                "system": "{{ event.gauge.system }}"
            },
            "start": "{{ event.start }}",
            "stop": "{{ event.stop }}",
            "label": "{{ key }}",
            "link_name": "{{ link_name }}",
            "source": "{{ event.source.name }}"
        },
        {% endfor %}
        {% endfor %}
    ]
}

var unique_event_uuids = new Set(events["events"].map(event => event["id"]));
var prime_event_id = events["events"].filter(event => event["id"] == "{{links['prime_events'][0].event_uuid}}").map(event => event["id"])[0];

var nodes = []
var edges = []
for (const id of unique_event_uuids){
    var associated_events = events["events"].filter(event => event["id"] == id)

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
        "tooltip":"<table border='1'>" +
            "<tr><td>UUID</td><td>" + associated_events[0]['id'] + "</td>" +
            "<tr><td>Gauge name</td><td>" + associated_events[0]['gauge']['name'] + "</td>" +
            "<tr><td>Gauge system</td><td>" + associated_events[0]['gauge']['system'] + "</td>" +
            "<tr><td>Start</td><td>" + associated_events[0]["start"] + "</td>" +
            "<tr><td>Stop</td><td>" + associated_events[0]["stop"] + "</td>" +
            "<tr><td>Source</td><td>" + associated_events[0]['source'] + "</td>" +
            "</tr></table>",
        "label": "Gauge name: " + associated_events[0]['gauge']['name'] + "\nGauge system: " + associated_events[0]['gauge']['system'] + "\nStart: " + associated_events[0]['start'] + "\nStop: " + associated_events[0]['stop'],
        "font": {"align": "left"}
    });
}
