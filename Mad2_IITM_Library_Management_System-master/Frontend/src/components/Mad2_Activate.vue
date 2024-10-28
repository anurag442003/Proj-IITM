<template>
    <div class="custom-container">
      <table class="table table-striped table-bordered">
            <thead class="thead-dark">
                <tr>
            <!-- <th>User ID</th> -->
            <th>ID</th>
            <th>Name</th>
            <th>Role</th>
            <th>Details</th>

            <th>Active</th>
            
          </tr>
        </thead>
        <tbody>
          <tr v-for="active in activeRequests" :key="active.id">
            <td>{{ active.id }}</td>
            <td>{{ active.fname }}</td>
            <td>{{ active.role }}</td>
            <td>
              <router-link :to="{ name: 'AllDetails', params: { userId: active.id } }"
                class="btn btn-action btn-warning">
                <i class="fa-solid fa-eye"></i>
              </router-link>
            </td>
            <td>
            <label class="switch">
              <input type="checkbox" :checked="active.status" @change="toggleStatus(active)">
              <span class="slider"></span>
            </label>
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
      activeRequests: [],
    };
  },
  methods: {
    async toggleStatus(approval) {
      if (typeof approval === 'object' && 'status' in approval) 
      {
        if (approval.status) {
          await this.deactivate(approval);
        } else {
          await this.activate(approval);
        }
        // Toggle the status after action completion
        approval.status = !approval.status;
      }
    },
    async activate(activate) {
      try {
        await this.$axios.post(
          `http://127.0.0.1:5000/activate/${activate.id}`,
          null,
          {
            headers: {
              Authorization: `Bearer ${sessionStorage.getItem("token")}`,
            },
          }
        );
        console.log("Activated successfully");
      } catch (error) {
        console.error("Error activating request:", error);
      }
    },
    async deactivate(activate) {
      try {
        await this.$axios.post(
          `http://127.0.0.1:5000/deactivate/${activate.id}`,
          null,
          {
            headers: {
              Authorization: `Bearer ${sessionStorage.getItem("token")}`,
            },
          }
        );
        console.log("Deactivated successfully");
      } catch (error) {
        console.error("Error deactivating request:", error);
      }
    },
    async fetchActiveRequests() {
        console.log("fetching active");
        try {
          const response = await this.$axios.get("http://127.0.0.1:5000/fetch_activate", {
            headers: {
              Authorization: `Bearer ${sessionStorage.getItem("token")}`
            }
          });
          this.activeRequests = response.data;
          console.log(this.activeRequests);
        } catch (error) {
          
          console.error("Error fetching approve requests:", error);
        }
      }
    },
    mounted() {
      this.fetchActiveRequests();
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

  .switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 20px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  border-radius: 50%;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
}

input:checked + .slider {
  background-color: #4caf50;
}

input:checked + .slider:before {
  transform: translateX(20px);
}
  </style>
  