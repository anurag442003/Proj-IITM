<template>
  <div>
    <div class="add-section-form">
      <form @submit.prevent="addSection">
        <label for="sectionName" class="mx-3 mb-3">Section Name:</label>
        <input v-model="sectionName" type="text" id="sectionName" required>
        <div class="row">
          <div class="col-6 d-flex align-items-center justify-content-center">
            <button class="mt-4 btn btn-secondary" type="submit">Add Section</button>
          </div>
          <div class="col-6 d-flex align-items-center justify-content-center">
            <router-link class="btn btn-danger can" to="/librarian-home">Cancel</router-link>
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
      sectionName: '',
    };
  },
  methods: {
    addSection() {
      const postData = {
        name: this.sectionName,
      };
      const token = sessionStorage.getItem("token");
      
      axios.post('http://127.0.0.1:5000/section', postData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then(response => {
          console.log(response.data.message);
          this.$router.push('/librarian-home');
        })
        .catch(error => {
          console.error('Error adding section:', error.response ? error.response.data : error.message);
        });
    }
  },
};
</script>

<style scoped>
.add-section-form {
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
