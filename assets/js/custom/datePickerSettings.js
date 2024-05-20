// datePickerSettings.js

document.addEventListener("DOMContentLoaded", function() {
    // Choices.js
    var choicesMultiple = document.querySelector(".choices-multiple");
    if (choicesMultiple) {
      new Choices(choicesMultiple);
    }
  
    // Flatpickr
    flatpickr(".flatpickr-minimum");
    flatpickr(".flatpickr-datetime", {
      enableTime: true,
      dateFormat: "d-m-Y H:i",
    });
    flatpickr(".flatpickr-human", {
      altInput: true,
      altFormat: "F j, Y",
      dateFormat: "d-m-Y",
    });
    flatpickr(".flatpickr-multiple", {
      mode: "multiple",
      dateFormat: "d-m-Y"
    });
    flatpickr(".flatpickr-range", {
      mode: "range",
      dateFormat: "d-m-Y"
    });
    flatpickr(".flatpickr-time", {
      enableTime: true,
      noCalendar: true,
      dateFormat: "H:i",
    });
  
    // Date filter AJAX
    $(document).ready(function () {
      // Function to fetch and display data based on interval
      function fetchAndDisplayData(interval, startDate = null, endDate = null) {
        var requestData = {};
  
        if (interval === 'custom') {
          requestData = {
            start_date: startDate,
            end_date: endDate
          };
          $('#dateRangeContainer').show(); // Show date range input when custom is selected
        } else {
          $('#dateRangeContainer').hide();
          requestData = {
            interval: interval
          };
        }
  
        $.ajax({
          url: '/api/report/' + reportId + '/', // reportId should be defined elsewhere
          type: 'GET',
          data: requestData,
          dataType: 'json',
          success: function (data) {
            if ($.isEmptyObject(data)) {
              $('#spreadsheet').html('<div class="alert alert-warning">No data available.</div>');
              return;
            }
  
            if (typeof data === 'string') {
              data = JSON.parse(data);
            }
  
            if (Array.isArray(data)) {
              window.reportExcelJson = data;
              new handsontableManager('spreadsheet');
            }
          },
          error: function (xhr, status, error) {
            $('#spreadsheet').html('<div class="alert alert-danger">Error fetching data.</div>');
          }
        });
      }
  
      function formatDate(dateString) {
        var parts = dateString.split('-');
        return parts[2] + '-' + parts[1] + '-' + parts[0];
      }
  
      function handleDateChange() {
        var dateRange = $('#datePicker').val().split(' to ');
        if (dateRange.length === 2) {
          var startDate = formatDate(dateRange[0]);
          var endDate = formatDate(dateRange[1]);
          fetchAndDisplayData('custom', startDate, endDate);
        } else if (dateRange.length === 1) {
          var singleDate = formatDate(dateRange[0]);
          fetchAndDisplayData('custom', singleDate, singleDate);
        }
      }
  
      // Trigger fetching and displaying data when the page loads with the default selected interval
      fetchAndDisplayData($('#timeInterval').val());
  
      // Event handler for when the select element's value changes
      $('#timeInterval').change(function () {
        var selectedValue = $(this).val();
        if (selectedValue === 'custom') {
          $('#dateRangeContainer').show();
          handleDateChange();
        } else {
          $('#dateRangeContainer').hide();
          fetchAndDisplayData(selectedValue);
        }
      });
  
      // Event handler for date range change
      $('#datePicker').change(function () {
        handleDateChange();
      });
    });
  });
  