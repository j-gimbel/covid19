<template>
  <div class="container-fluid vh-100 p-0">
    <div class="row vh-100 g-0">
      <div class="col-7">
        <Map />
      </div>
      <div class="col-5">
        <Info />
        <ChartPopulation />
      </div>
    </div>
  </div>
</template>

<script setup>
//import HelloWorld from "./components/HelloWorld.vue";
import Map from "./components/Map.vue";
import Info from "./components/Info.vue";
import ChartPopulation from "./components/ChartPopulation.vue";
import { computed } from "vue";
import { ref } from "vue";
// This starter template is using Vue 3 experimental <script setup> SFCs
// Check out https://github.com/vuejs/rfcs/blob/script-setup-2/active-rfcs/0000-script-setup.md
</script>
<!--
<script>
import { useStore } from "vuex";

export default {
  components: {},

  setup() {
    const store = useStore();
    //const LKName = computed(() => store.state.map.LKName);
    const LKName = ref("A");
    return {
      LKName,
    };
  },
};
</script>
-->
<style>
#app {
}
</style>