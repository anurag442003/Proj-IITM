<template>
    <div class="borrow-book-container">
        <h2>Borrow Book</h2>
        <form @submit.prevent="submitForm">
            <div class="form-group">
                <label for="bookId">Book ID</label>
                <input v-model.number="bookId" type="number" class="form-control" id="bookId" required>
            </div>
            <button type="submit" class="btn btn-primary">Borrow Book</button>
        </form>
    </div>
</template>
  
<script>
export default {
    data() {
        return {
            bookId: null,
        };
    },
    methods: {
        async submitForm() {
            try {
                const response = await this.$axios.post(`/borrow/${this.bookId}`);
                console.log(response.data);
                this.bookId = null;
            } catch (error) {
                console.error(error.response.data);
            }
        },
    },
};
</script>
  
<style scoped>
.borrow-book-container {
    max-width: 400px;
    margin: auto;
    padding: 20px;
    margin-top: 50px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 5px;
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
