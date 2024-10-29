<template>
    <div class="custom-container">
        <div class="data d-flex justify-professional-between">
            <h2 style="color: black;">Ongoing Services: {{ currentUsersCount }}</h2>
            <h2 style="color: black;">Total Services rendered: {{ totalUsersCount }}</h2>
        </div>
        <table class="table table-striped table-bordered">
            <thead class="thead-dark">
                <tr> 
                    <th>Professional ID</th>
                    <th>Title</th>
                    <th>Username</th>
                    <th>Service Name</th>
                    <th>Render Date</th>
                    <th>Returned</th>
                    <th>Return Date</th>
                    <th>Revoke</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, index) in tableData" :key="index">
                    <td>{{ row.professional_id }}</td>
                    <td>{{ row.title }}</td>
                    <td>{{ row.uname }}</td>
                    <td>{{ row.service_name }}</td>
                    <td>{{ row.render_date }}</td>
                    <td>{{ row.returned }}</td>
                    <td>{{ row.last_return_date }}</td>
                    <td><button class="btn btn-danger btn-sm"
                            @click="revokeAccess(row.professional_id, row.user_id)">Revoke</button></td>
                </tr>
            </tbody>
        </table>
        <BottomHome />
    </div>
</template>

<script>
import axios from 'axios';
import BottomHome from './Mad2_BottomHome.vue';

export default {
    components: {
        BottomHome,
    },
    data() {
        return {
            professionalId: null,
            tableData: [],
            currentUsersCount: 0,
            totalUsersCount: 0,
        };
    },
    mounted() {
        this.fetchData();
        this.fetchCounts();
    },
    methods: {
        revokeAccess(professionalId, userId) {
            axios.post('http://127.0.0.1:5000/revoke-access', { professionalId, userId },{
                headers:{
                    Authorization: `Bearer ${sessionStorage.getItem('token')}`
                }
            })
                .then(response => {
                    this.fetchCounts()
                    this.fetchData()
                    console.log(response.data);
                })
                .catch(error => {
                    console.error(error);
                });
        },
        fetchData() {
            const professionalId = this.$route.params.professionalId;
            const apiUrl = `http://127.0.0.1:5000/activity-data/${professionalId}`;

            axios.get(apiUrl, {
                headers: {
                    Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                }
            })
                .then(response => {
                    this.tableData = response.data;
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        },
        fetchCounts() {
            const professionalId = this.$route.params.professionalId;

            axios.get(`http://127.0.0.1:5000/current-users-count/${professionalId}`, {
                headers: {
                    Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                }
            })
                .then(response => {
                    this.currentUsersCount = response.data.currentUsersCount;
                })
                .catch(error => {
                    console.error('Error fetching current users count:', error);
                });


            axios.get(`http://127.0.0.1:5000/total-users-count/${professionalId}`, {
                headers: {
                    Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                }
            })
                .then(response => {
                    this.totalUsersCount = response.data.totalUsersCount;
                })
                .catch(error => {
                    console.error('Error fetching total users count:', error);
                });


            
        },
    },
};
</script>

<style scoped>
.custom-container {
    margin: 20px;
    color: black;
}

.table {
    text-align: center;
    width: 100%;
    border-collapse: separate;
    border-radius: 1rem;
    overflow: hidden;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.table th,
.table td {
    padding: 12px;
    border: transparent;
}

.data {
    margin: auto;
    text-align: center;
    width: 80%;
    color: white;
}
</style>