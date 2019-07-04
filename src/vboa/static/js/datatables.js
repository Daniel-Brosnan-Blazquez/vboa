
/* Function to activate the search on every column */
export function activate_search_on_columns() {
    // Setup - add a text input to each footer cell
    jQuery(".table tfoot th").each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );
 
    // DataTable
    var tables = jQuery(".table-search").each( function (){
        var table = $(this).DataTable({
            responsive: true,
            aLengthMenu: [
                [10, 25, 50, 100, 200, -1],
                [10, 25, 50, 100, 200, "All"]
            ],
            iDisplayLength: -1,
            select: true,
            scrollX: true,
            // This is to hide the second header set by the scrollX
            initComplete: function(settings, json) {
                $('.dataTables_scrollBody thead tr').css({visibility:'collapse'});
            },
            scrollY: "500px",
            /* dom:
               B: Buttons
               l: lenght changing input control
               f: filtering input
               t: table
               i: summary information
             */
            dom: 'Blftip',
            "order": [],
            buttons: [
                'copyHtml5',
                {
                    extend: 'excelHtml5',
                    text: 'Export excel',
                    filename: 'Export excel',
                    exportOptions: {
                        modifier: {
                            page: 'all'
                        }
                    }
                },
            ]
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
    })
};
