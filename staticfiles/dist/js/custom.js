$(document).ready(function () {
  var spinner= $('#uploadSpinner');
  var spinnerText=$('#uploadText');
  var message=$('#successMessage');
  $('#uploadForm').submit(function (event) {
      event.preventDefault();
      var formData = new FormData($(this)[0]);
      var fileType = $('input[type=radio]:checked').val();
      var fileInput = $('#file')[0];
      if (!fileType) {
          alert('Please select a file type.');
          return;
      }
      formData.delete('file'); // Clear file data

      if (fileInput.files.length > 0) {
          formData.append("file",fileInput.files[0]);
      } else {
          alert('Please select a file to upload.');
          return;
      }
      spinner.removeClass('d-none');
      spinnerText.removeClass('d-none');
      message.addClass('d-none');
      $.ajax({
          url: '/api/upload-data/',
          type: 'POST',
          data: formData,
          contentType: false,
          processData: false,
          success: function (response) {
              spinner.addClass('d-none');
              spinnerText.addClass('d-none');
              message.removeClass('d-none');
              alert(response.json())
          },
          error: function (xhr, status, error) {
              $('#uploadSpinner').addClass('d-none');
              $('#uploadText').addClass('d-none');
              alert(error);
          }
      });
  });
  // Event listener for running analytics button
  $('#runAnalyticsBtn').click(function () {
      spinnerText.text("Analytics running...")
      spinner.removeClass('d-none');
      spinnerText.removeClass('d-none');
      message.addClass('d-none');
      $.ajax({
          url: '/api/run-analytics/',
          type: 'POST',
          data: {},
          contentType: false,
          processData: false,
          success: function (response) {
              //Handle success response
              message.text("Analytics executed successfully...")
              spinner.addClass('d-none');
              spinnerText.addClass('d-none');
              message.removeClass('d-none');
              console.log('Analytics executed successfully.');
          },
          error: function (xhr, status, error) {
              //Handle error response
              message.text("Error executing analytics:"+error)
              spinner.addClass('d-none');
              spinnerText.addClass('d-none');
              message.removeClass('d-none');
              message.addClass('bg-danger')
              console.error('Error executing analytics:', error);
          }
      });
  });
});