<template>
  <div id="chart1"></div>
</template>
<script>
import { useStore } from "vuex";
import { ref, computed, watch } from "vue";

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
              newValue.Einwohner_AG_A00_A04,
              newValue.Einwohner_AG_A05_A14,
              newValue.Einwohner_AG_A15_A34,
              newValue.Einwohner_AG_A35_A59,
              newValue.Einwohner_AG_A60_A79,
              newValue.Einwohner_AG_A80Plus,
            ],
            type: "bar",
          },
        ],
        { title: "Age groups distribution" },
        { responsive: true }
      );
    });
    return {
      //LKData: computed(() => store.state.map.LKData),
      LKData,
    };
  },
};
</script>
<style>
</style>