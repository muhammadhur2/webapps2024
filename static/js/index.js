$('#abc').load(' #abc');
var timeout = setInterval(reloadDF, 5000);
function reloadDF () {
$('#abc').load(' #abc');
}
//
//function loadlink(){
//    $('#abc').load('$abc',function () {
//         $(this).unwrap();
//    });
//}
//
//loadlink(); // This will run on page load
//setInterval(function(){
//    loadlink() // this will run after every 5 seconds
//}, 5000);



