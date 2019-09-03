/* js */
import "bootstrap/dist/js/bootstrap.min.js";
import "bootstrap-datetime-picker/js/bootstrap-datetimepicker.min.js";
import "bootstrap-responsive-tabs/dist/js/jquery.bootstrap-responsive-tabs.min.js";
import "datatables/media/js/jquery.dataTables.min.js";
import "datatables.net/js/jquery.dataTables.min.js";
import "datatables.net-buttons/js/dataTables.buttons.min.js";
import "datatables.net-buttons/js/buttons.html5.min.js";
import "datatables.net-select/js/dataTables.select.js";
import "jszip/dist/jszip.min.js";
import "chosen-js/chosen.jquery.min.js";
import "metismenu/dist/metisMenu.min.js";
import * as toastr from "toastr/toastr.js";
import * as olMap from "ol/Map.js";
import * as olView from "ol/View.js";
import * as vis from "vis/dist/vis.js";
import * as graph from "./graph.js";
import * as sourceFunctions from "./sources.js";
import * as gaugeFunctions from "./gauges.js";
import * as annotationCnfsFunctions from "./annotation_confs.js";
import * as eventFunctions from "./events.js";
import * as annotationFunctions from "./annotations.js";
import * as eventKeyFunctions from "./event_keys.js";
import * as dimSignatureFunctions from "./dim_signatures.js";
import * as erFunctions from "./explicit_references.js";
import * as queryFunctions from "./query.js";
import * as dates from "./dates.js";
import * as datatableFunctions from "./datatables.js";

/* css */
import "bootstrap-datetime-picker/css/bootstrap-datetimepicker.min.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-social/bootstrap-social.css";
import "font-awesome/css/font-awesome.min.css";
import "bootstrap-responsive-tabs/dist/css/bootstrap-responsive-tabs.css";
import "datatables/media/css/jquery.dataTables.min.css";
import "vis/dist/vis.css";
import "vis/dist/vis-timeline-graph2d.min.css";
import "vis/dist/vis-network.min.css";
import "chosen-js/chosen.min.css";
import "ol/ol.css";
import "metismenu/dist/metisMenu.min.css";
import "toastr/build/toastr.min.css";

setInterval(update_clock, 1000);

/* Set clock */
function update_clock() {
    var date = new Date();
    var local_date = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
    document.getElementById("time-clock").innerHTML = "<div class='nav navbar-text'>" +
        "<p style='background:white'>UTC time: " + date.toISOString().split('.')[0] + " - Local time: " + local_date.toISOString().split('.')[0] + "</p>" +
        "</div>"
};

/* Activate chosen for the multiple input selection */
jQuery(".chosen-select").chosen({
    no_results_text: "Nothing found for the following criteria: ",
    width: "100%"
});

/* Manage side menu */
$(function() {
    $('#side-menu').metisMenu();
});

/* Toasts configuration */
toastr.options.progressBar = true; // Show how long it takes before it expires
toastr.options.timeOut = 10000; // How long the toast will display without user interaction (milliseconds)
toastr.options.extendedTimeOut = 10000; // How long the toast will display after a user hovers over it (milliseconds)

/* Update view */
export function update_view(parameters, repeat_cycle, view){
    setTimeout(function(){
        var href = view + "?"
        for (const parameter of Object.keys(parameters)){
                href = href + parameter + "=" + parameters[parameter] + "&";
        }
        href = href + "repeat_cycle=" + repeat_cycle;
        window.location.href = href;
    }, repeat_cycle * 60 * 1000);
}

/* Functions to add more time filters (start-stop, validity start-validity stop, ingestion time, generation time) */
export function add_start_stop(dom_id){
    dates.add_start_stop(dom_id);
}

export function add_validity_start_validity_stop(dom_id){
    dates.add_validity_start_validity_stop(dom_id);
}

export function add_ingestion_time(dom_id){
    dates.add_ingestion_time(dom_id);
}

export function add_ingestion_duration(dom_id){
    dates.add_ingestion_duration(dom_id);
}

export function add_generation_time(dom_id){
    dates.add_generation_time(dom_id);
}

export function add_event_duration(dom_id){
    dates.add_event_duration(dom_id);
}

export function add_source_validity_duration(dom_id){
    dates.add_source_validity_duration(dom_id);
}

/* Functions to add more filters by values for events and annotations */
export function add_value_query_events(dom_id){
    eventFunctions.add_value_query(dom_id);
}

export function add_value_query_annotations(dom_id){
    annotationFunctions.add_value_query(dom_id);
}

/* Functions to expand the values associated to events and annotations */
export function expand_event_values(dom_id, event_uuid){
    eventFunctions.expand_values(dom_id, event_uuid);
}

