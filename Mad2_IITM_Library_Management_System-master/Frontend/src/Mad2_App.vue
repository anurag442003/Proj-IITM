<template>
  <div>
    <NavBar/>
    <router-view />
  </div>
</template>

<style>
body {
  background-attachment: fixed;
  background-position: center;
  background-repeat: no-repeat;
  background-color: whitesmoke;
}
</style>

<script>
import NavBar from './components/Mad2_NavBar.vue';

export default {
  components: {
    NavBar,
  },
  methods: {
    showAlert(message, type) {
      this.$Mad2_store.commit('showAlert', { message, type });
    },
  }
};
</script>
