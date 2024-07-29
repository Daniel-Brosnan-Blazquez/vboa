
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
    return parseInt(elements[0]) * 60 * 60 + parseInt(elements[1]) * 60 + parseInt(elements[2]);
}

export function interval_to_minutes(interval){
    return interval_to_seconds(interval) / 60;
}

/* Function to add more start and stop selectors when commanded */
export function add_start_stop(dom_id){
    
    jQuery.get("/static/html/more_start_stop.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

    react_activate_datetimepicker(dom_id);

};

/* Function to add more validity start and validity stop selectors when commanded */
export function add_validity_start_validity_stop(dom_id){

    jQuery.get("/static/html/more_validity_start_validity_stop.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

    react_activate_datetimepicker(dom_id);

};

/* Function to add more reported validity start and reported validity stop selectors when commanded */
export function add_reported_validity_start_reported_validity_stop(dom_id){

    jQuery.get("/static/html/more_reported_validity_start_reported_validity_stop.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

    react_activate_datetimepicker(dom_id);

};

/* Function to add more reception time selectors when commanded */
export function add_reception_time(dom_id){
    
    jQuery.get("/static/html/more_reception_time.html", function (data){
        jQuery("#" + dom_id).append(data);
    });
    
    react_activate_datetimepicker(dom_id);

};

/* Function to add more ingestion time selectors when commanded */
export function add_ingestion_time(dom_id){
    
    jQuery.get("/static/html/more_ingestion_time.html", function (data){
        jQuery("#" + dom_id).append(data);
    });
    
    react_activate_datetimepicker(dom_id);

};

/* Function to add more processing duration selectors when commanded */
export function add_processing_duration(dom_id){
    
    jQuery.get("/static/html/more_processing_duration.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

};

/* Function to add more ingestion duration selectors when commanded */
export function add_ingestion_duration(dom_id){
    
    jQuery.get("/static/html/more_ingestion_duration.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

};

/* Function to add more event duration selectors when commanded */
export function add_event_duration(dom_id){
    
    jQuery.get("/static/html/more_event_duration.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

};

/* Function to add more source validity duration selectors when commanded */
export function add_source_validity_duration(dom_id){
    
    jQuery.get("/static/html/more_source_validity_duration.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

};

/* Function to add more generation time selectors when commanded */
export function add_generation_time(dom_id){
    
    jQuery.get("/static/html/more_generation_time.html", function (data){
        jQuery("#" + dom_id).append(data);
    });
    
    react_activate_datetimepicker(dom_id);

};

/* Function to add more reported generation time selectors when commanded */
export function add_reported_generation_time(dom_id){
    
    jQuery.get("/static/html/more_reported_generation_time.html", function (data){
        jQuery("#" + dom_id).append(data);
    });
    
    react_activate_datetimepicker(dom_id);

};

/* Function to add more solved time selectors when commanded */
export function add_solved_time(dom_id){
    
    jQuery.get("/static/html/more_solved_time.html", function (data){
        jQuery("#" + dom_id).append(data);
    });
    
    react_activate_datetimepicker(dom_id);

};

/* Function to add more rnotification time selectors when commanded */
export function add_notification_time(dom_id){
    
    jQuery.get("/static/html/more_notification_time.html", function (data){
        jQuery("#" + dom_id).append(data);
    });
    
    react_activate_datetimepicker(dom_id);

};

/* Function to add more report validity duration selectors when commanded */
export function add_report_validity_duration(dom_id){
    
    jQuery.get("/static/html/more_report_validity_duration.html", function (data){
        jQuery("#" + dom_id).append(data);
    });

};

/* Function to add more triggering time selectors when commanded */
export function add_triggering_time(dom_id){
    
    jQuery.get("/static/html/more_triggering_time.html", function (data){
        jQuery("#" + dom_id).append(data);
    });
    
    react_activate_datetimepicker(dom_id);

};

/* Function to react on mutations and call to activate the datetime picker */
function react_activate_datetimepicker(dom_id){

    var target = document.querySelector("#" + dom_id);
    if (target != null){
        var observer = new MutationObserver(
            function(mutations) {      
                activate_datetimepicker();
            });
        /* Observe changes on the childs */
        var config = {childList: true};
        
        /* Attach the observer to the target */
        observer.observe(target, config);
    }

}

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
