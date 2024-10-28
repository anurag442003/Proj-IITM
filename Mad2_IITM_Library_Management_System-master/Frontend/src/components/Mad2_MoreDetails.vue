<template>
    <div class="custom-container">
        <h2>Details</h2>
        <p><strong>UserId:</strong> {{ userDetails.userid }}</p>
        <p><strong>Username:</strong> {{ userDetails.username }}</p>
        <p><strong>Phone Number:</strong> {{ userDetails.phno }}</p>
        <p><strong>Pincode:</strong> {{ userDetails.pin }}</p>
        <p><strong>Section Name:</strong> {{ userDetails.sectionName }}</p>
        <div class="d-flex">
            <router-link :to="{ name: 'Approve'}" class="btn btn-primary mx-4"><i class="fa-solid fa-angles-left"></i></router-link>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            userDetails: {},
            contentId : null,
            userId: null
        }
    },
    methods: {
        async viewDetails() {
            try {
                this.contentId = this.$route.params.contentId;
                this.userId = this.$route.params.userId;

                const response = await this.$axios.get(`http://127.0.0.1:5000/more_details/${this.contentId}/${this.userId}`, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`
                    }
                });

                this.userDetails = response.data;
                console.log(response.data)
            } catch (error) {
                console.error('Error fetching details:', error);
            }
        }
    },
    mounted() {
        this.viewDetails();
    }
}
</script>

<style scoped>
.custom-container {
    padding: 15px;
    margin: 70px auto;
    width: 40%;
    border-radius: 2rem;
    background-color: rgba(0, 0, 0, 0.315);
    color: white;
    display: flex;
    flex-direction: column;
    row-gap: 2rem;
    align-items: center;
    padding-top: 2rem;
}

.modal-content {
    background-color: #fefefe;
    margin: 10% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
}

.close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
}

.close:hover,
.close:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
}
</style>