export function expand_event_values_in_tooltip(dom_id, event_uuid){
    eventFunctions.expand_values_in_tooltip(dom_id, event_uuid);
}

export function expand_annotation_values(dom_id, annotation_uuid){
    annotationFunctions.expand_values(dom_id, annotation_uuid);
}

/* Function to expand the sources associated to a source */
export function expand_source_statuses(dom_id, source_uuid){
    sourceFunctions.expand_source_statuses(dom_id, source_uuid);
}

/* Associate datetimepicker functionality */
jQuery(function () {
    dates.activate_datetimepicker();
});

jQuery(".responsive-tabs").responsiveTabs({
  accordionOn: ['xs', 'sm'] // xs, sm, md, lg
});

/* 
* Datatables
*/
/* Activate search on every column for datatables */
jQuery(function() {
    datatableFunctions.activate_search_on_columns();
});

/* Functions to fill lists of inputs */
/* Functions to be called just once to fill the options with values from the database */

/* Fill sources */

jQuery(".query-sources").one("focusin", sourceFunctions.fill_sources);

/* Fill processing statuses */
jQuery(".query-source-statuses").one("focusin", sourceFunctions.fill_statuses);

/* Fill gauges */
jQuery(".query-gauges").one("focusin", gaugeFunctions.fill_gauges);

/* Fill annotation configurations */
jQuery(".query-annotation-cnfs").one("focusin", annotationCnfsFunctions.fill_annotation_cnfs);

/* Fill explicit references */
jQuery(".query-ers").one("focusin", erFunctions.fill_ers);

/* Fill explicit reference groups */
jQuery(".query-er-groups").one("focusin", erFunctions.fill_er_groups);

/* Fill event keys */
jQuery(".query-keys").one("focusin", eventKeyFunctions.fill_keys);

/* Fill DIM signatures */
jQuery(".query-dim-signatures").one("focusin", dimSignatureFunctions.fill_dim_signatures);

/*
* Graph functions
*/
/* Function to display a timeline given the id of the DOM where to
 * attach it and the items to show with corresponding groups */
export function display_timeline(dom_id, items, groups){

    graph.display_timeline(dom_id, items, groups);

};

/* Function to display a network given the id of the DOM where to
 * attach it and the nodes to show with the corresponding relations */
export function display_network(dom_id, nodes, edges){

    graph.display_network(dom_id, nodes, edges);

};

/* Function to display an X-Time graph given the id of the DOM where to
 * attach it and the items to show with the corresponding groups */
export function display_x_time(dom_id, items, groups, options){

    graph.display_x_time(dom_id, items, groups, options);

};

/* Function to display a map graph given the id of the DOM where to
 * attach it and the items to show with the corresponding groups */
export function display_map(dom_id, polygons){

    graph.display_map(dom_id, polygons);

};

/*
* EVENTS *
*/

/* Function to show a timeline of events */
export function prepare_events_data_for_timeline(events, items, groups){

    eventFunctions.prepare_events_data_for_timeline(events, items, groups);

};
/* Function to show a X_time of events */
export function prepare_events_data_for_xy(events, items, groups, title){

    var options = eventFunctions.prepare_events_data_for_xy(events, items, groups, title);

    return options;
};
/* Function to show a map of events */
export function prepare_events_geometries_for_map(events_geometries, polygons){

    eventFunctions.prepare_events_geometries_for_map(events_geometries, polygons);

};

/* Function to show a timeline of events */
export function create_event_timeline(events, dom_id){

    eventFunctions.create_event_timeline(events, dom_id);

};

/* Function to show a network of events */
export function create_event_network(events, dom_id){

    eventFunctions.create_event_network(events, dom_id);

};

/* Function to show a map for events */
export function create_event_map(geometries, dom_id){

    eventFunctions.create_event_map(geometries, dom_id);

};

/*
* ANNOTATIONS *
*/

/* Function to show a map for annotations */
export function create_annotation_map(geometries, dom_id){

    annotationFunctions.create_annotation_map(geometries, dom_id);

};

/*
* GAUGES *
*/

/* Function to show a network of gauges */
export function create_gauge_network(gauges, dom_id){

    gaugeFunctions.create_gauge_network(gauges, dom_id);

};

/*
* SOURCES *
*/

/* Function to show a timeline of validities for the sources */
export function create_source_validity_timeline(sources, dom_id){

    sourceFunctions.create_source_validity_timeline(sources, dom_id);

};

/* Function to show a timeline of validities for the sources */
export function create_source_generation_to_ingestion_timeline(sources, dom_id){

    sourceFunctions.create_source_generation_to_ingestion_timeline(sources, dom_id);

};

