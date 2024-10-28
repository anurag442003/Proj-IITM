<template>

    <div class="custom-container">
    <h2>User Details</h2>
    <p><strong>User ID:</strong> {{ userDetails.id }}</p>
    <p><strong>First Name:</strong> {{ userDetails.fname }}</p>
    <p><strong>Last Name:</strong> {{ userDetails.lname }}</p>
    <p><strong>Username:</strong> {{ userDetails.uname }}</p>
    <p><strong>Phone Number:</strong> {{ userDetails.phNumber }}</p>
    <p><strong>Email:</strong> {{ userDetails.email }}</p>
    <p><strong>Pincode:</strong> {{ userDetails.pin }}</p>
    <p><strong>City:</strong> {{ userDetails.city }}</p>
    <p><strong>State:</strong> {{ userDetails.state }}</p>
    <p><strong>Role:</strong> {{ userDetails.role }}</p>

    <!-- Conditionally display content details if the user's role is "librarian" -->
    <div v-if="userDetails.role === 'LIBRARIAN'">
        <h2>Content Details</h2>
        <p><strong>Service Type:</strong> {{  userDetails.section }}</p>
        <p><strong>Description:</strong> {{  userDetails.author }}</p>
        <p><strong>Additional Charges:</strong> {{  userDetails.price }} Rs.</p>
        <p><strong>Experience:</strong> {{  userDetails.no_of_pages }} years</p>
        <p><strong>Date of birth:</strong> {{  userDetails.publish_year }}</p>

        <!-- Display image if available -->
        <div v-if=" userDetails.image">
            <img :src="getDecodedImage(userDetails)" alt="Content Image" />
        </div>

        <!-- Display PDF link if available -->
        <div v-if=" userDetails.pdf_file">
            <button class="btn btn-primary btn-sm" @click="openContent(userDetails.cid)">
                <i class="fa-brands fa-readme"></i> {{ userDetails.pdf_file_name }}
            </button>
        </div>
    </div>

    <div class="d-flex">
        <router-link :to="{ name: 'Activate'}" class="btn btn-primary mx-4"><i class="fa-solid fa-angles-left"></i></router-link>
    </div>
</div>
</template>

<script>
export default {
    data() {
        return {
            userDetails: {},
            userId: null
        }
    },
    props: {
        decodedImage: {
            type: String,
            required: true,
        },
    },
    methods: {
        async viewDetails() {
            try {
                this.userId = this.$route.params.userId;

                const response = await this.$axios.get(`http://127.0.0.1:5000/all_details/${this.userId}`, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`
                    }
                });

                this.userDetails = response.data;
                console.log(response.data)
            } catch (error) {
                console.error('Error fetching details:', error);
            }
        },
        async openContent(contentId) {
            try {
                const response = await fetch(`http://127.0.0.1:5000/get_pdf/${contentId}`, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                    },
                });
                const blob = await response.blob();

                const pdfUrl = URL.createObjectURL(blob);

                window.open(pdfUrl, '_blank');
            } catch (error) {
                console.error('Error opening content:', error);
            }
        },
        handleImageError(event) {
            console.error("Error loading image:", event);
        },
        getDecodedImage(content) {
            return `data:image/${content.imageType};base64,${content.image}`;
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