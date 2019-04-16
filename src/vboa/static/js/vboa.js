/* js */
import "bootstrap/dist/js/bootstrap.min.js";
import "bootstrap-datetime-picker/js/bootstrap-datetimepicker.min.js";
import "bootstrap-responsive-tabs/dist/js/jquery.bootstrap-responsive-tabs.min.js";
import "datatables/media/js/jquery.dataTables.min.js";
import "chosen-js/chosen.jquery.min.js";
import "metismenu/dist/metisMenu.min.js";
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

var timeout = 1000000

/* Set a timeout if the page is not ready after 10 seconds */
setTimeout(go_back, timeout);

function go_back(){
    if (document.readyState != "complete"){
        window.history.back();
    }
}

/* Activate chosen for the multiple input selection */
jQuery(".chosen-select").chosen({
    no_results_text: "Nothing found for the following criteria: ",
    width: "100%"
});

/* Manage side menu */
$(function() {
    $('#side-menu').metisMenu();
});

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

export function expand_annotation_values(dom_id, annotation_uuid){
    annotationFunctions.expand_values(dom_id, annotation_uuid);
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

/*
* EVENTS *
*/

/* Function to show a timeline of events */
export function create_event_timeline(events, dom_id){

    eventFunctions.create_event_timeline(events, dom_id);

};

/* Function to show a network of events */
export function create_event_network(events, dom_id){

    eventFunctions.create_event_network(events, dom_id);

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
