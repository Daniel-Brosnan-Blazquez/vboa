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
import * as vis_data from "vis-data/dist/umd.js";
import * as vis_network from "vis-network/peer/umd/vis-network.min.js";
import * as vis_timeline_graph2d from "vis-timeline/peer/umd/vis-timeline-graph2d.js";
import * as chartjs from "chart.js/dist/Chart.js";
import "chartjs-plugin-labels/build/chartjs-plugin-labels.min.js";
import * as graph from "./graph.js";
import * as sourceFunctions from "./sources.js";
import * as reportFunctions from "./reports.js";
import * as gaugeFunctions from "./gauges.js";
import * as annotationCnfsFunctions from "./annotation_confs.js";
import * as eventFunctions from "./events.js";
import * as alertFunctions from "./alerts.js";
import * as annotationFunctions from "./annotations.js";
import * as eventKeyFunctions from "./event_keys.js";
import * as dimSignatureFunctions from "./dim_signatures.js";
import * as erFunctions from "./explicit_references.js";
import * as queryFunctions from "./query.js";
import * as dates from "./dates.js";
import * as datatableFunctions from "./datatables.js";
import * as selectorFunctions from "./selectors.js";
import * as screenshotFunctions from "./screenshots.js";
import * as renderFunctions from "./render.js";

/* css */
import "bootstrap-datetime-picker/css/bootstrap-datetimepicker.min.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-social/bootstrap-social.css";
import "font-awesome/css/font-awesome.min.css";
import "bootstrap-responsive-tabs/dist/css/bootstrap-responsive-tabs.css";
import "datatables/media/css/jquery.dataTables.min.css";
import "datatables.net-select-dt/css/select.dataTables.min.css";
import "vis-timeline/dist/vis-timeline-graph2d.min.css";
import "vis-network/dist/vis-network.min.css";
import "chart.js/dist/Chart.min.css";
import "chosen-js/chosen.min.css";
import "ol/ol.css";
import "metismenu/dist/metisMenu.min.css";
import "toastr/build/toastr.min.css";

/* Save the very same page in the div with id boa-html-page */
jQuery(document).ready(function(){
    var html_content = document.documentElement.innerHTML
    var html = '<!doctype html>\n<html lang="en">\n' + html_content + "\n</html>"
    var compressed_html = btoa(html)
    document.getElementById("boa-html-page").innerHTML = compressed_html
});

setInterval(update_clock, 1000);

/* Hide service processes status after 60 seconds */
jQuery(document).ready(function(){
    jQuery('#boa-management-menu').click(function(){
        setTimeout(function () {
            // Remove attribute aria-expanded of the link element
            var a = document.getElementById("boa-management-menu")
            document.getElementById("boa-management-menu").removeAttributeNode(a.getAttributeNode("aria-expanded"));
            // Remove collapse content
            document.getElementById("boa-management-menu-li").classList.remove("mm-active");
            document.getElementById("boa-management-menu-ul").classList.remove("mm-show");
        }, 60000);
    });
});

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

/* Activate tooltips */
jQuery(document).ready(function(){
  jQuery('[data-toggle="tooltip"]').tooltip();
});

/* Manage side menu */
jQuery(function() {
    jQuery('#left-side-menu').metisMenu();
});

/* Toasts configuration */
toastr.options.progressBar = true; // Show how long it takes before it expires
toastr.options.timeOut = 10000; // How long the toast will display without user interaction (milliseconds)
toastr.options.extendedTimeOut = 10000; // How long the toast will display after a user hovers over it (milliseconds)

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
jQuery(document).ready(function() {
    datatableFunctions.activate_search_on_columns();
});
/* Activate search and checkboxes on the specified tables */
jQuery(document).ready(function() {
    datatableFunctions.activate_search_and_checkboxes_on_tables();
});

/* Fill source statuses */
jQuery(".query-source-statuses").one("focusin", sourceFunctions.fill_statuses);

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

