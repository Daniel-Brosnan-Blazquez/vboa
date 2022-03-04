import * as vis_data from "vis-data/dist/umd.js";
import { DataSet } from "vis-data/peer/esm/vis-data"
import * as vis_network from "vis-network/peer/umd/vis-network.min.js";
import * as vis_timeline_graph2d from "vis-timeline/peer/umd/vis-timeline-graph2d.js";
import * as chartjs from "chart.js/dist/Chart.js";
import olMap from 'ol/Map.js';
import olView from 'ol/View.js';
import WKT from 'ol/format/WKT.js';
import olLayerTile from 'ol/layer/Tile.js';
import olLayerVector from 'ol/layer/Vector.js';
import olSourceOSM from 'ol/source/OSM.js';
import olSourceVector from 'ol/source/Vector.js';
import {fromLonLat} from 'ol/proj';
import MousePosition from 'ol/control/MousePosition.js';
import {createStringXY} from 'ol/coordinate.js';
import {defaults as defaultControls} from 'ol/control.js';
import {Fill, Stroke, Style, Text} from 'ol/style.js';
import OLCesium from 'olcs/OLCesium.js';

/* Function to display a pie chart given the id of the DOM where to
 * attach it and the items to show */
export function display_pie(dom_id, data, options){

    /* create pie */
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
                     fontColor: "white",
                     precision: 2}]
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

    /* create bar */
    const container = document.getElementById(dom_id);
    if (options == undefined){
        const options = {
            style: "bar",
            barChart: {width:50, align:'center', sideBySide:true}
        };
    }

    const bar = new vis_timeline_graph2d.Graph2d(container, items, groups, options);

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
        const x = params["pageX"];
        const y = params["pageY"];

        const div = create_div(dom_id, element_id, header_content, body_content, x, y)
        drag_element(div)
    }
}

/* Function to display a timeline given the id of the DOM where to
 * attach it and the items to show with corresponding groups */
