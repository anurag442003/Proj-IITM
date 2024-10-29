<template>
  <div class="custom-container">
    <table class="table table-striped table-bordered">
      <thead class="thead-dark">
        <tr>
          <th>User ID</th>
          <th>User Name</th>
          <th>Rating</th>
          <th>Comment</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="review in reviews" :key="review.id">
          <td>{{ review.user_id }}</td>
          <td>{{ review.username }}</td>
          <td>{{ review.rating }}</td>
          <td>{{ review.comment }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      reviews: [],
      professionalId: null
    };
  },
  methods: {
    async fetchAllComments() {
      try {
        const response = await this.$axios.get(`http://127.0.0.1:5000/get_all_comments/${this.professionalId}`, {
          headers: {
            Authorization: `Bearer ${sessionStorage.getItem("token")}`
          }
        });
        this.reviews = response.data;
      } catch (error) {
        console.error("Error fetching comments:", error);
      }
    }
  },
  mounted() {
    this.professionalId = this.$route.params.professionalId;
    this.fetchAllComments();
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

.thead-dark th {
  background-color: #343a40;
  color: white;
}
</style>