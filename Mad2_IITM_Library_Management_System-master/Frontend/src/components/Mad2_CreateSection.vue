<template>
  <div>
    <div class="add-service-form">
      <form @submit.prevent="addService">
        <label for="serviceName" class="mx-3 mb-3">Service Name:</label>
        <input v-model="serviceName" type="text" id="serviceName" required>
        <label for="price" class="mx-3 mb-3">Base price in Rupees:</label>
        <input v-model="price" type="text" id="price" required>
        <label for="time" class="mx-3 mb-3">Service Time in hours:</label>
        <input v-model="time" type="text" id="time" required>
        <div class="row">
          <div class="col-6 d-flex align-items-center justify-content-center">
            <button class="mt-4 btn btn-secondary" type="submit">Add Service</button>
          </div>
          <div class="col-6 d-flex align-items-center justify-content-center">
            <router-link class="btn btn-danger can" to="/admin-home">Cancel</router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      serviceName: '',
      price:0.00,
      time:0
    };
  },
  methods: {
    addService() {
      const postData = {
        name: this.serviceName,
        price: this.price,
        time: this.time

      };
      const token = sessionStorage.getItem("token");
      
      axios.post('http://127.0.0.1:5000/service', postData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then(response => {
          console.log(response.data.message);
          this.$router.push('/admin-home');
        })
        .catch(error => {
          console.error('Error adding service:', error.response ? error.response.data : error.message);
        });
    }
  },
};
</script>

<style scoped>
.add-service-form {
  border-radius: 1rem;
  width: 400px;
  color: white;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.199);
  padding: 20px;
  text-align: center;
}

.can {
  margin-top: 23px;
}
</style>
