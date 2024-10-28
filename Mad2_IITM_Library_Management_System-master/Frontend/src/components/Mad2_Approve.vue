<template>
    <div class="custom-container">
      <table class="table table-striped table-bordered">
            <thead class="thead-dark">
                <tr>
            <!-- <th>User ID</th> -->
            <th>ID</th>
            <th>Name</th>
            <th>ServiceType</th>
            <th>AdditionalCharges</th>

            <th>Accept</th>
            <th>Reject</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="approval in approveRequests" :key="approval.id">
            <td>{{ approval.id }}</td>
            <td>{{ approval.title }}</td>
            <td>{{ approval.section }}</td>
            <td>{{ approval.price }}</td>
            <td>
              <button class="btn btn-action btn-success" @click="acceptApproval(approval.id)">
                Accept
              </button>
            </td>
            <td>
              <button class="btn btn-action btn-danger" @click="rejectApproval(approval.id)">
                Reject
              </button>
            </td>
            <td>
              <router-link :to="{ name: 'MoreDetails', params: { contentId: approval.id, userId: approval.uploaded_by_id } }"
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
        approveRequests: []
      };
    },
    methods: {
      async acceptApproval(contentId) {
        console.log("trying to accept approval");
        try {
          await this.$axios.post(
            `http://127.0.0.1:5000/accept_approval/${contentId}`,
            null,
            {
              headers: {
                Authorization: `Bearer ${sessionStorage.getItem("token")}`
              }
            }
          );
          this.fetchApproveRequests();
          console.log("Approve Request Accepted");
        } catch (error) {

          console.error("Error accepting content request:", error);
        }
      },
      async rejectApproval(contentId) {
        try {
          await this.$axios.post(
            `http://127.0.0.1:5000/reject_approval/${contentId}`,
            null,
            {
              headers: {
                Authorization: `Bearer ${sessionStorage.getItem("token")}`
              }
            }
          );
          this.fetchApproveRequests();
          console.log("Issue Request Rejected");
        } catch (error) {
          console.error("Error rejecting content request:", error);
        }
      },
      async fetchApproveRequests() {
        console.log("fetching approve");
        try {
          const response = await this.$axios.get("http://127.0.0.1:5000/fetch_approvals", {
            headers: {
              Authorization: `Bearer ${sessionStorage.getItem("token")}`
            }
          });
          this.approveRequests = response.data;
          console.log(this.approveRequests);
        } catch (error) {
          console.error("Error fetching approve requests:", error);
        }
      }
    },
    mounted() {
      this.fetchApproveRequests();
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
  