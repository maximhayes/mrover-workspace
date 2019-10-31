<template>
  <div class="wrap">
    <!-- Map goes here -->
    <canvas v-on:click="coordOut" id="map"></canvas>
  </div>
</template>

<script>

  /*function writeMsg(canvas, msg){
    var context = canvas.getContext('2d');
    context.clearRect(0,0, canvas.width, canvas.height);
    context.fillText(msg,10,25);
  }
  function getMousePos(canvas, event){sss
    var rect = canvas.getBoundingClientRect();
    return{
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
  }
  var canvas = document.getElementById("map");
  var context = canvas.getContext('2d');

  canvas.addEventListener('click', function(event){
    var mousePos = getMousePos(canvas, event);
    var msg = 'Mouse Position: ' + mousePos.x + ', ' + mousePos.y;
    writeMsg(canvas, msg);
  }, false);*/

import { LMap, LTileLayer, LMarker, LPolyline, LPopup, LTooltip, LControlScale } from 'vue2-leaflet'
import { mapGetters } from 'vuex'
import L from '../leaflet-rotatedmarker.js'

const MAX_ODOM_COUNT = 1000
const DRAW_FREQUENCY = 10

export default {
  name: 'RoverMap',

  components: {

  },

  created: function () {
    this.locationIcon = L.icon({
      iconUrl: '/static/location_marker_icon.png',
      iconSize: [64, 64],
      iconAnchor: [32, 32]
    })
    this.waypointIcon = L.icon({
      iconUrl: '/static/map_marker.png',
      iconSize: [64, 64],
      iconAnchor: [32, 64],
      popupAnchor: [0, -32]
    })
  },

  computed: {
    ...mapGetters('autonomy', {
      route: 'route',
      list: 'waypointList'
    }),

    odomLatLng: function () {
      return L.latLng(this.odom.latitude_deg + this.odom.latitude_min/60, this.odom.longitude_deg + this.odom.longitude_min/60)
    },

    polylinePath: function () {
      return [this.odomLatLng].concat(this.route.map(waypoint => waypoint.latLng))
    }
  },

  data () {

    map: []

    return {
      center: L.latLng(38.406371, -110.791954),
      url: '/static/map/{z}/{x}/{-y}.png',
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      roverMarker: null,
      waypointIcon: null,
      map: null,
      odomCount: 0,
      locationIcon: null,
      odomPath: []
    }
    
  },

  props: {
    odom: {
      type: Object,
      required: true
    }
  },

  watch: {

    odom: function (val) {
      // Trigger every time rover odom is changed

      const lat = val.latitude_deg + val.latitude_min / 60
      const lng = val.longitude_deg + val.longitude_min / 60
      const angle = val.bearing_deg

      // Update the rover marker
      this.roverMarker.setRotationAngle(angle)

      this.roverMarker.setLatLng(L.latLng(lat, lng))

      // Update the rover path
      this.odomCount++
      if (this.odomCount % DRAW_FREQUENCY === 0) {
        if (this.odomCount > MAX_ODOM_COUNT * DRAW_FREQUENCY) {
          this.odomPath.splice(0, 1)
        }
        this.odomPath.push(L.latLng(lat, lng))
      }

      this.odomPath[this.odomPath.length - 1] = L.latLng(lat, lng)
    }
  },

  methods: {
    coordOut: function(event){
      var canvas = document.getElementById('map');
      var ctx = canvas.getContext('2d');
      var map = canvas.getBoundingClientRect();
      console.log('test_msg');
      var xCoord = event.clientX - map.left;
      var yCoord = -(event.clientY - map.bottom);
      console.log('x: ' + xCoord + ', y: ' + yCoord);
      
      //draw objects on click
      ctx.fillStyle = "#138746";
      ctx.fillRect(xCoord, yCoord, 20, 20);


  },

  },

  mounted: function () {
    this.$nextTick(() => {
      this.map = this.$refs.map.mapObject
      this.roverMarker = this.$refs.rover.mapObject
    })
  }
}
</script>

<style scoped>
#map {
  height: 100%;
  width: 100%;
   background-color:#102837;
}

.wrap {
  display: flex;
  align-items: center;
  height: 100%;
}
</style>
