<template>
  <div>
    <h3>Info</h3>
    <div>
      Landkreis:
      <span> {{ LKName }}</span>
      <!--
          <span> {{ landkreisName }}</span>
          <div v-show="landkreisId" id="chart1"></div>
          -->
    </div>
  </div>
</template>
<script>
import { useStore } from "vuex";
import { ref, computed } from "vue";

export default {
  components: {},

  setup() {
    const store = useStore();
    const LKName = computed(() => store.state.map.LKName);
    //const LKName = ref("A");
    return {
      LKName,
    };
  },
};
</script>
<style>
</style>