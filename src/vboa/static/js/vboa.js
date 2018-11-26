/* js */
import "bootstrap/dist/js/bootstrap.min.js";
import "bootstrap-datetime-picker/js/bootstrap-datetimepicker.min.js";
import "bootstrap-responsive-tabs/dist/js/jquery.bootstrap-responsive-tabs.min.js";
import "datatables/media/js/jquery.dataTables.min.js";
import * as vis from "vis/dist/vis.js";
import * as graph from "./graph.js";
import * as sourceFunctions from "./sources.js";
import * as eventFunctions from "./events.js";

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

/* Function to add more start and stop selectors when commanded */
jQuery(function (){
    jQuery("#add-start-stop").click(function () {
        jQuery.get("/static/html/more_start_stop.html", function (data){
            jQuery("#more-start-stop").append(data);
        });
    });
});

/* Function to add more start and stop selectors when commanded */
function observe_more_start_stop(){
    
    var more_start_stop_target = document.querySelector("#more-start-stop");
    if (more_start_stop_target != null){
        var observer = new MutationObserver(
            function(mutations) {      
                react_new_date_fields(mutations);
            });
        /* Observe changes on the childs */
        var config = {childList: true};
        
        /* Attach the observer to the target */
        observer.observe(more_start_stop_target, config);
    }
};

observe_more_start_stop();

/* Function to add more ingestion time selectors when commanded */
function observe_more_ingestion_time(){
    
    var more_ingestion_time_target = document.querySelector("#more-ingestion-time");
    if (more_ingestion_time_target != null){
        var observer = new MutationObserver(
            function(mutations) {      
                react_new_date_fields(mutations);
            });
        /* Observe changes on the childs */
        var config = {childList: true};
        
        /* Attach the observer to the target */
        observer.observe(more_ingestion_time_target, config);
    }
};

observe_more_ingestion_time();

/* Function to activate the datetimepicker of the new added alements */
function react_new_date_fields(mutations){
    activate_datetimepicker();
};

/* Function to add more ingestion time selectors when commanded */
jQuery(function () {
    jQuery("#add-ingestion-time").click(function () {
        jQuery.get("/static/html/more_ingestion_time.html", function (data){
            jQuery("#more-ingestion-time").append(data);
        });
    });
});

/* Assciate datetimepicker functionality */
jQuery(function () {
    activate_datetimepicker();
});

function activate_datetimepicker(){
    jQuery(".date").datetimepicker({
        initialDate: new Date(),
        todayHighlight: true,
        format: "yyyy-mm-ddThh:ii:ss",
        sideBySide: true,
        todayBtn: "linked"
    });
}

jQuery(".responsive-tabs").responsiveTabs({
  accordionOn: ['xs', 'sm'] // xs, sm, md, lg
});

/* Activate search on every column */
jQuery(function() {
    // Setup - add a text input to each footer cell
    jQuery(".table tfoot th").each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );
 
    // DataTable
    var table = jQuery(".table").DataTable({
        responsive: true,
        aLengthMenu: [
            [10, 25, 50, 100, 200, -1],
            [10, 25, 50, 100, 200, "All"]
        ],
        iDisplayLength: 10,
        scrollX: true,
        scrollY: "500px"
    });
    
    // Apply the search
    table.columns().every( function () {
        var that = this;
        $( 'input', this.footer() ).on( 'keyup change', function () {
            if ( that.search() !== this.value ) {
                that.search( this.value ).draw();
            }
        } );
    } );
} );

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
