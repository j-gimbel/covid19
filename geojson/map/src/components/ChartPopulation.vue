<template>
  <div id="chart1"></div>
</template>
<script>
import { useStore } from "vuex";
import { ref, computed, watch, onMounted } from "vue";

export default {
  components: {},

  setup() {
    const store = useStore();
    //const LKData = computed(() => store.state.map.LKData);

    /*watch(store.state.map.LKData, (newValue, oldValue) => {
      console.log("watch LKData", newValue);
    });*/

    //
    //const LKName = ref("A");

    const LKData = computed(() => store.state.map.LKData);

    watch(LKData, (newValue, oldValue) => {
      console.log("watch", newValue, oldValue);

      //brTotal = store.state.map.BRData.Einwohner;
      let brData = store.state.map.BRData;

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
              (brData.Einwohner_AG_A00_A04 / brData.Einwohner) * 100,
              (brData.Einwohner_AG_A05_A14 / brData.Einwohner) * 100,
              (brData.Einwohner_AG_A15_A34 / brData.Einwohner) * 100,
              (brData.Einwohner_AG_A35_A59 / brData.Einwohner) * 100,
              (brData.Einwohner_AG_A60_A79 / brData.Einwohner) * 100,
              (brData.Einwohner_AG_A80Plus / brData.Einwohner) * 100,
            ],
            name: "Germany",
            type: "bar",
          },
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
              (newValue.Einwohner_AG_A00_A04 / newValue.Einwohner) * 100,
              (newValue.Einwohner_AG_A05_A14 / newValue.Einwohner) * 100,
              (newValue.Einwohner_AG_A15_A34 / newValue.Einwohner) * 100,
              (newValue.Einwohner_AG_A35_A59 / newValue.Einwohner) * 100,
              (newValue.Einwohner_AG_A60_A79 / newValue.Einwohner) * 100,
              (newValue.Einwohner_AG_A80Plus / newValue.Einwohner) * 100,
            ],
            name: store.state.map.LKName,
            type: "bar",
          },
        ],
        { title: "Age groups distribution" },
        { responsive: true }
      );
    });

    const loadGlobalData = () => {
      console.log("loadGlobalData");
      store.dispatch("map/loadBRData");
    };

    onMounted(loadGlobalData);
    return {
      //LKData: computed(() => store.state.map.LKData),
      LKData,
    };
  },
};
</script>
<style>
</style>