export function add_reported_validity_start_reported_validity_stop(dom_id){
    dates.add_reported_validity_start_reported_validity_stop(dom_id);
}

export function add_reception_time(dom_id){
    dates.add_reception_time(dom_id);
}

export function add_ingestion_time(dom_id){
    dates.add_ingestion_time(dom_id);
}

export function add_processing_duration(dom_id){
    dates.add_processing_duration(dom_id);
}

export function add_ingestion_duration(dom_id){
    dates.add_ingestion_duration(dom_id);
}

export function add_generation_time(dom_id){
    dates.add_generation_time(dom_id);
}

export function add_reported_generation_time(dom_id){
    dates.add_reported_generation_time(dom_id);
}

export function add_event_duration(dom_id){
    dates.add_event_duration(dom_id);
}

export function add_source_validity_duration(dom_id){
    dates.add_source_validity_duration(dom_id);
}

export function add_report_validity_duration(dom_id){
    dates.add_report_validity_duration(dom_id);
}

export function add_triggering_time(dom_id){
    dates.add_triggering_time(dom_id);
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

/* Function to expand the statuses associated to a source */
export function expand_source_statuses(dom_id, source_uuid){
    sourceFunctions.expand_source_statuses(dom_id, source_uuid);
}

/* Function to expand the statuses associated to a report */
export function expand_report_statuses(dom_id, report_uuid){
    reportFunctions.expand_report_statuses(dom_id, report_uuid);
}
export function submit_request_for_execution(){
    reportFunctions.submit_request_for_execution();
}

/* Function to fill searched elements into a selector */
export function fill_elements_into_selector(input_node, route, field_name, limit, offset){

    selectorFunctions.fill_elements_into_selector(input_node, route, field_name, limit, offset);

};

/* Function to fill searched elements into a selector with no input */
export function fill_elements_into_selector_no_input(selector, route, search, field_name, limit, offset){

    selectorFunctions.fill_elements_into_selector_no_input(selector, route, search, field_name, limit, offset);

};

/*
* Graph functions
*/
/* Function to display a pie chart given the id of the DOM where to
 * attach it and the items to show */
export function display_pie(dom_id, data, options){

    jQuery(document).ready(function(){
        graph.display_pie(dom_id, data, options);
    });        

};

/* Function to display a bar graph given the id of the DOM where to
 * attach it and the items to show with corresponding groups */
export function display_bar_time(dom_id, items, groups, height){

    jQuery(document).ready(function(){
        graph.display_bar_time(dom_id, items, groups, height);
    });        

};

/* Function to display a timeline given the id of the DOM where to
 * attach it and the items to show with corresponding groups */
export function display_timeline(dom_id, items, groups, options){

    jQuery(document).ready(function(){
        graph.display_timeline(dom_id, items, groups, options);
    });        

};

/* Function to display a network given the id of the DOM where to
 * attach it and the nodes to show with the corresponding relations */
export function display_network(dom_id, nodes, edges){

    jQuery(document).ready(function(){    
        graph.display_network(dom_id, nodes, edges);
    });

};

/* Function to display an X-Time graph given the id of the DOM where to
 * attach it and the items to show with the corresponding groups */
export function display_x_time(dom_id, items, groups, options){

    jQuery(document).ready(function(){
        graph.display_x_time(dom_id, items, groups, options);
    });

};

/* Function to display a map graph given the id of the DOM where to
 * attach it and the items to show with the corresponding groups */
export function display_map(dom_id, polygons){

    jQuery(document).ready(function(){
        graph.display_map(dom_id, polygons);
    });

};

/*
* EVENTS *
*/

/* Function to show a bar graph of events */
export function prepare_events_data_for_bar(events, items, groups){

    eventFunctions.prepare_events_data_for_bar(events, items, groups);

};
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

    jQuery(document).ready(function(){
        eventFunctions.create_event_timeline(events, dom_id);
    });

};

