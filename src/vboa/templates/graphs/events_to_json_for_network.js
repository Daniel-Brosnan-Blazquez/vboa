var events = {
    "events": [
        {% for key in events %}
        {% for event in events[key] %}
        {
            "id": "{{ event.event_uuid }}",
            "gauge":{
                "name": "{{ event.gauge.name }}",
                "system": "{{ event.gauge.system }}"
            },
            "start": "{{ event.start }}",
            "stop": "{{ event.stop }}",
            "label": "{{ key }}"
        },
        {% endfor %}
        {% endfor %}
    ]
}

var unique_event_uuids = new Set(events["events"].map(event => event["id"]));
var prime_event_id = events["events"].filter(event => event["id"] == "{{events['prime_events'][0].event_uuid}}").map(event => event["id"])[0];

var nodes = []
var edges = []
for (const id of unique_event_uuids){
    var filtered_events = events["events"].filter(event => event["id"] == id)
    
    var event = filtered_events[0]
    var shape = "box";
    var background_color = "lightblue";
    if (event["label"] == "prime_events"){
        shape = "elipse";
        background_color = "lightgreen";
    }
    else{
        var labels = filtered_events.map(event => event["label"])
        var arrows = "to"
        if (labels.length == 2){
            arrows = "to, from";
        }else if (labels[0] == "events_linking"){
            arrows = "from";
        }
        edges.push({
            "from": prime_event_id,
            "to": event["id"],
            "arrows": arrows
        })
    }
    nodes.push({
        "id": event["id"],
        "color": background_color,
        "shape": shape,
        "label":"Gauge name: " + event['gauge']['name'] + "\nGauge system: " + event['gauge']['system'] + "\nStart: " + event['start'] + "\nStop: " + event['stop'],
        "font": {"align": "left"}
    });
}