export function display_timeline(dom_id, items, groups, options){

    /* create timeline */
    const container = document.getElementById(dom_id);

    if (options == undefined){
        options = {
            groupOrder: 'content',
            margin: {
                item : {
                    horizontal : 0
                }
            },
        };
    };

    const threshold = 1000
    if (items.length > threshold){
        container.style.display = "none";
        const button_container = document.createElement("div");
        container.parentNode.appendChild(button_container);
        const button = document.createElement("button");
        button.classList.add("btn");
        button.classList.add("btn-primary");
        button.innerHTML = "Number of elements (" + items.length + ") exceeded the threshold (" + threshold + "). Click here to show the timeline graph";
        button_container.appendChild(button);
        button.onclick = function (){
            button.style.display = "none";
            container.style.display = "inherit";
            show_timeline(dom_id, items, container, groups, options);
        };
    }
    else{
        show_timeline(dom_id, items, container, groups, options);
    }
};
function show_timeline(dom_id, items, container, groups, options){

    var groups_dataset = new DataSet(groups)
    var items_dataset = new DataSet(items)
    const timeline = new vis_timeline_graph2d.Timeline(container, items_dataset, groups_dataset, options);

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
        nodes: nodes,
        edges: edges
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

    const threshold = 20
    if (nodes.length > threshold){
        container.style.display = "none";
        const button_container = document.createElement("div");
        container.parentNode.appendChild(button_container);
        const button = document.createElement("button");
        button.classList.add("btn");
        button.classList.add("btn-primary");
        button.innerHTML = "Number of elements (" + nodes.length + ") exceeded the threshold (" + threshold + "). Click here to show the network graph";
        button_container.appendChild(button);
        button.onclick = function (){
            button.style.display = "none";
            container.style.display = "inherit";
            show_network(dom_id, nodes, container, data, options);
        };
    }
    else{
        show_network(dom_id, nodes, container, data, options);
    }
};
function show_network(dom_id, nodes, container, data, options){

    const network = new vis_network.Network(container, data, options);

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
    
    const threshold = 1000
    if (items.length > threshold){
        container.style.display = "none";
        const button_container = document.createElement("div");
        container.parentNode.appendChild(button_container);
        const button = document.createElement("button");
        button.classList.add("btn");
        button.classList.add("btn-primary");
        button.innerHTML = "Number of elements (" + items.length + ") exceeded the threshold (" + threshold + "). Click here to show the timeline graph";
        button_container.appendChild(button);
        button.onclick = function (){
            button.style.display = "none";
            container.style.display = "inherit";
            show_x_time(dom_id, items, container, groups, options);
        };
    }
    else{
        show_x_time(dom_id, items, container, groups, options);
    }
};
function show_x_time(dom_id, items, container, groups, options){

    const x_time = new vis_timeline_graph2d.Graph2d(container, items, groups, options);

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

    /* Raster layer used to display world map */
    var raster = new olLayerTile({
        source: new olSourceOSM()
    });

    /* Format set to WKT (Well Known Text standard) */
    var format = new WKT();

    /* Build features containing polygons */
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
    
    var vector = new olLayerVector({
        source: new olSourceVector({
            features: features
        })
    });

    vector.set('name', 'features');
    
    var mousePositionControl = new MousePosition({
        coordinateFormat: createStringXY(4),
        projection: 'EPSG:4326',
    });

    /* Get the maps container div */
    var maps_container_div = document.getElementById(dom_id);

    /* Create div for maps options */
    const maps_options_div = document.createElement("div");
    maps_options_div.id = dom_id + "-maps-options"
    maps_container_div.appendChild(maps_options_div);
    maps_options_div.style.marginBottom = "10px";
    
    /* Create div including a button to change from 2D to 3D and viceversa */
    const change_2d_3d_div = document.createElement("div");
    change_2d_3d_div.id = dom_id + "-maps-options-change-2d-3d"
    maps_options_div.appendChild(change_2d_3d_div);
    const change_2d_3d_button = document.createElement("button");
    change_2d_3d_button.id = dom_id + "-maps-button-2d-3d"
    change_2d_3d_div.appendChild(change_2d_3d_button);
    change_2d_3d_button.classList.add("btn");
    change_2d_3d_button.classList.add("btn-primary");
    change_2d_3d_button.innerHTML = "3D";
    /* Annotate in data the option to display to the other visualization option (2D/3D) */
    change_2d_3d_button.data = "3D";

    /* Create div for 2D map */
    const map_div = document.createElement("div");
    map_div.id = dom_id + "-map"
    maps_container_div.appendChild(map_div);

    /* Specify height for map_div as newer versions of OpenLayers
     * (since version 6.0.0) do not set this value */
    map_div.style.height = "100vh";

    /* Reset map and add new layers if the map was already available */
    if (map_div.data){
        map = map_div.data;
        map.getLayers().forEach(function (layer) {
            if (layer.get('name') === 'features') {
                map.removeLayer(layer);
            }
        });
        map.addLayer(vector);
    }
    else{
        /* Create 2D map */
        var map = new olMap({
            controls: defaultControls().extend([mousePositionControl]),
            layers: [raster, vector],
            target: map_div.id,
            view: new olView({
                center: [0, 0],
                zoom: 2,
                multiWorld: true
            })
        });
        map_div.data = map;

        /* Create 3D map */
        const ol3d = new OLCesium({map});
        const scene = ol3d.getCesiumScene();
        scene.logarithmicDepthBuffer = false;
        ol3d.setEnabled(false);
        
        /**
         * Add a click handler to the 2D map to render the tooltip.
         */
        map.on('singleclick', function(event) {
            map.updateSize();
            show_map_item_information(event, map, map_div.id)
        });

        /* Add sidepanel-change event handler to resize the map */
        window.addEventListener("sidepanel-change", function() {
            setTimeout(function() {
                map.updateSize();
            }, 1);
        })

        /**
         * Add a click handler to the button to change from 2D to 3D and viceversa.
         */
        change_2d_3d_button.onclick = function(event) {
            const button = event.explicitOriginalTarget;
            ol3d.setEnabled(!ol3d.getEnabled());
            if (button.data == "2D"){
                /* Change to 2D visualization */
                button.data = "3D";
                button.innerHTML = "3D";
            }
            else{
                /* Change to 3D visualization */
                button.data = "2D";
                button.innerHTML = "2D";
            }
        };

    }
}

function show_map_item_information(event, map, dom_id){

    var feature = map.forEachFeatureAtPixel(event.pixel, function(feature) {
        return feature;
    });

    if (typeof feature !== 'undefined') {
        const header_content = "Detailed information for polygon with id: " + feature.getId();
        const body_content = feature.getProperties()["tooltip"]
        const x = event.originalEvent.pageX;
        const y = event.originalEvent.pageY;

        const div = create_div(dom_id, feature.getId(), header_content, body_content, x, y)
        drag_element(div)
    }
}

function create_div(dom_id, element_id, header_content, body_content, x, y){

    const container = document.getElementById("boa-body");

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
