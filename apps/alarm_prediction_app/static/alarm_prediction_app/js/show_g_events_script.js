
// $('#eventInput').on('show.bs.modal', function (event) {
//     var button = $(event.relatedTarget) // Button that triggered the modal
//     var recipient = button.data('whatever')
//     // Extract info from data-* attributes
//     $("label").css('color', "red")
//     // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
//     // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
//     var modal = $(this)
//     modal.find('.modal-title').text('New message to ' + recipient)
//     modal.find('#event_name').val("Hi")
//   })
    // $(document).ready(function() {
    //     $('#datepicker').datetimepicker({
    //         language: 'pt-BR'
    //     });
    // });
    



  $(document).on("click", '.open-Dialog', function () {
    // $('#addDialog').modal('show')
    // var button = $(event.relatedTarget) // Button that triggered the modal
    var description = $(this).data('description')
    var location = $(this).data('location')
    var start = $(this).data('start')
    var id =  $(this).data('id')
    $('form')[0].setAttribute('action', `/gcalendar/calc_alarm/${id}`);
    // Extract info from data-* attributes

    $(".modal-body #eventName").val( description )
    $(".modal-body #eventLocation").val( location )
    $(".modal-body #start_time").val( start )
  
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    // var modal = $(this)
    // modal.find('.modal-title').text('New message to ' + recipient)
    // modal.find('#event_name').val("Hi")
  });
function check_empty() {
    if (document.getElementById('name').value == "" || document.getElementById('email').value == "" || document.getElementById('msg').value == "") {
    alert("Fill All Fields !");
    } else {
    document.getElementById('form').submit();
    alert("Form Submitted Successfully...");
    }
}
//Function To Display Popup
function div_show() {
    document.getElementById('abc').style.display = "block";
}
//Function to Hide Popup
function div_hide(){
    console.log('hello');
    document.getElementById('abc').style.display = "none";
}

$(document).on("click", ".open-AddBookDialog", function () {
    var myBookId = $(this).data('id');
    $(".modal-body #bookId").val( myBookId );
    // As pointed out in comments, 
    // it is unnecessary to have to manually call the modal.
    // $('#addBookDialog').modal('show');
});