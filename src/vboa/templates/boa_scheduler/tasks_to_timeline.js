
var tasks = [
    {% for task in tasks %}
    {% if task["triggering_time"] >= task["stop_coverage"] %}
    {% set start_triggering_to_coverage = task["stop_coverage"] %}
    {% set stop_triggering_to_coverage = task["triggering_time"] %}    
    {% else %}
    {% set start_triggering_to_coverage = task["triggering_time"] %}
    {% set stop_triggering_to_coverage = task["stop_coverage"] %}
    {% endif %}
    {
        "id": "{{ task['task_uuid'] }}" + "_" + "{{ task['triggering_time'] }}" + "_1",
        "group": "{{ task['rule_name'] }}",
        "timeline": "{{ task['name'] }}",
        "start": "{{ start_triggering_to_coverage }}",
        "stop": "{{ stop_triggering_to_coverage }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Rule name</td><td>{{ task['rule_name'] }}</td></tr>" +
            "<tr><td>Task name</td><td>{{ task['task_name'] }}</td></tr>" +
            "<tr><td>Command</td><td>{{ task['command'].replace('\"','\'') }}</td></tr>" +
            "<tr><td>Triggering time</td><td>{{ task['triggering_time'] }}</td></tr>" +
            "<tr><td>Start coverage</td><td>{{ task['start_coverage'] }}</td></tr>" +
            "<tr><td>Stop coverage</td><td>{{ task['stop_coverage'] }}</td></tr>" +                        
            "<tr><td>Periodicity</td><td>{{ task['periodicity'] }}</td></tr>" +
            "<tr><td>Window size</td><td>{{ task['window_size'] }}</td></tr>" +
            "<tr><td>Window delay</td><td>{{ task['window_delay'] }}</td></tr>" +                        
            "</table>",
        "className": "background-yellow"
    },
    {
        "id": "{{ task['task_uuid'] }}" + "_" + "{{ task['triggering_time'] }}" + "_2",
        "group": "{{ task['rule_name'] }}",
        "timeline": "{{ task['name'] }}",
        "start": "{{ task['start_coverage'] }}",
        "stop": "{{ task['stop_coverage'] }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Rule name</td><td>{{ task['rule_name'] }}</td></tr>" +
            "<tr><td>Task name</td><td>{{ task['task_name'] }}</td></tr>" +
            "<tr><td>Command</td><td>{{ task['command'].replace('\"','\'') }}</td></tr>" +
            "<tr><td>Triggering time</td><td>{{ task['triggering_time'] }}</td></tr>" +
            "<tr><td>Start coverage</td><td>{{ task['start_coverage'] }}</td></tr>" +
            "<tr><td>Stop coverage</td><td>{{ task['stop_coverage'] }}</td></tr>" +                        
            "<tr><td>Periodicity</td><td>{{ task['periodicity'] }}</td></tr>" +
            "<tr><td>Window size</td><td>{{ task['window_size'] }}</td></tr>" +
            "<tr><td>Window delay</td><td>{{ task['window_delay'] }}</td></tr>" +                        
            "</table>",
        "className": "background-green"
    },
    {% endfor %}
]
