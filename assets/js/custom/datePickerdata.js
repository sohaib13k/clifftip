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
      dateFormat: "d-m-Y",
      allowInput: true,
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
          $('#dateRangeContainer01').show(); // Show date range input when custom is selected
        } else {
          $('#dateRangeContainer01').hide();
          requestData = {
            interval: interval
          };
        }
  
        $.ajax({
          url: "{% url 'report-datefilter-data-api' result.invoice_report.report.id|default:'0' %}",
          type: 'GET',
          data: requestData,
          dataType: 'json',
          success: function (data) {
            $('#less-than-zero-count').text(data.less_than_zero.count);
            $('#less-than-zero-percentage').text(data.less_than_zero.percentage.toFixed(2) + '%');
    
            $('#zero-count').text(data.zero.count);
            $('#zero-percentage').text(data.zero.percentage.toFixed(2) + '%');
    
            $('#one-count').text(data.one.count);
            $('#one-percentage').text(data.one.percentage.toFixed(2) + '%');
    
            $('#more-than-one-count').text(data.more_than_one.count);
            $('#more-than-one-percentage').text(data.more_than_one.percentage.toFixed(2) + '%');
    
            $('#cond-1-top').text((data.cond_1.top).toFixed(2) + '%');
            $('#cond-1-bottom').text((data.cond_1.bottom).toFixed(2) + '%');
    
            $('#cond-2-top').text((data.cond_2.top).toFixed(2) + '%');
            $('#cond-2-bottom').text((data.cond_2.bottom).toFixed(2) + '%');
          },
          error: function (error) {
            console.error('Error fetching data:', error);
          }
        });
      }
  
      function formatDate(dateString) {
        var parts = dateString.split('-');
        return parts[2] + '-' + parts[1] + '-' + parts[0];
      }
  
      function handleDateChange() {
        var dateRange = $('#datePicker01').val().split(' to ');
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
      fetchAndDisplayData($('#timeInterval01').val());
  
      // Event handler for when the select element's value changes
      $('#timeInterval01').change(function () {
        var selectedValue = $(this).val();
        if (selectedValue === 'custom') {
          $('#dateRangeContainer01').show();
          handleDateChange();
        } else {
          $('#dateRangeContainer01').hide();
          fetchAndDisplayData(selectedValue);
        }
      });
  
      // Event handler for date range change
      $('#datePicker01').change(function () {
        handleDateChange();
      });
    });
  });
  