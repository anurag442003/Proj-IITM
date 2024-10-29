<template>
    <div class="render-prof-container">
        <h2>Render Prof</h2>
        <form @submit.prevent="submitForm">
            <div class="form-group">
                <label for="profId">Prof ID</label>
                <input v-model.number="profId" type="number" class="form-control" id="profId" required>
            </div>
            <button type="submit" class="btn btn-primary">Render Prof</button>
        </form>
    </div>
</template>
  
<script>
export default {
    data() {
        return {
            profId: null,
        };
    },
    methods: {
        async submitForm() {
            try {
                const response = await this.$axios.post(`/render/${this.profId}`);
                console.log(response.data);
                this.profId = null;
            } catch (error) {
                console.error(error.response.data);
            }
        },
    },
};
</script>
  
<style scoped>
.render-prof-container {
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
