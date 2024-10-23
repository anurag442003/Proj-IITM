<template>
    <div class="custom-container">
        <h2>Transaction Logs</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>User ID</th>
                    <th>Action</th>
                    <th>Timestamp</th>
                    <th>Content ID</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="log in transactionLogs" :key="log.id">
                    <td>{{ log.id }}</td>
                    <td>{{ log.user_id }}</td>
                    <td>{{ log.action }}</td>
                    <td>{{ formatDate(log.timestamp) }}</td>
                    <td>{{ log.content_id }}</td>
                </tr>
            </tbody>
        </table>
        <div>
            <button @click="download_csv">Download TransactionLogs</button>
            <span v-if="iswaiting">  Wating...</span>
        </div>
    </div>
</template>

<script>
import { format } from 'date-fns';

export default {
    data() {
        return {
            iswaiting:false,
            transactionLogs: [],
        };
    },
    mounted() {

        this.fetchTransactionLogs();
    },
    methods: {
        formatDate(dateString) {
            return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss');
        },
        async fetchTransactionLogs() {
            try {
                const response = await this.$axios.get('http://127.0.0.1:5000/transaction_logs', {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`
                    }
                });

                this.transactionLogs = response.data.transaction_logs;
            } catch (error) {
                console.error('Error fetching transaction logs:', error);
            }
        },
        async download_csv() {
            try {
                this.isWaiting = true;
                const response = await this.$axios.get('http://127.0.0.1:5000/download-csv', {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`
                    }
                });

                const { task_id } = response.data;
                this.pollTask(task_id);
            } catch (error) {
                console.error('Error requesting CSV generation:', error);
                this.isWaiting = false;
            }
        },
        async pollTask(task_id) {
            try {
                const response = await this.$axios.get(`http://127.0.0.1:5000/get-csv/${task_id}`, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`
                    },
                    responseType: 'blob' 
                });

                if (response.status === 202) {
                    setTimeout(() => {
                        this.pollTask(task_id);
                    }, 2000);
                } else {
                    this.isWaiting = false;
                    if (response.status === 200) {
                        const url = window.URL.createObjectURL(new Blob([response.data]));
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', 'transaction_logs.csv');
                        document.body.appendChild(link);
                        link.click();
                    } else {
                        console.error('Error generating CSV:', response.data);
                    }
                }
            } catch (error) {
                console.error('Error polling CSV task:', error);
                this.isWaiting = false;
            }
        }
    },




};
</script>

<style scoped>
.custom-container {
    color: white;
    margin: 50px auto;
    width: 80%;
}

.table {
    text-align: center;
    width: 100%;
    margin-bottom: 1rem;
    border-collapse: separate;
    border-spacing: 1rem;
}

th, td {
    background-color: rgba(0, 0, 0, 0.336);
    color: white;
}
span{
    color:brown;
}

td {
    background-color: rgba(0, 0, 0, 0.486);
}
</style>
