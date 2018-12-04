
export function date_difference_in_ms(date1, date2){
    return (new Date(date1).getTime() - new Date(date2).getTime());
}

export function date_difference_in_s(date1, date2){
    return date_difference_in_ms(date1, date2) / 1000;
}

export function date_difference_in_m(date1, date2){
    return date_difference_in_ms(date1, date2) / 1000 / 60;
}

export function interval_to_seconds(interval){
    const elements = interval.split(":");
    return (elements[0]) * 60 * 60 + (elements[1]) * 60 + elements[2];
}

/* Function to add more start and stop selectors when commanded */
export function observe_more_start_stop(){
    
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

/* Function to add more ingestion time selectors when commanded */
export function observe_more_ingestion_time(){
    
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

/* Function to activate the datetimepicker of the new added alements */
function react_new_date_fields(mutations){
    activate_datetimepicker();
};

/* Associate a datetime picker to the elements */
export function activate_datetimepicker(){
    jQuery(".date").datetimepicker({
        initialDate: new Date(),
        todayHighlight: true,
        format: "yyyy-mm-ddThh:ii:ss",
        sideBySide: true,
        todayBtn: "linked"
    });
}
