<template>
  <div class="container-fluid vh-100">
    <div class="row vh-100">
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

      <div class="col-5">
        <h3>Info</h3>
        <div>
          Landkreis:

          <span> {{ landkreisName }}</span>
          <div v-show="landkreisId" id="chart1"></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
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

  mounted() {
    console.log("mounted");
    /*
    let plotlyScript = document.createElement("script");
    plotlyScript.setAttribute(
      "src",
      "https://cdn.plot.ly/plotly-latest.min.js"
    );
    document.head.appendChild(recaptchaScript);*/
    /*var TESTER = document.getElementById("tester");
    console.log(TESTER);
    window.Plotly.newPlot(
      TESTER,
      [
        {
          x: [1, 2, 3, 4, 5],
          y: [1, 2, 4, 8, 16],
        },
      ],
      {
        margin: { t: 0 },
      }
    );*/
  },

  setup(props) {
    let url = "http://localhost:8000";
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

    /*
    const selectedLayer = ref(null);
    const hoveredLayer = ref(null);
    */

    var selectedLayer = null;
    var hoveredLayer = null;

    const landkreisId = ref(null);
    const landkreisName = ref(null);
    const chart1Data = ref({});
    const geoJsonloaded = ref(false);
    const geojson = ref({});

    // load new data when landkreisId changes

    const getLandKreisData = async () => {
      console.log("getLandKreisData", landkreisId.value);
      fetch(
        "http://j-gimbel.ddns.net:8000/api/landkreis/" + landkreisId.value,
        {
          mode: "cors",
        }
      )
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
    };

    watch(chart1Data, updateChart1);

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

          window.Plotly.newPlot(
            document.getElementById("chart1"),
            //date
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
                y: [0, 0, 0, 0, 0, 0],
                type: "bar",
              },
            ],
            //layout
            { title: "Age groups distribution" },
            //config
            { responsive: true }
          );
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
          landkreisId.value = null;
          return;
        }
      }
      selectedLayer = layer;
      landkreisId.value = layer.feature.properties.id;
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
      landkreisName.value = hoveredLayer.feature.properties.name;
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
      // getGeojson,
      // onEachFeature,
      // setGeoJsonStyle,
      // whenClicked,
      // selectedLayer,
      // hoveredLayer,
      geoJsonloaded,
      landkreisName,
      landkreisId,
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