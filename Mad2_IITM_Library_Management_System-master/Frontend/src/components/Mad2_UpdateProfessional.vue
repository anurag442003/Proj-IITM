<template>
  <div class="container">
    <h2><b>Update Professional</b></h2>
    <form @submit.prevent="submitForm">
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="image">Image</label>
            <input type="file" ref="imageInput" @change="handleImageChange">
          </div>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <label for="pdfFile">PDF File</label>
            <input type="file" ref="pdfInput" @change="handlePdfChange">
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <div class="form-group">
            <label for="title">Title</label>
            <input v-model="professional.title" type="text" class="form-control" id="title" required>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-7">
          <div class="form-group">
            <label for="prof_desc">Author(s)</label>
            <input v-model="professional.prof_desc" type="text" class="form-control" id="prof_desc" required>
          </div>
        </div>
        <div class="col-md-3">
          <div class="form-group">
            <label for="publishYear">Publish Year</label>
            <input v-model="professional.date_of_birth" type="number" class="form-control" id="publishYear" required>
          </div>
        </div>
        <div class="col-md-2">
          <div class="form-group">
            <label for="price">Price (in Rs.)</label>
            <input v-model="professional.price" type="number" class="form-control" id="price" required>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-8 d-flex align-items-center justify-professional-center px-4 mx-4">
          <button type="submit" class="btn btn-primary">Update</button>
        </div>
        <div class="col-3 d-flex align-items-center justify-professional-center">
          <router-link class="btn btn-danger" to="/admin-home">Cancel</router-link>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      professional: {
        title: '',
        prof_desc: '',
        number_of_pages: 0,
        date_of_birth: 0,
        price: 0,
        image: null,
        pdf: null,
        pdf_file_name: null
      },
      existingService: '',
      oldImage: null,
      oldPdf: null
    };
  },
  mounted() {
    const professionalId = this.$route.params.professionalId;
    if (professionalId) {
      this.fetchProfessionalDetails(professionalId);
    }
  },
  methods: {
    fetchProfessionalDetails(professionalId) {
      const token = sessionStorage.getItem('token');

      axios.get(`http://127.0.0.1:5000/fetch-professional-details/${professionalId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then(response => {
          const professionalDetails = response.data;
          this.professional = {
            image: professionalDetails.image,
            title: professionalDetails.title,
            prof_desc: professionalDetails.prof_desc,
            date_of_birth: professionalDetails.date_of_birth,
            price: professionalDetails.price,
            pdf: professionalDetails.pdf,
            pdf_file_name: professionalDetails.pdf_file_name,
          };
          this.existingService = professionalDetails.service;
          this.oldImage = professionalDetails.image;
          this.oldPdf = professionalDetails.pdf;
        })
        .catch(error => {
          console.error('Error fetching professional details:', error);
        });
    },
    getUserIdFromToken() {
      const token = sessionStorage.getItem('token');
      const user = this.$jwtDecode(token);
      const userId = user.id;
      return userId;
    },
    handlePdfChange() {
      const file = this.$refs.pdfInput.files[0];
      this.professional.pdf = file;
    },
    handleImageChange() {
      const file = this.$refs.imageInput.files[0];
      this.professional.image = file;
    },
    submitForm() {
      const token = sessionStorage.getItem('token');
      const professionalId = this.$route.params.professionalId;

      const userId = this.getUserIdFromToken();

      const formData = new FormData();
      formData.append('title', this.professional.title);
      formData.append('prof_desc', this.professional.prof_desc);
      formData.append('number_of_pages', this.professional.number_of_pages);
      formData.append('date_of_birth', this.professional.date_of_birth);
      formData.append('price', this.professional.price);

      if (!this.professional.image && this.oldImage) {
        formData.append('image', this.oldImage);
      } else if (this.professional.image) {
        formData.append('image', this.professional.image);
      }

      if (!this.professional.pdf && this.oldPdf) {
        formData.append('pdf', this.oldPdf);
      } else if (this.professional.pdf) {
        formData.append('pdf', this.professional.pdf);
      }

      axios.post(`http://127.0.0.1:5000/update-professional/${professionalId}/${userId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      })
        .then(response => {
          console.log(response.data);
          this.$router.push('/professionals-home');
        })
        .catch(error => {
          console.error('Error:', error);
        });
    },
  },
};
</script>

<style scoped>
.container {
  color: #fff;
  background-color: #00000038;
  max-width: 900px;
  margin: 100px auto;
  padding: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
}

label {
  width: 150px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  display: block;
  width: 100%;
  padding: 10px;
  font-size: 16px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
