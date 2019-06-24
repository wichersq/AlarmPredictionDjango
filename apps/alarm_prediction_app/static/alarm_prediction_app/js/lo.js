<script type="text/javascript" src="http://maps.google.com/maps/api/js?
libraries=geometry&amp;sensor=false">
</script>


var encodedPoints   = "s}dcFlnchVz@n@vJeVpF}NzMy\\} KyI{AoBg@{@wKmWs@wB_AsE_@wEQkLQ}Cy@qE{@kCiBsD{_@_r@qS{\\mBqDoOw^mBwGOqAPyEGsAKu@eBmEOu@Eu@X}DEu@r_@osCjJyi@| AiH~B_NxJoe@j[kdBjLwl@rJkh@zG_]jCsOhEe\\`Iur@pBuOjAuLhAsI| BcPnCuNhAiEz@_B~@kA| AgAnLcDvBmAt@o@dBwBxEwJtI_PzBcDdE_EnVePpg@o]lKsFzJgE`EkCjCqCrB{CvAwCtBmFfAsB`DiEdC_CpEkClGgC`EyBrG_ETAdHuDx@YdAKhEb@jB]hAi@{EaOmDqJeEnC" ; 

var decodedPoints = google.maps.geometry.encoding.decodePath(encodedPoints) ; 

var encodedPolyline = new google.maps.Polyline ( {
              strokeColor: "#970E04" ,
              strokeOpacity: 1.0 ,
              strokeWeight: 2 ,
              path: decodedPoints ,
              clickable: false 
} );
encodedPolyline.setMap(myMap); 