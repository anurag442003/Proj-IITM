<template>
    <div class="custom-container">
      <table class="table table-striped table-bordered">
            <thead class="thead-dark">
                <tr>
            <th>User ID</th>
            <th>Professional ID</th>
            <th>Actions</th>
            <th>Reject</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in issueRequests" :key="request.id">
            <td>{{ request.userId }}</td>
            <td>{{ request.professionalId }}</td>
            <td>
              <button class="btn btn-action btn-success" @click="acceptRequest(request.professionalId, request.userId)">
                Accept
              </button>
            </td>
            <td>
              <button class="btn btn-action btn-danger" @click="rejectRequest(request.professionalId, request.userId)">
                Reject
              </button>
            </td>
            <td>
              <router-link :to="{ name: 'DetailView', params: { professionalId: request.professionalId, userId: request.userId } }"
                class="btn btn-action btn-warning">
                <i class="fa-solid fa-eye"></i>
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        issueRequests: []
      };
    },
    methods: {
      async acceptRequest(professionalId, userId) {
        try {
          await this.$axios.post(
            `http://127.0.0.1:5000/accept_request/${professionalId}/${userId}`,
            null,
            {
              headers: {
                Authorization: `Bearer ${sessionStorage.getItem("token")}`
              }
            }
          );
          this.fetchIssueRequests();
          console.log("Issue Request Accepted");
        } catch (error) {
          console.error("Error accepting professional request:", error);
        }
      },
      async rejectRequest(professionalId, userId) {
        try {
          await this.$axios.post(
            `http://127.0.0.1:5000/reject_request/${professionalId}/${userId}`,
            null,
            {
              headers: {
                Authorization: `Bearer ${sessionStorage.getItem("token")}`
              }
            }
          );
          this.fetchIssueRequests();
          console.log("Issue Request Rejected");
        } catch (error) {
          console.error("Error rejecting professional request:", error);
        }
      },
      async fetchIssueRequests() {
        try {
          const response = await this.$axios.get("http://127.0.0.1:5000/fetch_requests", {
            headers: {
              Authorization: `Bearer ${sessionStorage.getItem("token")}`
            }
          });
          this.issueRequests = response.data;
          console.log(this.issueRequests);
        } catch (error) {
          console.error("Error fetching issue requests:", error);
        }
      }
    },
    mounted() {
      this.fetchIssueRequests();
    }
  };
  </script>
  
  <style scoped>
  .custom-container {
    padding: 10px;
    background-color: rgba(0, 0, 0, 0.1);
    border-radius: 10px;
    margin: 20px auto;
    width: 80%;
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
  .btn-action {
    padding: 8px 16px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
  }
  
  .btn-success {
    background-color: #28a745;
    color: white;
  }
  
  .btn-danger {
    background-color: #dc3545;
    color: white;
  }
  
  .btn-warning {
    background-color: #ffc107;
    color: #333;
  }
  
  .fa-eye {
    font-size: 16px;
    margin-right: 5px;
  }
  </style>
  