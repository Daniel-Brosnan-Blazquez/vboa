import * as queryFunctions from "./query.js";
import * as toastr from "toastr/toastr.js";

export function save_screenshot(report_group, group_description){

    var html = atob(document.getElementById("boa-html-page").innerHTML);

    var data = {
        "html": html,
        "name": "test",
        "group": report_group,
        "group_description": group_description
    }

    queryFunctions.request_info_json("/save-screenshot", notify_end_of_saving_of_screenshot, data, true)

}

export function save_screenshot_with_form(report_group, group_description){

    jQuery('input:text, input:hidden, input:password').each(function() {
        var v=this.value; 
        jQuery(this).attr("magicmagic_value",v).removeAttr("value").val(v);
    });
    jQuery('input:checkbox,input:radio').each(function() {
        var v=this.checked; 
        if(v) jQuery(this).attr("magicmagic_checked","checked"); 
        jQuery(this).removeAttr("checked"); 
        if(v) this.checked=true; 
    });
    jQuery('select option').each(function() { 
        var v=this.selected; 
        if(v) jQuery(this).attr("magicmagic_selected","selected"); 
        jQuery(this).removeAttr("selected");
        if(v) this.selected=true; 
    });
    jQuery('textarea').each(function() { 
        jQuery(this).html(this.value); 
    });

    var head=jQuery('html').html().replace(/magicmagic_/g,"");

    jQuery('[magicmagic_value]').removeAttr('magicmagic_value');
    jQuery('[magicmagic_checked]').attr("checked","checked").
        removeAttr('magicmagic_checked');
    jQuery('[magicmagic_selected]').attr("selected","selected").
        removeAttr('magicmagic_selected');
    
    var html = '<!doctype html>\n<html lang="en">\n' + head + "\n</html>"

    var data = {
        "html": html,
        "name": "test",
        "group": report_group,
        "group_description": group_description
    }

    queryFunctions.request_info_json("/save-screenshot", notify_end_of_saving_of_screenshot, data, true)

}

function notify_end_of_saving_of_screenshot(response){

    var data = JSON.parse(response)
    var message = data["message"];
    var status = data["status"];

    if (status == 0){
        toastr.success(message)
    }else{
        toastr.error(message)
    }
    return true;
}
