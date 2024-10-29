<template>
    <div class="custom-container">
        <AlertTop v-if="professional.showAlert" :message="professional.alertMessage" type="error"
            @close="professional.showAlert = false"></AlertTop>
        <h2><b>Upload New Professional</b></h2>
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
                <div class="col-6">
                    <div class="form-group">
                        <label for="prof_desc">Author(s)</label>
                        <input v-model="professional.prof_desc" type="text" class="form-control" id="prof_desc" required>
                    </div>
                </div>
                <div class="col-4">
                    <div class="form-group">
                        <label for="publishYear">Publish Year</label>
                        <select v-model="professional.date_of_birth" class="form-control" id="publishYear" required>
                            <option disabled value="">Select year</option>
                            <option v-for="year in range(1900, 2025)" :key="year">{{ year }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-2">
                    <div class="form-group">
                        <label for="price">Price (in Rs.)</label>
                        <input v-model="professional.price" type="number" class="form-control" id="price" required>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-8 d-flex align-items-center justify-professional-center px-4 mx-4">
                    <button type="submit" class="btn btn-primary">Upload</button>
                </div>
                <div class="col-3 d-flex align-items-center justify-professional-center">
                    <router-link class="btn btn-danger" to="/professionals-home">Cancel</router-link>
                </div>
            </div>
        </form>
    </div>
</template>

<script>
import axios from 'axios';
import AlertTop from '../components/Mad2_AlertTop.vue';

export default {
    components: {
        AlertTop
    },
    data() {
        return {
            professional: {
                title: "",
                prof_desc: "",
                number_of_pages: 0,
                date_of_birth: 0,
                price: 0,
                image: null,
                pdf: null,
                showAlert: false,
                alertMessage: ''
            }
        };
    },
    methods: {
        range(start, end) {
            return Array.from({ length: end - start + 1 }, (_, index) => start + index);
        },
        handlePdfChange() {
            const file = this.$refs.pdfInput.files[0];
            this.professional.pdf = file;
        },
        getUserIdFromToken() {
            const token = sessionStorage.getItem('token');
            const user = this.$jwtDecode(token);
            const userId = user.id;
            return userId;
        },
        handleImageChange() {
            const file = this.$refs.imageInput.files[0];
            this.professional.image = file;
        },
        submitForm() {
            if (!this.professional.image || !this.professional.pdf) {
                this.professional.alertMessage = 'Both image and PDF file are required.';
                this.professional.showAlert = true;
                setTimeout(() => {
                    this.professional.showAlert = false;
                }, 3000);
                return;
            }

            const formData = new FormData();
            formData.append('title', this.professional.title);
            formData.append('prof_desc', this.professional.prof_desc);
            formData.append('number_of_pages', this.professional.number_of_pages);
            formData.append('date_of_birth', this.professional.date_of_birth);
            formData.append('image', this.professional.image);
            formData.append('price', this.professional.price);
            formData.append('pdf', this.professional.pdf, this.professional.pdf.name);

            const serviceId = this.$route.params.serviceId;
            const userId = this.getUserIdFromToken();
            const token = sessionStorage.getItem('token');

            axios.post(`http://127.0.0.1:5000/add-professional/${serviceId}/${userId}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${token}`
                },
            })
                .then(response => {
                    console.log(response.data);
                    this.professional = {
                        title: "",
                        prof_desc: "",
                        number_of_pages: 0,
                        price: 0,
                        date_of_birth: 0,
                        image: null,
                    };

                    this.$refs.imageInput.value = null;
                    this.$refs.pdfInput.value = null;
                })
                .catch(error => {
                    this.professional.showAlert = true;
                    console.error("Error:", error);
                });
        }
    }
};
</script>

<style scoped>
.custom-container {
    color: #fff;
    background-color: #00000038;
    max-width: 900px;
    margin: 120px auto;
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
