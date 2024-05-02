// Below code to be present, for utilising this library
{
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
    <script src="{% static 'js/dynamic_handsontable.js' %}"></script>
=============
*/
}

document.addEventListener("DOMContentLoaded", function () {
  var container = document.getElementById("spreadsheet");
  var jsonData = window.reportExcelJson || [];

  // Function to initialize or update Handsontable
  function initOrUpdateHandsontable(data) {
    if (window.hotInstance) {
      window.hotInstance.loadData(data);
    } else {
      var headers = Object.keys(data[0]);
      var columns = headers.map((header) => ({ data: header, type: "text" }));
      window.hotInstance = new Handsontable(container, {
        data: data,
        rowHeaders: true,
        colHeaders: headers,
        columns: columns,
        filters: true,
        dropdownMenu: true,
        manualColumnResize: true,
        manualRowResize: true,
        contextMenu: true,
        licenseKey: "non-commercial-and-evaluation",
      });
    }
  }

  // Initial setup
  if (jsonData.length > 0) {
    initOrUpdateHandsontable(jsonData);
  } else {
    container.innerHTML =
      '<div class="alert alert-warning" role="alert">No data to show.</div>';
  }

  // Setup an event listener for when data updates
  document.addEventListener("dataUpdated", function () {
    jsonData = window.reportExcelJson;
    initOrUpdateHandsontable(jsonData);
  });
});
