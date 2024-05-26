function downloadExcel(jsonData) {
    if (!Array.isArray(jsonData)) {
        console.error('Data is not an array:', jsonData);
        return; // Exit if data is not an array
    }

    // Continue with Excel file creation if data is correct
    const worksheet = XLSX.utils.json_to_sheet(jsonData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Report");
    XLSX.writeFile(workbook, "Report.xlsx");
}



function handsontableManager(containerId) {
    this.container = document.getElementById(containerId);
    this.hotInstance = null;

    // Initialize or update Handsontable
    this.initOrUpdateHandsontable = function(data) {
        if (this.hotInstance) {
            this.hotInstance.loadData(data);
        } else if (data.length > 0) {
            var headers = Object.keys(data[0]);
            var columns = headers.map(header => ({
                data: header,
                type: 'text' // Customize type based on data as needed
            }));

            this.hotInstance = new Handsontable(this.container, {
                data: data,
                rowHeaders: true,
                colHeaders: headers,
                columns: columns,
                filters: true,
                dropdownMenu: true,
                manualColumnResize: true,
                manualRowResize: true,
                colWidths: 150,
                columnSorting: true,
                renderAllRows: false,
                contextMenu: true,
                batch: true,
                licenseKey: 'non-commercial-and-evaluation'
            });
        } else {
            this.container.innerHTML = '<div class="alert alert-warning" role="alert">No data to show.</div>';
        }
    };

    // Initial call to setup or update the table
    var initialData = window.reportExcelJson || [];
    this.initOrUpdateHandsontable(initialData);



    // Usage:
    // In your HTML, after including this script, instantiate the manager:
    // new handsontableManager('spreadsheet');

    // Below codes to be present
    /* 
    =============
        <link href="{% static 'css/handsontable.full.min.css' %}" rel="stylesheet" />
    =============

    =============
        <div id="spreadsheet" class="handsontable" style="display: block"></div>
    =============

    =============
    window.reportExcelJson = {{ report_excel_json|safe }};  // Make JSON data available globally

    OR

    <script>
        success: function(data) {
                // Ensure that data is an array
                if (typeof data === 'string') {
                    try {
                        data = JSON.parse(data);  // Parse string into JSON
                    } catch (e) {
                        console.error("Error parsing JSON!", e);
                    }
                }

                if (Array.isArray(data)) {
                    window.reportExcelJson = data;
                    document.dispatchEvent(new Event('dataUpdated'));  // Trigger the event
                } else {
                    console.error("Data is not an array:", data);
                }
            },
    </script>
        
        >> report_excel_json is a JSON coming as orient="records".
        >> Sample:
        [{"SR NO":14825,"Invoice No":"INV-SSUP-DS-4048","Invoice Date":"2024-02-01","Customer Name":"SPECTRUM INNS & MOTELS P. LTD","Customer GSTN":"04AAOCS6433L1ZY","Item Code":"ACOUSTIC FOAM","Item Name":"ACOUSTIC FOAM Pyramid-1\" x 1\"-50 mm-(20 mm + 30 mm)-D-32-Comfy-Black-Without Adhesive Quoted","Quantity":640.0,"Rate":28.25,"Taxable Amt":18080.0,"CGST":0,"SGST":0,"IGST":3254.4,"Net Total":21334.4,"Year":2024,"Month":2},{"SR NO":14563,"Invoice No":"INV-SSUP-DS-4123","Invoice Date":"2024-02-07","Customer Name":"RAJAT FOAM SALES","Customer GSTN":"07AABFR2160B1ZT","Item Code":"ACOUSTIC FOAM","Item Name":"ACOUSTIC FOAM Base Trap-12'' X 12''-24''-Diffuser-D-32-Comfy-Black-Without Adhesive Quoted","Quantity":32.53,"Rate":245.0,"Taxable Amt":7969.85,"CGST":0,"SGST":0,"IGST":1434.57,"Net Total":9404.42,"Year":2024,"Month":2}]
    =============

    =============
        <script src="{% static 'js/handsontable.full.min.js' %}"></script>
        <script src="{% static 'js/custom/commonutil.js' %}"></script>
    =============
    */
}

document.addEventListener('DOMContentLoaded', function () {
    const scrollableContainer = document.getElementById('scrollable-container');
    const scrollAlert = document.getElementById('scroll-alert');
    let alertTimeout;

    scrollableContainer.addEventListener('wheel', function (e) {
        if (e.deltaY !== 0 && !e.shiftKey) {
            // Show alert message
            scrollAlert.style.display = 'block';

            // Clear previous timeout
            clearTimeout(alertTimeout);

            // Hide alert message after 3 seconds
            alertTimeout = setTimeout(function () {
                scrollAlert.style.display = 'none';
            }, 3000);
        }

        // Horizontal scrolling with Shift key
        if (e.shiftKey) {
            scrollableContainer.scrollLeft += e.deltaY;
            e.preventDefault();
        }
    });

    // Close the alert when the close button is clicked
    document.querySelector('.btn-close').addEventListener('click', function () {
        scrollAlert.style.display = 'none';
    });
  });