/* Function to show an X-time graph with the number of events per source */
export function create_source_number_events_xy(sources, dom_id){

    sourceFunctions.create_source_number_events_xy(sources, dom_id);

};

/* Function to show an X-time graph with the ingestion duration per source */
export function create_source_ingestion_duration_xy(sources, dom_id){

    sourceFunctions.create_source_ingestion_duration_xy(sources, dom_id);

};

/* Function to show an X-time graph with the difference between the
 * ingestion time and the generation time per source */
export function create_source_generation_time_to_ingestion_time_xy(sources, dom_id){

    sourceFunctions.create_source_generation_time_to_ingestion_time_xy(sources, dom_id);

};

/* Function to provide a way to request information from database from javascript */
export function request_info(url, callback, parameters){

    queryFunctions.request_info(url, callback, parameters);

};

/* Functions for providing management on the BOA processes */
function handle_return_status(parameters, command_status){

    document.getElementById(parameters["dom_indicator_id"]).className = "circle"
    if (command_status["return_code"] == 0){
        var message = parameters["success_message"]
        if (command_status["output"]){
            message += "</br>The output of the executed command was:</br>" + command_status["output"]
        }
        toastr.success(message)
    }
    else{
        var message = parameters["error_message"]
        if (command_status["output"] || command_status["error"]){
            message += "</br>The output of the executed command was:</br>" + command_status["output"] + "</br>The error of the executed command was: " + command_status["error"]
        }
        toastr.error(message)
    }
}

/***
 * ORC
 ***/
/* Function for switching on/off the ORC */
export function request_switch_on_off_orc(){

    queryFunctions.request_info("/check-orc-status", switch_on_off_orc, null);

};

function switch_on_off_orc(parameters, orc_status) {

    document.getElementById("orc-indicator").className = "circle loader"
    if (orc_status["scheduler"]["status"] == "on" && orc_status["ingester"]["status"] == "on"){
        parameters = {
            "success_message": "ORC was switched off sucessfully",
            "error_message": "ORC could not be switched off sucessfully",
            "dom_indicator_id": "orc-indicator"
        }
        queryFunctions.request_info("/switch-off-orc", handle_return_status, parameters);
    }else{
        parameters = {
            "success_message": "ORC was switched on sucessfully",
            "error_message": "ORC could not be switched on sucessfully",
            "dom_indicator_id": "orc-indicator"
        }
        queryFunctions.request_info("/switch-on-orc", handle_return_status, parameters);
    }
    
};

/* Function to update the status of the orc */
setInterval(request_and_update_orc_status, 1000);

function request_and_update_orc_status() {
    
    queryFunctions.request_info("/check-orc-status", update_orc_status, null);
    
};

function update_orc_status(parameters, orc_status) {

    if (! document.getElementById("orc-indicator").className.includes("loader")){
        if (orc_status["scheduler"]["status"] == "on" && orc_status["ingester"]["status"] == "on"){
            document.getElementById("orc-indicator").className = "circle green-circle"
        }else if (orc_status["scheduler"]["status"] == "on" || orc_status["ingester"]["status"] == "on"){
            document.getElementById("orc-indicator").className = "circle yellow-circle"
        }else{
            document.getElementById("orc-indicator").className = "circle red-circle"
        }
    }
    
};

/***
 * CRON
 ***/
/* Function for switching on/off the CRON */
export function request_switch_on_off_cron(){

    queryFunctions.request_info("/check-cron-status", switch_on_off_cron, null);
    
};

function switch_on_off_cron(parameters, cron_status) {

    document.getElementById("cron-indicator").className = "circle loader"
    if (cron_status["crond"]["status"] == "on"){
        parameters = {
            "success_message": "CRON was switched off sucessfully",
            "error_message": "CRON could not be switched off sucessfully",
            "dom_indicator_id": "cron-indicator"
        }
        queryFunctions.request_info("/switch-off-cron", handle_return_status, parameters);
    }else{
        parameters = {
            "success_message": "CRON was switched on sucessfully",
            "error_message": "CRON could not be switched on sucessfully",
            "dom_indicator_id": "cron-indicator"
        }
        queryFunctions.request_info("/switch-on-cron", handle_return_status, parameters);
    }
    
};

/* Function to update the status of the cron */
setInterval(request_and_update_cron_status, 1000);

function request_and_update_cron_status() {
    
    queryFunctions.request_info("/check-cron-status", update_cron_status, null);
    
};

function update_cron_status(parameters, cron_status) {

    if (! document.getElementById("cron-indicator").className.includes("loader")){
        if (cron_status["crond"]["status"] == "on"){
            document.getElementById("cron-indicator").className = "circle green-circle"
        }else{
            document.getElementById("cron-indicator").className = "circle red-circle"
        }
    }

};
