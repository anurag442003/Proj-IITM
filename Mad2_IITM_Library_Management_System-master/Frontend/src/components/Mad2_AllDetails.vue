<template>
    <div class="custom-container">
        <div class="details-card">
            <h2 class="card-title">User Details</h2>
            <div class="info-grid">
                <p><strong>User ID:</strong> {{ userDetails.id }}</p>
                <p><strong>First Name:</strong> {{ userDetails.fname }}</p>
                <p><strong>Last Name:</strong> {{ userDetails.lname }}</p>
                <p><strong>Username:</strong> {{ userDetails.uname }}</p>
                <p><strong>Phone:</strong> {{ userDetails.phNumber }}</p>
                <p><strong>Email:</strong> {{ userDetails.email }}</p>
                <p><strong>Pincode:</strong> {{ userDetails.pin }}</p>
                <p><strong>City:</strong> {{ userDetails.city }}</p>
                <p><strong>State:</strong> {{ userDetails.state }}</p>
            </div>
            <p class="role-tag"><strong>Role:</strong> {{ userDetails.role }}</p>
        </div>

        <!-- Librarian Details -->
        <div v-if="userDetails.role === 'LIBRARIAN'" class="details-card">
            <h2 class="card-title">Professional Details</h2>
            <div class="info-grid">
                <p><strong>Service Type:</strong> {{ userDetails.service }}</p>
                <p><strong>Description:</strong> {{ userDetails.prof_desc }}</p>
                <p><strong>Charges:</strong> {{ userDetails.price }} Rs.</p>
                <p><strong>Experience:</strong> {{ userDetails.no_of_years }} years</p>
                <p><strong>DOB:</strong> {{ userDetails.date_of_birth }}</p>
            </div>

            <div class="media-professional">
                <!-- Profile Image -->
                <div v-if="userDetails.image" class="profile-image">
                    <img :src="getDecodedImage(userDetails)" alt="Professional Image"/>
                </div>

                <!-- Resume PDF -->
                <div v-if="userDetails.pdf_file" class="pdf-button">
                    <button class="btn btn-primary" @click="openProfessional(userDetails.cid)">
                        <i class="fa-brands fa-readme"></i> View Resume
                    </button>
                </div>
            </div>
        </div>

        <div class="nav-buttons">
            <router-link :to="{ name: 'Activate'}" class="btn btn-primary">
                <i class="fa-solid fa-angles-left"></i> Back
            </router-link>
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
            } catch (error) {
                console.error('Error fetching details:', error);
            }
        },
        async openProfessional(professionalId) {
            try {
                const response = await fetch(`http://127.0.0.1:5000/get_pdf/${professionalId}`, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                    },
                });
                const blob = await response.blob();
                const pdfUrl = URL.createObjectURL(blob);
                window.open(pdfUrl, '_blank');
            } catch (error) {
                console.error('Error opening professional:', error);
            }
        },
        handleImageError(event) {
            console.error("Error loading image:", event);
        },
        getDecodedImage(professional) {
            return `data:image/${professional.imageType};base64,${professional.image}`;
        }
    },
    mounted() {
        this.viewDetails();
    }
}
</script>

<style scoped>
.custom-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 1rem;
}

.details-card {
    background-color: rgba(0, 0, 0, 0.315);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    color: black;
}

.card-title {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #000;
    font-size: 1.5rem;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}

.info-grid p {
    margin: 0;
    padding: 0.5rem;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 0.5rem;
}

.role-tag {
    text-align: center;
    margin-top: 1rem;
    padding: 0.5rem;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 0.5rem;
    font-size: 1.1rem;
}

.media-professional {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin-top: 1.5rem;
}

.profile-image {
    width: 200px;
    height: 200px;
    overflow: hidden;
    border-radius: 0.5rem;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.profile-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.pdf-button {
    margin-top: 0.5rem;
}

.nav-buttons {
    text-align: center;
    margin-top: 1rem;
}

.btn {
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
}

@media (max-width: 600px) {
    .info-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .profile-image {
        width: 150px;
        height: 150px;
    }
}
</style>