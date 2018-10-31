
/* Function to display a timeline given the id of the DOM where to
 * attach it and the data to show */
export function display_timeline(dom_id, items, groups){

    /* create timeline */
    var container = document.getElementById(dom_id);

    var options = {
        groupOrder: 'content'
    };
    
    var timeline = new vis.Timeline(container, items, groups, options);

};
