import * as vis from "vis/dist/vis.min.js";
import * as chartjs from "chart.js/dist/Chart.js";
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import WKT from 'ol/format/WKT.js';
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer.js';
import {OSM, Vector as VectorSource} from 'ol/source.js';
import {fromLonLat} from 'ol/proj';
import MousePosition from 'ol/control/MousePosition.js';
import {createStringXY} from 'ol/coordinate.js';
import {defaults as defaultControls} from 'ol/control.js';
import {Fill, Stroke, Style, Text} from 'ol/style.js';


/* Function to display a pie chart given the id of the DOM where to
 * attach it and the items to show */
export function display_pie(dom_id, data, options){

    /* create timeline */
    var container = document.getElementById(dom_id);

    if (options == undefined){
        var options = {
            responsive: true,
            maintainAspectRatio: true,
            legend: {
                display: false
            },
            plugins: {
                labels: [
                    {render: 'label',
                     position: 'outside',
                     fontSize: 14,
                     fontStyle: "bold",
                     fontColor: "black"},
                    {render: 'percentage',
                     fontSize: 14,
                     fontStyle: "bold",
                     fontColor: "white"}]
            }
        }
    }
    
    if (options == undefined){    
        var pie_chart = new chartjs.Chart(container, {
            type: 'pie',
            data: data
        });
    }else{
        var pie_chart = new chartjs.Chart(container, {
            type: 'pie',
            data: data,
            options: options
        });
    }

};

/* Function to display a bar chart given the id of the DOM where to
 * attach it and the items to show with corresponding groups */
export function display_bar_time(dom_id, items, groups, options){

    /* create timeline */
    const container = document.getElementById(dom_id);
    if (options == undefined){
        const options = {
            style: "bar",
            barChart: {width:50, align:'center', sideBySide:true},
        };
    }
    
    const bar = new vis.Graph2d(container, new vis.DataSet(items), new vis.DataSet(groups), options);

    bar.on("click", function (params) {
        show_bar_item_information(params, items, dom_id)
    });

};

function show_bar_item_information(params, items, dom_id){

    const time_margin = 5;

    var left_time = new Date(params["time"]);
    left_time.setSeconds(left_time.getSeconds() - time_margin);
    var right_time = new Date(params["time"])
    right_time.setSeconds(right_time.getSeconds() + time_margin);
    const y = params["value"][0]
    const matched_items = items.filter(item => new Date(item["x"]) >= left_time && new Date(item["x"]) <= right_time)
    for (const matched_item of matched_items){
        const element_id = matched_item["id"]
        const header_content = "Detailed information for the BAR element: " + element_id;
        const item = items.filter(item => item["id"] == element_id)[0]
        const body_content = item["tooltip"];
        const x = params["x"];
        const y = params["y"];
        const div = create_div(dom_id, element_id, header_content, body_content, x, y)
        drag_element(div)
    }
}

/* Function to display a timeline given the id of the DOM where to
 * attach it and the items to show with corresponding groups */
export function display_timeline(dom_id, items, groups){

    /* create timeline */
    const container = document.getElementById(dom_id);

    const options = {
        groupOrder: 'content',
        margin: {
            item : {
                horizontal : -1
            }
        }
    };
    
    const timeline = new vis.Timeline(container, new vis.DataSet(items), new vis.DataSet(groups), options);

    timeline.on("click", function (params) {
        show_timeline_item_information(params, items, dom_id)
    });

};

function show_timeline_item_information(params, items, dom_id){

    const element_id = params["item"]
    if (element_id != undefined){
        const header_content = "Detailed information for the timeline element: " + element_id;
        const item = items.filter(item => item["id"] == element_id)[0]
        const body_content = item["tooltip"];
        const x = params["pageX"];
        const y = params["pageY"];

        const div = create_div(dom_id, element_id, header_content, body_content, x, y)
        drag_element(div)
    }
}

/* Function to display a network given the id of the DOM where to
 * attach it and the nodes to show with the corresponding relations */
export function display_network(dom_id, nodes, edges, options){

    /* create timeline */
    const container = document.getElementById(dom_id);

    const data = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
    };
    
    if (options == undefined){
        options = {
            physics: {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -250000
                }
            },
            interaction:{hover:true}
        };
    }
    const network = new vis.Network(container, data, options);

    network.on("click", function (params) {
        show_network_node_information(params, nodes, dom_id)
    });

};

function show_network_node_information(params, nodes, dom_id){

    const element_id = params["nodes"][0];
    if (element_id != undefined && nodes.length > 0){
        const header_content = "Detailed information for the network element: " + element_id;
        const node = nodes.filter(node => node["id"] == element_id)[0]
        const body_content = node["tooltip"];
        const x = params["event"]["center"]["x"] + pageXOffset;
        const y = params["event"]["center"]["y"] + pageYOffset;

        const div = create_div(dom_id, element_id, header_content, body_content, x, y);
        drag_element(div);
    }
}

/* Function to display an X-Time graph given the id of the DOM where to
 * attach it and the items to show with the corresponding groups */
export function display_x_time(dom_id, items, groups, options){

    /* create timeline */
    const container = document.getElementById(dom_id);
    
    if (options == undefined){
        options = {
            legend: true
        };
    }
    
    const x_time = new vis.Graph2d(container, new vis.DataSet(items), new vis.DataSet(groups), options);

    x_time.on("click", function (params) {
        show_x_time_item_information(params, items, dom_id)
    });

};

