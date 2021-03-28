<template>
  <div id="chart2"></div>
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

    const LKDataDetails = computed(() => store.state.map.LKDataDetails);

    watch(LKDataDetails, (newValue, oldValue) => {
      console.log("watch LKDataDetails", newValue, oldValue);

      //brTotal = store.state.map.BRData.Einwohner;
      let data = store.state.map.LKDataDetails;
      console.log(data);

      window.Plotly.newPlot(
        document.getElementById("chart2"),
        [
          {
            x: data.dates,
            y: data.incidences,
            name: "incidences",
          },
        ],
        { title: "7 Day avg. incidence" },
        { responsive: true }
      );
    });

    /*const loadGlobalData = () => {
      console.log("loadGlobalData");
      store.dispatch("map/loadBRData");
    };

    onMounted(loadGlobalData);*/
    return {
      //LKData: computed(() => store.state.map.LKData),
      LKDataDetails,
    };
  },
};
</script>
<style>
</style>