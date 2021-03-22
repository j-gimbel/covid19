<template>
  <div v-if="loaded" class="container-fluid vh-100">
    <div class="row vh-100">
      <div class="col-9">
        <l-map :zoom="7" :center="[51.4, 9.0]">
          <l-geo-json
            v-if="loaded"
            :geojson="geojson"
            :options="geojsonOptions"
          />
          <l-tile-layer
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
          ></l-tile-layer>
        </l-map>
      </div>

      <div class="col-3">
        <h3>Info</h3>
        Landkreis:
        <span> {{ lkName }}</span>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, onMounted, watch } from "vue";
import { LMap, LTileLayer, LGeoJson } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
export default {
  components: {
    LMap,
    LTileLayer,
    LGeoJson,
  },

  data() {
    return {
      zoom: 6,
      geojsonOptions: {
        onEachFeature: this.onEachFeature,
        style: this.setGeoJsonStyle,
      },
      loaded: false,
      lkName: "",
    };
  },

  mounted() {
    this.loaded = true;
  },
  watch: {
    selectedLayer(o, n) {
      console.log(o, n, this.selectedLayer);
    },
    hoveredLayer(o, n) {
      console.log(o, n, this.hoveredLayer);
      this.lkName = this.hoveredLayer.feature.properties.name;
    },
    geoJsonloaded(o, n) {
      console.log("loaded!");
      this.loaded = this.geoJsonloaded;
    },
  },

  setup() {
    const defaultStyle = {
      weight: 1,

      color: "#808080",
    };

    const hoverStyle = {
      color: "#333",

      weight: 2,
    };

    const selectedStyle = {
      color: "#cc0000",
      weight: 2,
    };

    const selectedLayer = ref(null);
    const hoveredLayer = ref(null);

    const geoJsonloaded = ref(false);

    const geojson = ref({});
    const getGeojson = async () => {
      var myHeaders = new Headers();
      myHeaders.append("pragma", "no-cache");
      myHeaders.append("cache-control", "no-cache");
      myHeaders.append("Content-Type", "application/json");
      myHeaders.append("Accept", "application/json");

      var myInit = {
        method: "GET",
        headers: myHeaders,
      };

      var myRequest = new Request("landkreise_rki.geojson");
      await fetch(myRequest, myInit)
        .then(function (response) {
          console.log(response);
          return response.json();
        })
        .then(function (geojson_data) {
          console.log(geojson_data);
          geojson.value = geojson_data;
          geoJsonloaded.value = true;
          return geojson_data;
        });
    };

    const whenClicked = (e) => {
      //console.log("whenClicked", e);

      var layer = e.target;

      //if (selectedLayer != null) {
      if (selectedLayer.value != null) {
        selectedLayer.value.setStyle(defaultStyle);
        if (
          selectedLayer.value.feature.properties.id ==
          layer.feature.properties.id
        ) {
          selectedLayer.value = null;
          return;
        }
      }
      selectedLayer.value = layer;
      console.log(selectedLayer.value);
      layer.setStyle(selectedStyle);
    };

    const whenMouseover = (e) => {
      //console.log("whenMouseover", e);
      var layer = e.target;
      hoveredLayer.value = layer;
      //if (selectedLayer != null) {
      if (selectedLayer.value != null) {
        if (
          selectedLayer.value.feature.properties.id ==
          layer.feature.properties.id
        ) {
          return;
        }
      }
      layer.setStyle(hoverStyle);
    };

    const whenMouseout = (e) => {
      console.log("whenMouseout", e);
      var layer = e.target;

      //if (selectedLayer != null) {

      if (selectedLayer.value != null) {
        console.log(selectedLayer);

        if (
          selectedLayer.value.feature.properties.id ==
          layer.feature.properties.id
        ) {
          return;
        }
      }

      layer.setStyle(defaultStyle);
    };

    const onEachFeature = (feature, layer) => {
      //console.log(feature, layer);
      //bind click
      layer.on({
        click: whenClicked,
        mouseover: whenMouseover,
        mouseout: whenMouseout,
      });
    };

    const setGeoJsonStyle = (e) => {
      return { color: "#808080", weight: 1 };
    };

    onMounted(getGeojson); // on `mounted` call `getUserRepositories`

    return {
      geojson,
      getGeojson,
      onEachFeature,
      setGeoJsonStyle,
      whenClicked,
      selectedLayer,
      hoveredLayer,
      geoJsonloaded,
    };
  },
};
</script>
<style>
#map {
  position: relative;
  width: 100%;
  height: 100%;
  left: 0%;
  top: 0%;
}
</style>