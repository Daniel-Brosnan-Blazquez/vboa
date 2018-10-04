import "bootstrap/dist/js/bootstrap.min.js";
import "bootstrap-datetime-picker/js/bootstrap-datetimepicker.min.js";
import "bootstrap-datetime-picker/css/bootstrap-datetimepicker.min.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-social/bootstrap-social.css";
import "font-awesome/css/font-awesome.min.css";

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