/* Function to show a network of events */
export function create_event_network(events, dom_id){

    jQuery(document).ready(function(){
        eventFunctions.create_event_network(events, dom_id);
    });

};

/* Function to show a map for events */
export function create_event_map(geometries, dom_id){

    jQuery(document).ready(function(){
        eventFunctions.create_event_map(geometries, dom_id);
    });

};

/*
* ALERTS *
*/

/* Function to show a timeline of alerts */
export function create_alert_timeline(alerts, dom_id){

    jQuery(document).ready(function(){
        alertFunctions.create_alert_timeline(alerts, dom_id);
    });

};

/*
* ANNOTATIONS *
*/

/* Function to show a map for annotations */
export function create_annotation_map(geometries, dom_id){

    jQuery(document).ready(function(){
        annotationFunctions.create_annotation_map(geometries, dom_id);
    });

};

/*
* EXPLICIT REFERENCES *
*/

/* Function to show a network of explicit references */
export function create_er_network(ers, dom_id){

    jQuery(document).ready(function(){
        erFunctions.create_er_network(ers, dom_id);
    });

};

/*
* GAUGES *
*/

/* Function to show a network of gauges */
export function create_gauge_network(gauges, dom_id){

    jQuery(document).ready(function(){
        gaugeFunctions.create_gauge_network(gauges, dom_id);
    });

};

/*
* SOURCES *
*/

/* Function to show a timeline of validities for the sources */
export function create_source_validity_timeline(sources, dom_id){

    jQuery(document).ready(function(){
        sourceFunctions.create_source_validity_timeline(sources, dom_id);
    });

};

/* Function to show a timeline of validities for the sources */
export function create_source_generation_to_ingestion_timeline(sources, dom_id){

    jQuery(document).ready(function(){
        sourceFunctions.create_source_generation_to_ingestion_timeline(sources, dom_id);
    });

};

/* Function to show an X-time graph with the number of events per source */
export function create_source_number_events_xy(sources, dom_id){

    jQuery(document).ready(function(){
        sourceFunctions.create_source_number_events_xy(sources, dom_id);
    });

};

/* Function to show an X-time graph with the ingestion duration per source */
export function create_source_ingestion_duration_xy(sources, dom_id){

    jQuery(document).ready(function(){
        sourceFunctions.create_source_ingestion_duration_xy(sources, dom_id);
    });

};

/* Function to show an X-time graph with the difference between the
 * ingestion time and the generation time per source */
export function create_source_generation_time_to_ingestion_time_xy(sources, dom_id){

    jQuery(document).ready(function(){
        sourceFunctions.create_source_generation_time_to_ingestion_time_xy(sources, dom_id);
    });

};

export function submit_request_for_ingestion_management(form_id){
    sourceFunctions.submit_request_for_ingestion_management(form_id);
}

/*
* REPORTS *
*/

/* Fill report statuses */
jQuery(".query-report-statuses").one("focusin", reportFunctions.fill_statuses);

/* Function to show a timeline of validities for the reports */
export function create_report_validity_timeline(reports, dom_id){

    jQuery(document).ready(function(){
        reportFunctions.create_report_validity_timeline(reports, dom_id);
    });

};

/* Function to show an X-time graph with the generation duration per report */
export function create_report_generation_duration_xy(reports, dom_id){

    jQuery(document).ready(function(){
        reportFunctions.create_report_generation_duration_xy(reports, dom_id);
    });

};

/* Function to show the selected report from a select button combination */
export function show_selected_report(button){

    reportFunctions.show_selected_report(button);

};

/*
* QUERY *
*/

/* Function to provide a way to request information from database from javascript */
export function request_info(url, callback, parameters){

    queryFunctions.request_info(url, callback, parameters);

};

/* Function to provide a way to request information from database from javascript with no parameters */
export function request_info_no_args(url, callback, show_loader){

    queryFunctions.request_info_no_args(url, callback, show_loader);

};

