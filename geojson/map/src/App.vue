<template>
  <div class="container-fluid vh-100 p-0">
    <div class="row vh-100 g-0">
      <!--
      <div class="col-9">
        <Map />
      </div>

      <div class="col-2 px-2">
        <HelloWorld msg="Hello Vue 3 + Vite" />
      </div>
      -->
      <Map />

      <div class="col-5">
        <h3>Info</h3>
        <div>
          Landkreis:
          <!--
          <span> {{ landkreisName }}</span>
          <div v-show="landkreisId" id="chart1"></div>
          -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
//import HelloWorld from "./components/HelloWorld.vue";
import Map from "./components/Map.vue";

// This starter template is using Vue 3 experimental <script setup> SFCs
// Check out https://github.com/vuejs/rfcs/blob/script-setup-2/active-rfcs/0000-script-setup.md
</script>
<script>
import { useStore } from "vuex";

export default {
  components: {},

  setup(props) {
    const store = useStore();
  },
};
</script>
<style>
#app {
}
</style>