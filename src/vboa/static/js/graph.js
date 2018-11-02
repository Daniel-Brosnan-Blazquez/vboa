
/* Function to display a timeline given the id of the DOM where to
 * attach it and the items to show with corresponding groups */
export function display_timeline(dom_id, items, groups){

    /* create timeline */
    var container = document.getElementById(dom_id);

    var options = {
        groupOrder: 'content'
    };
    
    var timeline = new vis.Timeline(container, items, groups, options);

};

/* Function to display a network given the id of the DOM where to
 * attach it and the nodes to show with the corresponding relations */
export function display_network(dom_id, nodes, edges){

    /* create timeline */
    var container = document.getElementById(dom_id);

    var data = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
    };
    
    var options = {
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -250000
            }
        }
    };
    console.log(data);
    console.log(container);
    var network = new vis.Network(container, data, options);

};