function show_x_time_item_information(params, items, dom_id){

    const time_margin = 5;

    var left_time = new Date(params["time"]);
    left_time.setSeconds(left_time.getSeconds() - time_margin);
    var right_time = new Date(params["time"])
    right_time.setSeconds(right_time.getSeconds() + time_margin);
    const y = params["value"][0]
    const matched_items = items.filter(item => new Date(item["x"]) >= left_time && new Date(item["x"]) <= right_time)
    for (const matched_item of matched_items){
        const element_id = matched_item["id"]
        const header_content = "Detailed information for the X-Time element: " + element_id;
        const item = items.filter(item => item["id"] == element_id)[0]
        const body_content = item["tooltip"];
        const x = params["pageX"];
        const y = params["pageY"];

        const div = create_div(dom_id, element_id, header_content, body_content, x, y)
        drag_element(div)
    }
}

/* Function to display a map given the id of the DOM where to
 * attach it and the polygons to show */
export function display_map(dom_id, polygons){

    var raster = new TileLayer({
        source: new OSM()
    });

    var format = new WKT();
    
    var features = []
    for (const polygon of polygons){
        var feature = format.readFeature(polygon["polygon"], {
            dataProjection: 'EPSG:4326',
            featureProjection: 'EPSG:3857'
        });
        feature.setId(polygon["id"])
        feature.setProperties({"tooltip": polygon["tooltip"]})
        if ("style" in polygon){
            var stroke_color = "blue"
            if ("stroke_color" in polygon["style"]){
                stroke_color = polygon["style"]["stroke_color"];
            }
            var stroke_width = 1
            if ("stroke_width" in polygon["style"]){
                stroke_width = polygon["style"]["stroke_width"];
            }
            var fill_color = "rgba(0, 0, 255, 0.1)"
            if ("fill_color" in polygon["style"]){
                fill_color = polygon["style"]["fill_color"];
            }
            var text = ""
            if ("text" in polygon["style"]){
                text = polygon["style"]["text"];
            }
            var font_text = ""
            if ("font_text" in polygon["style"]){
                font_text = polygon["style"]["font_text"];
            }
            var style = new Style({
                stroke: new Stroke({
                    color: stroke_color,
                    width: stroke_width
                }),
                fill: new Fill({
                    color: fill_color
                }),
                text: new Text({
                    text: text,
                    font: font_text
                })
            });
            feature.setStyle(style);
        }
        features.push(feature);
    }
    
    var vector = new VectorLayer({
        source: new VectorSource({
            features: features
        })
    });

    vector.set('name', 'features');
    
    var mousePositionControl = new MousePosition({
        coordinateFormat: createStringXY(4),
        projection: 'EPSG:4326',
    });

    if (document.getElementById(dom_id).data){
        map = document.getElementById(dom_id).data;
        map.getLayers().forEach(function (layer) {
            if (layer.get('name') === 'features') {
                map.removeLayer(layer);
            }
        });
        map.addLayer(vector);
    }
    else{
        var map = new Map({
            controls: defaultControls().extend([mousePositionControl]),
            layers: [raster, vector],
            target: dom_id,
            view: new View({
                center: [0, 0],
                zoom: 2
            })
        });
        document.getElementById(dom_id).data = map;
    
        /**
         * Add a click handler to the map to render the tooltip.
         */
        map.on('singleclick', function(event) {
            show_map_item_information(event, map, dom_id)
        });
    }
}

function show_map_item_information(event, map, dom_id){

    var feature = map.forEachFeatureAtPixel(event.pixel, function(feature) {
        return feature;
    });

    const header_content = "Detailed information for polygon with id: " + feature.getId();
    const body_content = feature.getProperties()["tooltip"]
    const x = event.originalEvent.pageX;
    const y = event.originalEvent.pageY;

    const div = create_div(dom_id, feature.getId(), header_content, body_content, x, y)
    drag_element(div)

}

function create_div(dom_id, element_id, header_content, body_content, x, y){

    const container = document.getElementById(dom_id);

    // Create div
    const div = document.createElement("div");
    div.id = dom_id + "_" + element_id
    container.appendChild(div);
    // Add class to the div
    div.classList.add("draggable-div");
    div.style.top = y + "px";
    div.style.left = x + "px";

    // Create header for the div
    const div_header = document.createElement("div");
    const div_header_text = document.createElement("div");
    div_header_text.innerHTML = header_content;
    div_header.id = "header"
    div.appendChild(div_header);
    div_header.appendChild(div_header_text);
    // Add class to the div
    div_header_text.classList.add("draggable-div-header-text");

    // Add close icon
    const div_header_close = document.createElement("div");
    div_header.appendChild(div_header_close);
    const span_close = document.createElement("span");
    div_header_close.appendChild(span_close);
    span_close.classList.add("fa");
    span_close.classList.add("fa-times");
    div_header_close.classList.add("draggable-div-close");
    div_header_close.onclick = function(){
        div.parentNode.removeChild(div);
    };

    // Create body for the div
    const div_body = document.createElement("div");
    div.appendChild(div_body);
    div_body.innerHTML = body_content;
    div_body.id = "body"
    div_body.classList.add("draggable-div-body");

    return div;

}

function drag_element(element) {

    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    // The element is draggable only using the header
    element.querySelector("#header").onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    }
}
