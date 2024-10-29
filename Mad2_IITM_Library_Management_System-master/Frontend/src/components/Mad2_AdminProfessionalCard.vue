<template>
    <div class="professional-card">
        <img :src="decodedImage" alt="Professional Image" @error="handleImageError" />
        <div class="professional-body">
            <div class="title-service">
                <!-- <p>Title</p> -->
                <h3>{{ professional.title }}</h3>
            </div>
            <div class="details-service">
                <p>About me: {{ professional.prof_desc }}</p>
                <p>Service Charge: {{ professional.price }} </p>
                <p>Rating: {{ !professional.rating || isNaN(professional.rating) ? 'N/A' : `${professional.rating.toFixed(2)} / 5` }}</p>
            </div>
            <div class="action-buttons">
                <!-- <button class="btn btn-primary btn-sm" @click="editProfessional(professional.id)">
                    <i class="fa-solid fa-pen"></i> Edit
                </button> -->
                <router-link class="btn btn-success btn-sm" :to="'/activity-data/' + professional.id">
                    <i class="fa-solid fa-chart-line"></i> View Activity
                </router-link>
                <!-- <button class="btn btn-danger btn-sm" @click="confirmDeletion(professional.id)">
                    <i class="fa-solid fa-trash"></i> Delete
                </button> -->
            </div>
            <div v-if="showAlert" :class="[alertType, 'alert-dismissible', 'fade', 'show']" role="alert">
                {{ alertMessage }}
                <button type="button" class="btn-close" @click="closeAlert" aria-label="Close"></button>
            </div>
        </div>

        <AlertTop v-if="showAlert" :message="alertMessage" :type="alertType" @close="closeAlert" />
    </div>
</template>

<script>
import AlertTop from './Mad2_AlertTop.vue';

export default {
    components: {
        AlertTop,
    },
    data() {
        return {
            showAlert: false,
            alertType: 'success',
            alertMessage: '',
        };
    },
    props: {
        professional: {
            type: Object,
            required: true,
        },
        decodedImage: {
            type: String,
            required: true,
        },
    },
    methods: {
        // confirmDeletion(professionalId) {
        //     if (confirm("Are you sure you want to delete this professional?")) {
        //         this.removeProfessional(professionalId);
        //     }
        // },
        getDecodedImage(professional) {
            return `data:image/${professional.imageType};base64,${professional.image}`;
        },
        handleImageError(event) {
            console.error("Image failed to load:", event);
        },
        navigateToActivity(professionalId) {
            this.$router.push(`/activity-data/${professionalId}`);
        },
        filterProfessionalsByService(serviceId) {
            return this.professionals
                .filter(professional => professional.service === serviceId)
                .map(professional => ({
                    ...professional,
                    decodedImage: this.getDecodedImage(professional),
                    rating: this.calculateAverageRating(professional.id),
                }));
        },
        editProfessional(professionalId) {
            this.$router.push({ name: 'UpdateProfessional', params: { professionalId } });
        },
        // removeProfessional(professionalId) {
        //     const token = sessionStorage.getItem('token');

        //     fetch(`http://127.0.0.1:5000/delete-professional/${professionalId}`, {
        //         method: 'DELETE',
        //         headers: {
        //             'Content-Type': 'application/json',
        //             'Authorization': `Bearer ${token}`,
        //         },
        //     })
        //         .then(response => {
        //             if (response.ok) {
        //                 this.showAlert = true;
        //                 this.alertType = 'success';
        //                 this.alertMessage = 'Professional successfully deleted.';
        //                 return response.json();
        //             } else {
        //                 throw new Error('Failed to delete professional');
        //             }
        //         })
        //         .then(data => {
        //             this.$emit('professionalUpdated');
        //             console.log(data.message);
        //         })
        //         .catch(error => {
        //             this.showAlert = true;
        //             this.alertType = 'error';
        //             this.alertMessage = 'Professional deletion failed.';
        //             console.error(error);
        //         });
        // },
        closeAlert() {
            this.showAlert = false;
        }
    }
};
</script>

<style scoped>
.professional-card {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    background-color: #f3eeee;
    border-radius: 0.5rem;
    border: 1px solid white;
    box-shadow: 0 50px 100px -20px rgba(50, 50, 93, 0.25), 0 30px 60px -30px rgba(0, 0, 0, 0.3), 0 -2px 6px 0 rgba(10, 37, 64, 0.35) inset;
    width: 210px;
    scroll-snap-align: start;
}

.professional-card img {
    height: 180px !important;
    border-radius: 0.5rem 0.5rem 0 0;
    width: auto;
}

.professional-body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.5rem;
    height: 100%;
}

.title-service {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    font-family: Arial, Helvetica, sans-serif;
}

.title-service p {
    font-size: 14px;
    line-height: 18px;
    color: #333;
    margin: 0;
}

.title-service h3 {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 20px;
    line-height: 30px;
    margin: 0;
    color: black;
    width: 200px;
}

.details-service {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
}

.details-service p {
    font-size: 14px;
    line-height: 18px;
    color: #333;
    margin: 0;
}

.action-buttons {
    display: flex;
    justify-professional: center;
    gap: 0.5rem;
    margin-top: auto;
}

.action-buttons button {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem;
    width: 100%;
}
</style>
