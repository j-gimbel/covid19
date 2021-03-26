<template>
  <div class="col-7">
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
  </div>
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
    /*
    const landkreisId = ref(null);
    const landkreisName = ref(null);
    const chart1Data = ref({});
    

    const firstchartPlot = ref(true);

    // load new data when landkreisId changes

    const getLandKreisData = async () => {
      console.log("getLandKreisData", landkreisId.value);
      fetch(url + "/api/landkreis/" + landkreisId.value, {
        mode: "cors",
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          //landkreisName.value = data.name;
          chart1Data.value = data;
        });
    };
    watch(landkreisId, getLandKreisData);

    const updateChart1 = () => {
      var data = chart1Data.value;
      console.log(
        "updateChart1",
        chart1Data.value.Einwohner_AG_A00_A04,
        data.Einwohner_AG_A00_A04
      );

      if (firstchartPlot.value == true) {
        console.log("newPlot");
        window.Plotly.newPlot(
          document.getElementById("chart1"),
          [
            {
              x: [
                "AG 0-4",
                "AG 5-14",
                "AG 15-34",
                "AG 35-59",
                "AG 60-79",
                "AG 80+",
              ],
              y: [
                data.Einwohner_AG_A00_A04,
                data.Einwohner_AG_A05_A14,
                data.Einwohner_AG_A15_A34,
                data.Einwohner_AG_A35_A59,
                data.Einwohner_AG_A60_A79,
                data.Einwohner_AG_A80Plus,
              ],
              type: "bar",
            },
          ],
          { title: "Age groups distribution" },
          { responsive: true }
        );
        firstchartPlot.value = false;
      } else {
        console.log("react");
        window.Plotly.react(
          document.getElementById("chart1"),
          [
            {
              x: [
                "AG 0-4",
                "AG 5-14",
                "AG 15-34",
                "AG 35-59",
                "AG 60-79",
                "AG 80+",
              ],
              y: [
                data.Einwohner_AG_A00_A04,
                data.Einwohner_AG_A05_A14,
                data.Einwohner_AG_A15_A34,
                data.Einwohner_AG_A35_A59,
                data.Einwohner_AG_A60_A79,
                data.Einwohner_AG_A80Plus,
              ],
              type: "bar",
            },
          ],
          { title: "Age groups distribution" },
          { responsive: true }
        );
      }
    };

    watch(chart1Data, updateChart1);
    */

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
          console.log(geojson_data);
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
      //landkreisId.value = layer.feature.properties.id;
      store.commit("map/setLKID", layer.feature.properties.id);
      store.dispatch("map/loadLKData", layer.feature.properties.id);

      console.log(selectedLayer);
      layer.setStyle(selectedStyle);
    };

    const whenMouseover = (e) => {
      console.log("whenMouseover", e);
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
      //landkreisName.value = hoveredLayer.feature.properties.name;
      layer.setStyle(hoverStyle);
    };

    const whenMouseout = (e) => {
      //console.log("whenMouseout", e);
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