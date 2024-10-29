<template>
    <div class="custom-container">
        <div class="add-service-form">
            <form @submit.prevent="updateService">
                <label for="serviceName" class="my-4">Service Name:</label>
                <input v-model="serviceName" type="text" id="serviceName" required>
                <label for="serviceTime" class="my-4">Service Time:</label>
                <input v-model="serviceTime" type="text" id="serviceTime" required>
                <label for="serviceBaseprice" class="my-4">Service Base Price:</label>
                <input v-model="serviceBaseprice" type="text" id="serviceBaseprice" required>
                <div class="row mt-4">
                    <div class="col-6 d-flex align-items-center justify-content-center">
                        <button class="btn btn-secondary" type="submit">Update</button>
                    </div>
                    <div class="col-6 d-flex align-items-center justify-content-center">
                        <router-link class="btn btn-danger" to="/admin-home">Cancel</router-link>
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
            serviceBaseprice: 0.00,
            serviceTime: 1
        };
    },
    mounted() {
        this.fetchService();
    },
    methods: {
        async fetchService() {
            const serviceId = this.$route.params.serviceId;
            const apiUrl = `http://127.0.0.1:5000/get-service/${serviceId}`;

            try {
                const response = await fetch(apiUrl, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`
                    }
                });
                const data = await response.json();

                if (response.ok) {
                    this.serviceName = data.name;
                    this.serviceTime = data.time;
                    this.serviceBaseprice = data.baseprice;
                } else {
                    console.error('Failed to fetch service data');
                }
            } catch (error) {
                console.error('Error fetching service data:', error);
            }
        },
        updateService() {
            const serviceId = this.$route.params.serviceId;
            const putData = {
                name: this.serviceName,
                time : this.serviceTime,
                baseprice: this.serviceBaseprice
            };
            const token = sessionStorage.getItem("token");

            axios.put(`http://127.0.0.1:5000/update-service/${serviceId}`, putData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
                .then(response => {
                    console.log(response.data.message);
                    this.$router.push('/admin-home');
                })
                .catch(error => {
                    console.error('Error updating service:', error.response ? error.response.data : error.message);
                });
        },
    },
};
</script>

<style scoped>
.custom-container {
    width: 400px;
    color: white;
    position: fixed;
    text-align: center;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: rgba(0, 0, 0, 0.199);
    padding: 20px;
    border-radius: 1rem;
}
</style>