/* Function to provide a way to request information from javascript passing json as parameter */
export function request_info_json(url, callback, json, show_loader = false){

    queryFunctions.request_info_json(url, callback, json, show_loader);

};

/* Function to request information to the EBOA by URL, using json for the parameters after asking for confirmation */
export function request_info_json_after_confirmation(url, json, confirmation_message, cancel_message, show_loader = false){
    queryFunctions.request_info_json_after_confirmation(url, json, confirmation_message, cancel_message, show_loader);

};

/* Function render a received page */
export function render_page(page){

    document.open();
    document.write(page);
    document.close();

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
setInterval(request_and_update_orc_status, 3000);

request_and_update_orc_status(true)

function request_and_update_orc_status(first = false) {

    if (document.getElementById("boa-management-menu").getAttribute("aria-expanded") == "true" || first == true){
        queryFunctions.request_info("/check-orc-status", update_orc_status, null);
    }
    
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

    if (cron_status["crond"]["status"] == "on"){

        // Cron needs to be managed by the root user
        toastr.warning("You have no permissions for switching this process off." + 
                       "</br>Access with user root and perform a kill operation to the crond process")
        
    }else{

        // Cron needs to be managed by the root user
        toastr.warning("You have no permissions for switching this process on." + 
                       "</br>Access with user root and execute 'crond' process")

    }
    
};

/* Function to update the status of the cron */
setInterval(request_and_update_cron_status, 3000);

request_and_update_cron_status(true)

function request_and_update_cron_status(first = false) {

    if (document.getElementById("boa-management-menu").getAttribute("aria-expanded") == "true" || first == true){
        queryFunctions.request_info("/check-cron-status", update_cron_status, null);
    }
    
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

/***
 * SCREENSHOTS
 ***/
export function save_screenshot(report_group, group_description){

    screenshotFunctions.save_screenshot(report_group, group_description);
    
}

export function save_screenshot_with_form(report_group, group_description){

    screenshotFunctions.save_screenshot_with_form(report_group, group_description);
    
}

/***
 * SCHEDULER
 ***/
export function handle_sboa_return_status(status){

    var json_status = JSON.parse(status)
    
    if (json_status["status"] == 0){
        toastr.success(json_status["message"])
    }
    else{
        toastr.error(json_status["message"])        
    }

}

/* Function for switching on/off the Scheduler */
export function request_switch_on_off_scheduler(){

    queryFunctions.request_info("/check-scheduler-status", switch_on_off_scheduler, null);

};

function switch_on_off_scheduler(parameters, scheduler_status) {

    document.getElementById("sboa-indicator").className = "circle loader"
    if (scheduler_status["status"] == "on"){
        parameters = {
            "success_message": "Scheduler was switched off sucessfully",
            "error_message": "Scheduler could not be switched off sucessfully",
            "dom_indicator_id": "sboa-indicator"
        }
        queryFunctions.request_info("/switch-off-scheduler", handle_return_status, parameters);
    }else{
        parameters = {
            "success_message": "Scheduler was switched on sucessfully",
            "error_message": "Scheduler could not be switched on sucessfully",
            "dom_indicator_id": "sboa-indicator"
        }
        queryFunctions.request_info("/switch-on-scheduler", handle_return_status, parameters);
    }
    
};

/* Function to update the status of the scheduler */
setInterval(request_and_update_scheduler_status, 3000);

request_and_update_scheduler_status(true)

function request_and_update_scheduler_status(first = false) {

    if (document.getElementById("boa-management-menu").getAttribute("aria-expanded") == "true" || first == true){
        queryFunctions.request_info("/check-scheduler-status", update_scheduler_status, null);
    }
    
};

function update_scheduler_status(parameters, scheduler_status) {

    if (! document.getElementById("sboa-indicator").className.includes("loader")){
        if (scheduler_status["status"] == "on"){
            document.getElementById("sboa-indicator").className = "circle green-circle"
        }else{
            document.getElementById("sboa-indicator").className = "circle red-circle"
        }
    }
    
};

/* Function to create an index content at the beggining of the page */
function create_index_of_content(divs, divs_already_covered, div_index_of_content, iterator, level, parent_position){
    for (const div of divs){
        if (!divs_already_covered.includes(div)){
            // Create link in the div with class panel-heading (to go
            // to the element and to come back to the index of
            // content)
            const a_href_element = document.createElement("a");
            div.appendChild(a_href_element);
            a_href_element.setAttribute("name", "BOA-ELEMENT-OF-CONTENT-" + iterator + "-" + level + "-" + parent_position);
            a_href_element.setAttribute("href", "#BOA-INDEX-OF-CONTENT-" + iterator + "-" + level + "-" + parent_position);
            a_href_element.innerHTML = "<i class='fa fa-level-up'></i>";
            a_href_element.classList.add("panel-index-reference");
            
            // Create link for the element in the index of content (to go
            // to the element and to come back to the index of
            // content)
            const div_index_element = document.createElement("div");
            div_index_element.classList.add("row");
            div_index_of_content.appendChild(div_index_element);
            const a_index_element = document.createElement("a");
            div_index_element.appendChild(a_index_element);
            a_index_element.setAttribute("name", "BOA-INDEX-OF-CONTENT-" + iterator + "-" + level + "-" + parent_position);
            a_index_element.setAttribute("href", "#BOA-ELEMENT-OF-CONTENT-" + iterator + "-" + level + "-" + parent_position);
            a_index_element.textContent = div.textContent.replace(/\n */g,"").replace(/ *$/g,"").replace(/^ */g,"").replace(/ /g,"_");
            a_index_element.classList.add("index-element");

            divs_already_covered.push(div)

            // Create the collapse div with the sub-elements
            const child_divs = div.parentNode.getElementsByClassName("panel-heading");
            if (child_divs.length > 1){
                a_index_element.innerHTML = a_index_element.innerHTML + "     " + "<a  data-toggle='collapse' data-parent='#accordion' href='#boa-index-of-content-" + iterator + "-level-" + level + "'><i class='fa fa-angle-double-down'></i></a>";
                const div_next_level = document.createElement("div");
                div_next_level.classList.add("row");
                div_next_level.classList.add("collapse");
                div_next_level.classList.add("panel-index");
                div_next_level.id = "boa-index-of-content-" + iterator + "-level-" + level;
                div_index_element.parentNode.insertBefore(div_next_level, div_index_element.nextSibling);
                create_index_of_content(child_divs, divs_already_covered, div_next_level, 0, level+1, iterator);
            };
            iterator++;

        };
    };    
};

jQuery(document).ready(function() {
    // Build the div where the index of content will be placed
    const div_page_header = document.getElementsByClassName("page-header")[0].parentNode;
    if (! div_page_header.classList.contains("panel-no-index")){
        const div_index_of_content = document.createElement("div");
        div_index_of_content.classList.add("row");
        div_index_of_content.id = "boa-index-of-content";
        div_page_header.parentNode.insertBefore(div_index_of_content, div_page_header.nextSibling);

        // Obtain panel headings to be traced in index of content
        const divs = document.getElementsByClassName("panel-heading");
        
        jQuery("#boa-index-of-content").append("<div class='panel panel-default'><div class='panel-heading'><h3 class='panel-title'><a data-toggle='collapse' data-parent='#accordion' href='#panel-body-index-of-conent'>Index of content <span class='fa fa-angle-double-down'></span></a></h3></div><div class='panel-body panel-collapse panel-index collapse in' id='panel-body-index-of-conent'></div></div>");

        const div_panel_body_index = document.getElementById("panel-body-index-of-conent");
        
        var divs_already_covered = [];
        var iterator = 0;
        var level = 0;

        create_index_of_content(divs, divs_already_covered, div_panel_body_index, iterator, level, -1);
    };
});
