check();
// setTimeField()
function check() {
    dt = new Date();
    document.getElementById("datetime").innerHTML = dt.toLocaleString();
}

// function setTimeField() {
//     // document.getElementById('event_time_picker').valueAsDate= new Date();
//     dt = new Date();
//     console.log(dt.format('Y/m/d'))
// }

// $("#container").click(function() {
//     // add a new paragraph to the container div
// 	$("#container").append("<p>New paragraph!</p>");
// });
    
// $("tr").hover(function() {
//     	// change the text color of all elements with class 'xyz' to blue
//     	$(".table-row").css("color", "blue");
//     },
//     function() {
//     	// change the text color of all elements with class 'xyz' to black
//     	$(".table-row a").css("color", "black");
// });