<template>
    <div class="form-container">
        <h2>Add a New Book or Document</h2>
        <form @submit.prevent="handleSubmit">
            <div class="form-group">
                <label for="title">Title</label>
                <input v-model="title" type="text" class="form-control" id="title" required>
            </div>
            <div class="form-group">
                <label for="author">Author</label>
                <input v-model="author" type="text" class="form-control" id="author" required>
            </div>
            <div class="form-group">
                <label for="category">Category</label>
                <input v-model="category" type="text" class="form-control" id="category" required>
            </div>
            <div class="form-group">
                <label for="numberOfPages">Number of Pages</label>
                <input v-model="numberOfPages" type="number" class="form-control" id="numberOfPages" required>
            </div>
            <div class="form-group">
                <label for="publishYear">Publication Year</label>
                <input v-model="publishYear" type="number" class="form-control" id="publishYear" required>
            </div>
            <div class="form-group">
                <label for="quantityAvailable">Quantity in Stock</label>
                <input v-model="quantityAvailable" type="number" class="form-control" id="quantityAvailable" required>
            </div>
            <button type="submit" class="btn btn-primary">Add Book/Document</button>
        </form>
    </div>
</template>
  
<script>
export default {
    data() {
        return {
            title: '',
            author: '',
            category: '',
            numberOfPages: '',
            publishYear: '',
            quantityAvailable: '',
        };
    },
    methods: {
        async handleSubmit() {
            try {
                const response = await this.$axios.post('/add_books', {
                    title: this.title,
                    author: this.author,
                    category: this.category,
                    numberOfPages: this.numberOfPages,
                    publishYear: this.publishYear,
                    quantityAvailable: this.quantityAvailable,
                });

                console.log('Book added successfully:', response.data);
            } catch (error) {
                console.error('Error adding book:', error.response.data);
            }
        },
    },
};
</script>
  
<style scoped>
.form-container {
    max-width: 500px;
    margin: 50px auto;
    padding: 25px;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #333;
}

input {
    width: 100%;
    padding: 10px;
    font-size: 14px;
    border: 1px solid #ddd;
    border-radius: 5px;
    box-sizing: border-box;
}

button {
    width: 100%;
    padding: 10px;
    font-size: 16px;
    color: #fff;
    background-color: #007bff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

button:hover {
    background-color: #0056b3;
}
</style>
