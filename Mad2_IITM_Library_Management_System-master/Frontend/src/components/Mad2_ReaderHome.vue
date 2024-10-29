<template>
    <div class="custom-container">
        <section class="single-container">
            <div class="wrapper" v-for="service in services" :key="service.id">
                <h2 class="my2">{{ service.name }}</h2>
                <h4 class="my3">Time required : {{ service.time }} hours</h4>
                <h4 class="my3">Base Price : {{ service.baseprice }} Rs.</h4>
                <div class="slider-professional"> <!-- :isRead="professional.isRead" -->
                    <professional-card v-for="professional in filteredProfessionals(service.id)"
                                  :key="professional.id"
                                  :professional="professional"
                                  :decodedImage="professional.decodedImage"
                                  :price="professional.price"
                                  :isRequested="professional.isRequested"
                                  @professional-updated="updatedProfessional">
                    </professional-card>
                    <!-- additional charge plus service.price has to be made -->
                </div>
            </div>
        </section>
    </div>
</template>

<script>
import ProfessionalCard from './Mad2_ProfessionalCard.vue';

export default {
    components: {
        ProfessionalCard,
    },
    data() {
        return {
            professionals: [],
            services: [],
            loadingServiceProfessional: false,
        };
    },
    mounted() {
        this.fetchProfessionals();
        this.fetchServices();
    },
    methods: {
        updatedProfessional() {
            this.fetchProfessionals();
        },
        filteredProfessionals(serviceId) {
            return this.professionals
                .filter(professional => professional.service === serviceId)
                .map(professional => ({
                    ...professional,
                    decodedImage: this.getDecodedImage(professional)
                }));
        },
        async fetchProfessionals() {
            const token = sessionStorage.getItem('token');
            const decodedToken = this.$jwtDecode(token);
            const userId = decodedToken.id;
            
            try {
                const response = await this.$axios.get(`http://127.0.0.1:5000/user/fetch-professional/${userId}`);
                this.professionals = response.data.professionals;
            } catch (error) {
                console.error('Error fetching user professionals:', error);
            }
        },
        async fetchServices() {
            this.loadingServiceProfessional = true;
            try {
                const response = await this.$axios.get('http://127.0.0.1:5000/fetch-services');
                this.services = response.data.services;
            } catch (error) {
                console.error('Error fetching services:', error);
            } finally {
                this.loadingServiceProfessional = false;
            }
        },
        getDecodedImage(professional) {
            return `data:image/${professional.imageType};base64, ${professional.image}`;
        },
        handleImageError(event) {
            console.error("Error loading image:", event);
        }
    },
};
</script>

<style scoped>
.custom-container {
    display: flex;
    flex-direction: column;
    row-gap: 2rem;
    align-items: center;
    padding-top: 2rem;
}

.single-container {
    background-color: rgba(0, 0, 0, 0.30);
    width: 85%;
    height: 100%;
    padding: 3rem;
    border-radius: 1rem;
    box-shadow: rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px;
}

.wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
    overflow: hidden;
}

.wrapper h2 {
    font-size: 30px;
    line-height: 44px;
    color: white;
    font-weight: 700;
    font-family: Arial, Helvetica, sans-serif;
    border-bottom: 2px solid lightgray;
}

.slider-professional {
    overflow-x: scroll;
    scroll-snap-type: x mandatory;
    display: flex;
    column-gap: 2rem;
    width: 100%;
    padding-bottom: 1rem;
}

.slider-professional::-webkit-scrollbar {
    display: none;
    width: 0;
}
</style>
