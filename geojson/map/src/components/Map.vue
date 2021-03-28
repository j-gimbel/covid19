<template>
  <l-map :zoom="7" :center="[51.4, 10.4]">
    <l-geo-json
      v-if="geoJsonloaded"
      :geojson="geojson"
      :options="geojsonOptions"
    />
    <l-tile-layer
      url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
    ></l-tile-layer>
  </l-map>
</template>
<script>
import { useStore } from "vuex";
import { ref, onMounted, watch, computed, toRefs } from "vue";
import { LMap, LTileLayer, LGeoJson } from "@vue-leaflet/vue-leaflet";

// import { Plotly } from "vue-plotly";

//import Plotly from "plotly.js";
//var Plotly = require("plotly.js-dist");
import "leaflet/dist/leaflet.css";
export default {
  components: {
    LMap,
    LTileLayer,
    LGeoJson,
    Plotly,
  },

  setup(props) {
    const store = useStore();

    let url = "http://j-gimbel.ddns.net:8000"; // "http://localhost:8000";

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

    var selectedLayer = null;
    var hoveredLayer = null;
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
      fetch(myRequest, myInit)
        .then((response) => response.json())
        .then(function (geojson_data) {
          //console.log(geojson_data);
          geojson.value = geojson_data;
          geoJsonloaded.value = true;
        });
    };

    const whenClicked = (e) => {
      console.log("whenClicked", e);
      var layer = e.target;

      if (selectedLayer != null) {
        selectedLayer.setStyle(defaultStyle);
        if (
          selectedLayer.feature.properties.id == layer.feature.properties.id
        ) {
          selectedLayer = null;

          //landkreisId.value = null;
          store.commit("map/setLKID", null);
          return;
        }
      }
      selectedLayer = layer;
      store.dispatch("map/loadLKData", layer.feature.properties.id);
      store.dispatch("map/loadLKDataDetails", layer.feature.properties.id);
      layer.setStyle(selectedStyle);
    };

    const whenMouseover = (e) => {
      var layer = e.target;
      hoveredLayer = layer;
      // this is just to not change the style if the user hover the selected layer
      if (selectedLayer != null) {
        if (
          selectedLayer.feature.properties.id == layer.feature.properties.id
        ) {
          return;
        }
      }
      store.commit(
        "map/setHoveredLKName",
        hoveredLayer.feature.properties.name
      );

      layer.setStyle(hoverStyle);
    };

    const whenMouseout = (e) => {
      var layer = e.target;
      // this is just to not change the style if the user hover the selected layer
      if (selectedLayer != null) {
        if (
          selectedLayer.feature.properties.id == layer.feature.properties.id
        ) {
          return;
        }
      }
      layer.setStyle(defaultStyle);
    };

    const onEachFeature = (feature, layer) => {
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
      geoJsonloaded,

      geojsonOptions: {
        onEachFeature: onEachFeature,
        style: setGeoJsonStyle,
      },
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