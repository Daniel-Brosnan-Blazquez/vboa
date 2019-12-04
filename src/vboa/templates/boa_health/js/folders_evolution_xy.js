
var events = [
    {% for event in events %}
    {% set folders = event.eventTexts|selectattr("name", "equalto", "folder_name")|map(attribute="value")|list %}
    {% for folder in folders %}
    {% set number_of_files = event.eventDoubles|selectattr("name", "equalto", folder + "_number_of_files")|first|attr("value") %}
    {
        "id": "{{ event.event_uuid }}-{{ folder }}-number-of-files",
        "group": "{{ folder }}",
        "x": "{{ event.start.isoformat() }}",
        "y": "{{ number_of_files }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Group</td><td>{{ folder }}</td></tr>" +
            "<tr><td>Notification time</td><td>{{ event.start.isoformat() }}</td></tr>" +
            "<tr><td>Value</td><td>{{ number_of_files }}</td></tr>" +
            '<tr><td>Details</td><td><a href="/eboa_nav/query-event-links/{{ event.event_uuid }}">{{ event.event_uuid }}"></a></td></tr>' +
            "</table>"
    },
    {% endfor %}
    {% endfor %}
]
